from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.main import ALGORITHM
from backend.models import Usuario, engine
from sqlalchemy.orm import sessionmaker
    
def get_session():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token, session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=[ALGORITHM])
        id_usuario = payload.get("sub") 
        if id_usuario is None:
            raise HTTPException(status_code=401, detail='Token inválido')
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if usuario is None:
            raise HTTPException(status_code=401, detail='Token inválido')
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail='Token inválido')
    