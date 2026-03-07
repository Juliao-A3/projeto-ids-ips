from backend.main import SECRET_KEY
from backend.auth_routes import criar_token

# Verificar a SECRET_KEY
print(f"SECRET_KEY na main: {SECRET_KEY}")
print(f"Tipo: {type(SECRET_KEY)}")

# Criar um token
token = criar_token(1)
print(f"Token criado: {token}")

# Decodificar
from jose import jwt
from backend.main import ALGORITHM

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Token verificado: {payload}")
except Exception as e:
    print(f"Erro ao verificar token: {e}")
