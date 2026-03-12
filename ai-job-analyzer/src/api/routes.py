# Importăm APIRouter pentru a grupa endpointurile.
from fastapi import APIRouter, Depends, HTTPException

# Importăm Session pentru tiparea sesiunii DB.
from sqlalchemy.orm import Session

# Importăm fabrica de sesiuni DB.
from src.core.config import SessionLocal

# Importăm schema pentru request body.
from src.schemas.job import JobCreate

# Importăm serviciile care conțin logica de business.
from src.services.job_service import create_job, get_all_jobs, ingest_jobs_from_adzuna
from src.services.analytics_service import get_skill_counts

# Creăm routerul principal.
# Aici definim toate endpointurile aplicației.
router = APIRouter()


def get_db():
    """
    Creează o sesiune DB pentru fiecare request și o închide la final.

    FastAPI va folosi această funcție ca dependency.
    De fiecare dată când un endpoint cere db: Session = Depends(get_db),
    se va crea o sesiune nouă.
    """
    db = SessionLocal()
    try:
        # yield dă mai departe sesiunea endpointului.
        yield db
    finally:
        # La finalul requestului, sesiunea este închisă.
        db.close()


def format_job(job):
    """
    Transformă un obiect ORM Job într-un dicționar simplu,
    ușor de serializat ca JSON.
    """
    return {
        "id": job.id,
        "external_id": job.external_id,
        "source": job.source,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description
    }

@router.get("/health")
def health():
    """
    Endpoint simplu pentru a verifica dacă aplicația rulează.
    """
    return {"status": "ok"}


@router.post("/jobs")
def create_job_endpoint(job: JobCreate, db: Session = Depends(get_db)):
    """
    Creează manual un job nou.

    FastAPI:
    - citește JSON-ul din request body
    - îl validează folosind JobCreate
    - injectează sesiunea DB prin Depends(get_db)
    """

    # Apelăm service-ul care se ocupă de logica de creare.
    created_job = create_job(
        db=db,
        title=job.title,
        company=job.company,
        location=job.location
    )

    # Returnăm un răspuns JSON.
    return {
        "message": "Job created successfully",
        "job": format_job(created_job)
    }


@router.get("/jobs")
def get_jobs_endpoint(db: Session = Depends(get_db)):
    """
    Returnează toate joburile din baza de date.
    """
    jobs = get_all_jobs(db)

    # Convertim fiecare obiect ORM într-un dicționar simplu.
    return {"jobs": [format_job(job) for job in jobs]}

@router.post("/ingest/jobs")
def ingest_jobs_endpoint(
    what: str = "python developer",
    country: str = "gb",
    db: Session = Depends(get_db)
):
    """
    Endpoint care aduce joburi din Adzuna și le salvează în DB.

    Parametri query:
    - what: ce căutăm
    - country: în ce țară căutăm
    """
    try:
        # Apelăm service-ul care face integrarea completă.
        result = ingest_jobs_from_adzuna(db, what, country)

    except Exception as exc:
        # Dacă apare orice eroare, o transformăm într-un HTTP 500.
        raise HTTPException(status_code=500, detail=f"Adzuna error: {str(exc)}")

    # Returnăm un rezumat al ingestion-ului.
    return {
        "message": "Ingestion completed",
        "inserted": result["inserted"],
        "skipped": result["skipped"]
    }


@router.get("/analytics/skills")
def get_skills_analytics_endpoint(db: Session = Depends(get_db)):
    """
    Endpoint care întoarce frecvența skill-urilor detectate în joburi.
    """
    return {
        "skills": get_skill_counts(db)
    }