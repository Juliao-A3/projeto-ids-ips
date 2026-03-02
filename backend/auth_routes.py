from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from backend.dependencies import get_session
from backend.models import Usuario, engine
from backend.main import bcrypt_context
from backend.schemas import UsuarioSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])

Session = sessionmaker(bind=engine)

@auth_router.get('/')
async def login():
    return {'mensagem': 'Voce acessou a rota padrao de autenticacao'}

@auth_router.post('/criar-usuario')
async def criar_usuario(dados: UsuarioSchema, session = Depends(get_session)):
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