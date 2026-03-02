from backend.models import engine
from sqlalchemy.orm import sessionmaker

    
def get_session():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()