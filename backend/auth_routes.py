from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.dependencies import get_session, verificar_token, require_role
from backend.models import Usuario, engine
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, bcrypt_context, SECRET_KEY
from backend.schemas import LoginSchema, UsuarioSchema
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from backend.schemas import RefreshTokenSchema
from pydantic import BaseModel, EmailStr
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

auth_router = APIRouter(prefix='/auth', tags=['auth'])

_reset_codes: dict[str, dict] = {}

CODE_EXPIRE_MINUTES = 10    # código válido 10 minutos
MAX_TENTATIVAS      = 5     # tentativas erradas antes de invalidar


def _gerar_codigo() -> str:
    """Gera um código numérico de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=6))

"""
    Envia o código de recuperação usando credenciais SMTP do .env —
    separado do email de alertas da empresa (NotificationConfig).
"""
def _enviar_codigo_email(email: str, codigo: str):  # ← sem session
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")

    print(f"[DEBUG] smtp_host: '{smtp_host}'")
    print(f"[DEBUG] smtp_user: '{smtp_user}'")
    print(f"[DEBUG] smtp_pass: '{smtp_pass[:4]}...' (len={len(smtp_pass)})")

    if not smtp_user or not smtp_pass:
        print(f"[AEGIS] ⚠ SMTP_USER/SMTP_PASS não configurados no .env")
        print(f"[AEGIS] ⚠ Código de recuperação para {email}: {codigo}")
        return

    corpo_html = f"""
    <div style="font-family:monospace;background:#0B0E14;color:#fff;padding:32px;
                max-width:480px;margin:0 auto;border-radius:8px;
                border:1px solid #1E2530;">
      <div style="text-align:center;margin-bottom:24px;">
        <span style="font-size:22px;font-weight:900;letter-spacing:.4em;color:#fff;">AEGIS</span>
        <div style="font-size:10px;letter-spacing:.2em;color:#00A3FF;margin-top:4px;">
          RECUPERAÇÃO DE SENHA
        </div>
      </div>
      <p style="color:#94A3B8;font-size:13px;line-height:1.8;">
        Recebemos um pedido de recuperação de senha para a tua conta.<br>
        Usa o código abaixo para redefinir a tua senha:
      </p>
      <div style="background:#151921;border:1px solid #1E2530;border-radius:6px;
                  padding:28px;text-align:center;margin:24px 0;">
        <div style="font-size:38px;font-weight:700;letter-spacing:.6em;
                    color:#00A3FF;padding-right:.6em;">{codigo}</div>
        <div style="font-size:11px;color:#64748B;margin-top:10px;">
          Válido por {CODE_EXPIRE_MINUTES} minutos
        </div>
      </div>
      <p style="color:#64748B;font-size:11px;line-height:1.8;">
        Se não foste tu a pedir esta recuperação, ignora este email.<br>
        A tua senha permanece inalterada.
      </p>
      <div style="border-top:1px solid #1E2530;margin-top:24px;padding-top:16px;
                  text-align:center;font-size:9px;color:#475569;">
        © 2025 AEGIS SECURITY · Sistema IDS/IPS
      </div>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "AEGIS — Código de Recuperação de Senha"
        msg["From"]    = smtp_user
        msg["To"]      = email
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, email, msg.as_string())

        print(f"[AEGIS] ✓ Email de recuperação enviado para {email}")

    except Exception as e:
        print(f"[AEGIS] ✗ Erro ao enviar email de recuperação: {e}")


# ─── Schemas para recuperação de senha 
class ForgotPasswordSchema(BaseModel):
    email: str

class VerifyCodeSchema(BaseModel):
    email: str
    codigo: str

class ResetPasswordSchema(BaseModel):
    email: str
    codigo: str
    nova_senha: str

class AlterarSenhaSchema(BaseModel):
    senha_atual: str
    nova_senha: str

# Rotas existentes (inalteradas)

