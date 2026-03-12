# Importăm tipuri de coloane SQL.
from sqlalchemy import Column, Integer, String

# Importăm declarative_base pentru a defini modele ORM.
from sqlalchemy.orm import declarative_base

# Base este clasa de bază pentru toate modelele noastre.
Base = declarative_base()

# Definim modelul Job.
# Acesta va deveni o tabelă în baza de date.
class Job(Base):

    # Numele tabelului în PostgreSQL
    __tablename__ = "jobs"

    # Cheia primară a tabelului
    id = Column(Integer, primary_key=True, index=True)

    # ID-ul jobului din sursa externă, ex. Adzuna
    external_id = Column(String, unique=True, index=True)

    # Sursa din care a venit jobul
    source = Column(String)

    # Titlul jobului
    title = Column(String)
    # Compania
    company = Column(String)
    # Locația jobului
    location = Column(String)

    # Păstrăm și descrierea, pentru viitorul RAG / LLM
    description = Column(String)