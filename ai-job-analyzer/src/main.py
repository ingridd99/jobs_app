#importing the class FastAPI from the library fastapi
#to create the web app
# și Depends pentru dependency injection.
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
# Încărcăm variabilele de mediu din fișierul .env.
# Asta trebuie făcut înainte să folosim valorile din os.getenv().
load_dotenv()
from src.config import engine, SessionLocal
from src.models import Base, Job

# Importăm schema Pydantic folosită pentru validarea request body-ului
from src.schemas import JobCreate

# Importăm funcția care face request la Adzuna.
from src.adzuna_client import fetch_adzuna_jobs

# Încărcăm variabilele de mediu din fișierul .env.
# Asta trebuie făcut înainte să folosim valorile din os.getenv().
load_dotenv()

#creating the app instance
#the variable is named "app" for the command "uvicorn src.main:app --reload"
# where:
#   src = current folder
#   main = the file main.py
#   app = the FastAPI object
app = FastAPI()

#creating all the tabels defined in the models
#if the tabels already exists, does nothing
#creaza toate tabelele modelelor care mostenesc clasa Base
Base.metadata.create_all(bind=engine)

# Helper function to start a db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#the decorator @app.get("/health") -> when a GET request comes on route "/health", the health() function is executed
@app.get("/health")
def health():
    #return a python dictionary
    #FastAPI automatically transforms it into a JSON
    return {"status": "ok"}

@app.post("/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    # Creăm un job de test
    new_job = Job(
        title=job.title,
        company=job.company,
        location=job.location
    )

    # Îl adăugăm în sesiune
    db.add(new_job)

    # Salvăm în baza de date
    db.commit()

    # Reîncărcăm obiectul ca să primim id-ul generat de DB
    db.refresh(new_job)

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
def get_jobs(db: Session = Depends(get_db)):
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


@app.post("/ingest/jobs")
def ingest_jobs(
    what: str = "python developer",
    country: str = "gb",
    db: Session = Depends(get_db)
):
    """
    Ia joburi din Adzuna și le salvează în baza de date.

    Parametri:
    - what: ce tip de joburi vrem să căutăm
    - country: țara în care căutăm joburi
    """

    # Încercăm să luăm joburi din API-ul Adzuna
    try:
        jobs_from_api = fetch_adzuna_jobs(what=what, country=country)

    # Dacă apare o eroare la apelul extern, returnăm HTTP 500
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Adzuna error: {str(exc)}")

    # Contorizăm câte joburi am inserat și câte am sărit
    inserted = 0
    skipped = 0

     # Parcurgem joburile primite din API
    for item in jobs_from_api:
        # Luăm ID-ul extern și îl transformăm în string
        external_id = str(item.get("id"))

        # Verificăm dacă jobul există deja în DB.
        # Așa evităm duplicatele.
        existing_job = db.query(Job).filter(Job.external_id == external_id).first()

        if existing_job:
            skipped += 1
            continue

        # Construim un nou obiect Job din datele API-ului
        new_job = Job(
            external_id=external_id,
            source="adzuna",
            title=item.get("title"),
            company=(item.get("company") or {}).get("display_name"),
            location=(item.get("location") or {}).get("display_name"),
            description=item.get("description"),
        )

        # Îl adăugăm în sesiunea DB
        db.add(new_job)
        inserted += 1

    # Facem un singur commit la final pentru toate joburile noi
    db.commit()

    # Returnăm un rezumat al operației
    return {
        "message": "Ingestion completed",
        "inserted": inserted,
        "skipped": skipped
    }