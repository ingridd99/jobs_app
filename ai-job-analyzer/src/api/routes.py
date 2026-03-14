from fastapi import APIRouter

# Import services — same as before, but they now use DynamoDB internally.
from src.services.job_service import create_job, get_jobs, ingest_jobs_from_adzuna
from src.services.analytics_service import get_skill_counts
from src.schemas.job import JobCreate

# Creăm routerul principal.
# Aici definim toate endpointurile aplicației.
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/jobs")
def add_job(job: JobCreate):
    item = create_job(job)
    return {"message": "Job created", "job": item}

@router.get("/jobs")
def list_jobs(limit: int = 20):
    jobs = get_jobs(limit=limit)
    return {"count": len(jobs), "jobs": jobs}

@router.post("/ingest/jobs")
def ingest_jobs(what: str = "python developer", country: str = "gb"):
    result = ingest_jobs_from_adzuna(what=what, country=country)
    return result

@router.get("/analytics/skills")
def analytics_skills():
    counts = get_skill_counts()
    return {"skills": counts}