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

auth_router = APIRouter(prefix='/auth', tags=['auth'])

def criar_token(id_usuario, duracao_token=None):
    if duracao_token is None:
        duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + duracao_token
    payload = {
        "sub": str(id_usuario),
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token
 

def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha_hash):
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
        usuario_existente = session.query(Usuario).filter(Usuario.email == dados.email).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail='Esse usuario já existe')
        
        # Validar role
        from backend.models import UserRole
        if dados.role not in [role.value for role in UserRole]:
            raise HTTPException(status_code=400, detail='Role inválido')
        
        usuario = Usuario(
            email=dados.email,
            senha_hash=bcrypt_context.hash(dados.senha),
            role=dados.role,
            nome=dados.nome,
            ativo=dados.ativo
        )
        session.add(usuario)
        session.commit()
        return {'mensagem': 'Usuario criado com sucesso'}
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail='Erro ao criar usuario')

@auth_router.post('/register')
async def register(dados: UsuarioSchema, session: Session = Depends(get_session)):
    try:
        usuario_existente = session.query(Usuario).filter(Usuario.email == dados.email).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail='Esse usuario já existe')
        
        usuario = Usuario(
            email=dados.email,
            senha_hash=bcrypt_context.hash(dados.senha),
            role="admin",
            nome=dados.nome,
            ativo=True
        )
        session.add(usuario)
        session.commit()
        
        # Gera tokens
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(minutes=25))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'user': {
                'name': usuario.nome,
                'role': usuario.role.value
            }
        }
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail='Erro ao criar usuario')
    
    
@auth_router.post('/login')
async def login(dados: LoginSchema, session: Session = Depends(get_session)):
    usuario = autenticar_usuario(dados.email, dados.senha, session)
    if not usuario:
        raise HTTPException(status_code=401, detail='Email ou senha inválidos')
    
    access_token = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, duracao_token=timedelta(minutes=25))
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'user': {
            'name': usuario.nome,
            'role': usuario.role.value
        }
    }

@auth_router.get('/users')
async def listar_usuarios(
    usuario: Usuario = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
):
    usuarios = session.query(Usuario).all()
    return [
        {
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'role': u.role.value,
            'ativo': u.ativo,
            'criado_em': u.criado_em
        } for u in usuarios
    ]

@auth_router.post('/refresh')
async def refresh_token(dados: RefreshTokenSchema, session: Session = Depends(get_session)):
    try:
        # valida o refresh token
        payload = jwt.decode(dados.refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = int(payload.get("sub"))
        
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # gera novo access token
        novo_token = criar_token(usuario.id)
        
        return {
            "access_token": novo_token,
            "token_type": "Bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")    

@auth_router.post('/token')
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    usuario = autenticar_usuario(form_data.username, form_data.password, session)
    if not usuario:
        raise HTTPException(status_code=401, detail='Email ou senha inválidos')
    
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }        