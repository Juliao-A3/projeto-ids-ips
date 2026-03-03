from dotenv import load_dotenv
from fastapi import FastAPI  
import os
from passlib.context import CryptContext 

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
from backend.auth_routes import auth_router

app.include_router(auth_router)

#para executar o nosso codigo, executar no terminal: python -m uvicorn main:app --reload
