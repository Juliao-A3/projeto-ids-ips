from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.main import ALGORITHM, oauth2_schema, SECRET_KEY
from backend.models import Usuario, engine, UserRole
from sqlalchemy.orm import sessionmaker
from functools import wraps
from typing import List
    
def get_session():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload.get("sub") 
        if id_usuario is None:
            raise HTTPException(status_code=401, detail='Token inválido')
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if usuario is None:
            raise HTTPException(status_code=401, detail='Token inválido')
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail='Token inválido')

def require_role(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, usuario: Usuario = Depends(verificar_token), **kwargs):
            if usuario.role.value not in allowed_roles:
                raise HTTPException(status_code=403, detail='Acesso denegado - permissão insuficiente')
            return await func(*args, usuario=usuario, **kwargs)
        return wrapper
    return decorator
