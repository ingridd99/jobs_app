#importing the class FastAPI from the library fastapi
#to create the web app
from fastapi import FastAPI
from sqlalchemy.orm import Session

from src.config import engine, SessionLocal
from src.models import Base, Job

#creating the app instance
#the variable is named "app" for the command "uvicorn src.main:app --reload"
# where:
#   src = current folder
#   main = the file main.py
#   app = the FastAPI object
app = FastAPI()

# Această linie creează toate tabelele definite în modele.
# Dacă tabela există deja, nu face nimic.
Base.metadata.create_all(bind=engine)

# Funcție ajutătoare pentru a deschide o sesiune DB
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

#the decorator @app.get("/health") -> when a GET request comes on route "/health", the health() function is executed
@app.get("/health")
def health():
    #return a python dictionary
    #FastAPI automatically transforms it into a JSON
    return {"status": "ok"}

@app.post("/jobs")
def create_job():
    # Deschidem o sesiune către baza de date
    db: Session = SessionLocal()

    # Creăm un job de test
    new_job = Job(
        title="Python Developer",
        company="Example Company",
        location="Iasi"
    )

    # Îl adăugăm în sesiune
    db.add(new_job)

    # Salvăm în baza de date
    db.commit()

    # Reîncărcăm obiectul ca să primim id-ul generat de DB
    db.refresh(new_job)

    # Închidem sesiunea
    db.close()

    return {
        "message": "Job created successfully",
        "job": {
            "id": new_job.id,
            "title": new_job.title,
            "company": new_job.company,
            "location": new_job.location
        }
    }


@app.get("/jobs")
def get_jobs():
    # Deschidem sesiunea DB
    db: Session = SessionLocal()

    # Luăm toate joburile din tabel
    jobs = db.query(Job).all()

    # Transformăm obiectele ORM în dict-uri simple
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location
        })

    # Închidem sesiunea
    db.close()

    return {"jobs": result}