def criar_token(id_usuario, duracao_token=None):
    if duracao_token is None:
        duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + duracao_token
    payload = {"sub": str(id_usuario), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    if not bcrypt_context.verify(senha, usuario.senha_hash):
        return False
    return usuario


@auth_router.get('/')
async def auth_index():
    return {'mensagem': 'Rota de autenticação'}


@auth_router.post('/criar-usuario')
async def criar_usuario(
    dados: UsuarioSchema,
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    try:
        if session.query(Usuario).filter(Usuario.email == dados.email).first():
            raise HTTPException(status_code=400, detail='Esse usuario já existe')
        from backend.models import UserRole
        if dados.role not in [role.value for role in UserRole]:
            raise HTTPException(status_code=400, detail='Role inválido')
        usuario = Usuario(
            email=dados.email, senha_hash=bcrypt_context.hash(dados.senha),
            role=dados.role, nome=dados.nome, ativo=dados.ativo
        )
        session.add(usuario); session.commit()
        return {'mensagem': 'Usuario criado com sucesso'}
    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(status_code=500, detail='Erro ao criar usuario')


@auth_router.post('/register')
async def register(dados: UsuarioSchema, session: Session = Depends(get_session)):
    try:
        if session.query(Usuario).filter(Usuario.email == dados.email).first():
            raise HTTPException(status_code=400, detail='Esse usuario já existe')
        usuario = Usuario(
            email=dados.email, senha_hash=bcrypt_context.hash(dados.senha),
            role="admin", nome=dados.nome, ativo=True
        )
        session.add(usuario); session.commit()
        access_token  = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(minutes=25))
        return {
            'access_token': access_token, 'refresh_token': refresh_token,
            'token_type': 'Bearer', 'user': {'name': usuario.nome, 'role': usuario.role.value}
        }
    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(status_code=500, detail='Erro ao criar usuario')


@auth_router.post('/login')
async def login(dados: LoginSchema, session: Session = Depends(get_session)):
    usuario = autenticar_usuario(dados.email, dados.senha, session)
    if not usuario:
        raise HTTPException(status_code=401, detail='Email ou senha inválidos')
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail='Conta desativada. Contacta o administrador.')
    access_token  = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
    return {
        'access_token': access_token, 'refresh_token': refresh_token,
        'token_type': 'Bearer', 'user': {'name': usuario.nome, 'role': usuario.role.value}
    }


