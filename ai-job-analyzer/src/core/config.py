# Importăm funcția create_engine din SQLAlchemy.
# Ea creează conexiunea către baza de date.
from sqlalchemy import create_engine

# Importăm sessionmaker pentru a crea sesiuni de lucru cu DB.
from sqlalchemy.orm import sessionmaker

# URL-ul bazei de date.
# Formatul este:
# dialect+driver://user:password@host:port/database
DATABASE_URL = "postgresql://jobs:jobs@localhost:5432/jobsdb"

# Engine-ul este obiectul care gestionează conexiunea la baza de date.
engine = create_engine(DATABASE_URL)

# SessionLocal creează sesiuni DB pentru fiecare request.
SessionLocal = sessionmaker(
    #modificările NU se salvează automat în DB
    autocommit=False, 
    #flush = trimite modificările din memorie către baza de date, dar fără commit.
    autoflush=False, 
    #connects the session to the database engine.
    bind=engine
    )