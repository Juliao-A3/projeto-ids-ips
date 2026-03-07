from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.config import ALGORITHM, oauth2_schema, SECRET_KEY
from backend.models import Usuario, engine, UserRole
from sqlalchemy.orm import sessionmaker
from functools import wraps
from typing import List
from fastapi import Query
    
def get_session():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = payload.get("sub")
        if id_usuario is None:
            raise HTTPException(status_code=401, detail='Token inválido')
        id_usuario = int(id_usuario)
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if usuario is None:
            raise HTTPException(status_code=401, detail='Token inválido')
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail='Token inválido')

def verificar_token_ws(token: str, session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = int(payload.get("sub"))
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            raise HTTPException(status_code=401)
        return usuario
    except JWTError:
        raise HTTPException(status_code=401)        

def require_role(allowed_roles: List[str]):
    def check_role(usuario: Usuario = Depends(verificar_token)):
        print(f"=== require_role ===")
        print(f"role do usuario: '{usuario.role.value}'")
        print(f"tipo: {type(usuario.role.value)}")
        print(f"allowed_roles: {allowed_roles}")
        print(f"está incluído: {usuario.role.value in allowed_roles}")
        
        if usuario.role.value not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail='Acesso denegado - permissão insuficiente'
            )
        return usuario
    return check_role

def verificar_token_query(
    token: str = Query(None),
    session: Session = Depends(get_session)
):
    if not token:
        raise HTTPException(status_code=401, detail='Token inválido')
    return verificar_token_ws(token, session)