@auth_router.get('/users')
async def listar_usuarios(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    usuarios = session.query(Usuario).all()
    return [{'id':u.id,'nome':u.nome,'email':u.email,'role':u.role.value,'ativo':u.ativo,'criado_em':u.criado_em} for u in usuarios]


@auth_router.put('/users/{user_id}')
async def editar_usuario(
    user_id: int, dados: dict,
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    user = session.query(Usuario).filter(Usuario.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail='Utilizador não encontrado')
    if user.id == usuario.id: raise HTTPException(status_code=400, detail='Não podes editar o teu próprio role')
    if 'role'  in dados: user.role  = dados['role']
    if 'ativo' in dados: user.ativo = dados['ativo']
    session.commit()
    return {"message": "Utilizador atualizado com sucesso"}


@auth_router.delete('/users/{user_id}')
async def apagar_usuario(
    user_id: int,
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    user = session.query(Usuario).filter(Usuario.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail='Utilizador não encontrado')
    if user.id == usuario.id: raise HTTPException(status_code=400, detail='Não podes apagar a tua própria conta')
    session.delete(user); session.commit()
    return {"message": f"Utilizador {user.nome} apagado com sucesso"}


@auth_router.post('/refresh')
async def refresh_token(dados: RefreshTokenSchema, session: Session = Depends(get_session)):
    try:
        payload    = jwt.decode(dados.refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = int(payload.get("sub"))
        usuario    = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario: raise HTTPException(status_code=401, detail="Token inválido")
        return {"access_token": criar_token(usuario.id), "token_type": "Bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")


@auth_router.post('/token')
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    usuario = autenticar_usuario(form_data.username, form_data.password, session)
    if not usuario: raise HTTPException(status_code=401, detail='Email ou senha inválidos')
    return {"access_token": criar_token(usuario.id), "token_type": "bearer"}


@auth_router.get('/me')
async def get_perfil(usuario: Usuario = Depends(verificar_token), session: Session = Depends(get_session)):
    return {
        "id": usuario.id, "nome": usuario.nome, "email": usuario.email,
        "role": usuario.role.value, "ativo": usuario.ativo,
        "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
    }

@auth_router.put('/me')
async def editar_perfil(
    dados: dict,
    usuario: Usuario = Depends(verificar_token),
    session: Session = Depends(get_session)
):
    if 'nome'  in dados and dados['nome'].strip():  usuario.nome  = dados['nome'].strip()
    if 'email' in dados and dados['email'].strip():
        existente = session.query(Usuario).filter(Usuario.email==dados['email'], Usuario.id!=usuario.id).first()
        if existente: raise HTTPException(status_code=400, detail='Email já está em uso')
        usuario.email = dados['email'].strip()
    session.commit()
    return {"id":usuario.id,"nome":usuario.nome,"email":usuario.email,"role":usuario.role.value,
            "criado_em":usuario.criado_em.isoformat() if usuario.criado_em else None}

# NOVAS ROTAS — Recuperação de Senha

@auth_router.post('/forgot-password')
async def forgot_password(
    dados: ForgotPasswordSchema,
    session: Session = Depends(get_session)
):
    usuario = session.query(Usuario).filter(Usuario.email == dados.email).first()

    if usuario and usuario.ativo:
        codigo = _gerar_codigo()
        _reset_codes[dados.email] = {
            "codigo":     codigo,
            "expira":     datetime.now(timezone.utc) + timedelta(minutes=CODE_EXPIRE_MINUTES),
            "tentativas": 0,
        }
        _enviar_codigo_email(dados.email, codigo)  # ← sem session

    return {
        "message": "Se o email existir na nossa base de dados, irás receber um código de verificação."
    }


@auth_router.post('/verify-reset-code')
async def verify_reset_code(dados: VerifyCodeSchema):
    entry = _reset_codes.get(dados.email)

    if not entry:
        raise HTTPException(status_code=400, detail="Nenhum código de recuperação ativo para este email.")

    # expirou?
    if datetime.now(timezone.utc) > entry["expira"]:
        _reset_codes.pop(dados.email, None)
        raise HTTPException(status_code=400, detail="Código expirado. Solicita um novo código.")

    # demasiadas tentativas?
    if entry["tentativas"] >= MAX_TENTATIVAS:
        _reset_codes.pop(dados.email, None)
        raise HTTPException(status_code=400, detail="Demasiadas tentativas. Solicita um novo código.")

    # código errado?
    if entry["codigo"] != dados.codigo:
        entry["tentativas"] += 1
        restantes = MAX_TENTATIVAS - entry["tentativas"]
        raise HTTPException(
            status_code=400,
            detail=f"Código inválido. {restantes} tentativa(s) restante(s)."
        )

    return {"message": "Código verificado com sucesso.", "valido": True}


@auth_router.post('/reset-password')
async def reset_password(
    dados: ResetPasswordSchema,
    session: Session = Depends(get_session)
):
    """
    Passo 3 — Valida o código novamente e redefine a senha.
    """
    entry = _reset_codes.get(dados.email)

    if not entry:
        raise HTTPException(status_code=400, detail="Sessão de recuperação inválida ou expirada.")

    if datetime.now(timezone.utc) > entry["expira"]:
        _reset_codes.pop(dados.email, None)
        raise HTTPException(status_code=400, detail="Código expirado. Solicita um novo código.")

    if entry["codigo"] != dados.codigo:
        raise HTTPException(status_code=400, detail="Código inválido. Começa o processo novamente.")

    # validação da senha
    if len(dados.nova_senha) < 8:
        raise HTTPException(status_code=422, detail="A senha deve ter no mínimo 8 caracteres.")

    usuario = session.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada. Contacta o administrador.")

    # atualiza senha
    usuario.senha_hash = bcrypt_context.hash(dados.nova_senha)
    session.commit()

    # invalida o código usado
    _reset_codes.pop(dados.email, None)

    return {"message": "Senha redefinida com sucesso!"}

@auth_router.post('/alterar-senha')
async def alterar_senha(
    dados: AlterarSenhaSchema,
    usuario: Usuario = Depends(verificar_token),
    session: Session = Depends(get_session)
):
    if not bcrypt_context.verify(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")

    if len(dados.nova_senha) < 8:
        raise HTTPException(status_code=422, detail="A nova senha deve ter no mínimo 8 caracteres.")

    if dados.senha_atual == dados.nova_senha:
        raise HTTPException(status_code=400, detail="A nova senha não pode ser igual à senha atual.")

    usuario.senha_hash = bcrypt_context.hash(dados.nova_senha)
    session.commit()

    return {"message": "Senha alterada com sucesso!"}