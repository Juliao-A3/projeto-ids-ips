from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.dependencies import get_session, verificar_token
from backend.models import Usuario, engine
from backend.main import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, bcrypt_context
from backend.schemas import LoginSchema, UsuarioSchema
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix='/auth', tags=['auth'])

def criar_token(id_usuario, duracao_token=None):
    if duracao_token is None:
        duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + duracao_token
    payload = {
        "sub": id_usuario,
        "exp": expire
    }
    token = jwt.encode(payload, "SECRET_KEY", ALGORITHM)
    return token


def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha_hash):
        return False
    return usuario

@auth_router.get('/')
async def login():
    return {'mensagem': 'Voce acessou a rota padrao de autenticacao'}

@auth_router.post('/criar-usuario')
async def criar_usuario(dados: UsuarioSchema, session: Session = Depends(get_session)):
    try:
        usuario_existente = session.query(Usuario).filter(Usuario.email == dados.email).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail='Esse usuario já existe')
        
        usuario = Usuario(
            email=dados.email,
            senha_hash=bcrypt_context.hash(dados.senha),
            role="admin",  # Definindo o role como "admin" por padrão
            nome=dados.nome,
            ativo=True
        )
        session.add(usuario)
        session.commit()
        return {'mensagem': 'Usuario criado com sucesso'}
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail='Erro ao criar usuario')
    
@auth_router.post('/login')
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=401, detail='Email ou senha inválidos')
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))  # Criando um token de refresh (pode ser o mesmo ou diferente do access token)
        return {
            'access_token': access_token, 
            'refresh_token': refresh_token, 
            'token_type': 'bearer'
            }

@auth_router.get('/refresh')
async def refresh_token(usuario: Usuario = Depends(verificar_token), session: Session = Depends(get_session)):
    if not usuario:
        raise HTTPException(status_code=401, detail='Token inválido')
    else:
        new_access_token = criar_token(usuario.id)
        return {
            'access_token': new_access_token, 
            'token_type': 'bearer'
            }