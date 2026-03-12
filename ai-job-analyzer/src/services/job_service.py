# Importăm Session pentru operații cu baza de date.
from sqlalchemy.orm import Session

# Importăm modelul ORM Job.
from src.db.models import Job

# Importăm clientul care vorbește cu Adzuna.
from src.clients.adzuna_client import fetch_adzuna_jobs

def create_job(db: Session, title: str, company: str, location: str):
    """
    Creează un job nou în baza de date.
    Aceasta este logica de business pentru crearea manuală a unui job.
    """

    # Construim obiectul ORM Job.
    new_job = Job(
        title=title,
        company=company,
        location=location
    )

    # Îl adăugăm în sesiunea DB.
    db.add(new_job)

    # Salvăm modificările permanent în baza de date.
    db.commit()

    # Reîncărcăm obiectul din DB pentru a obține valori generate automat,
    # de exemplu id-ul.
    db.refresh(new_job)

    # Returnăm obiectul nou creat.
    return new_job


def get_all_jobs(db: Session):
    """
    Returnează toate joburile din baza de date.
    """
    return db.query(Job).all()



def ingest_jobs_from_adzuna(db: Session, what: str, country: str):
    """
    Ia joburi din Adzuna și le salvează în baza de date.

    Logica acestui serviciu este:
    1. cere joburi de la API-ul extern
    2. verifică duplicatele după external_id
    3. adaugă doar joburile noi
    4. face un singur commit la final
    """

    # Cerem joburile din API-ul extern.
    jobs_from_api = fetch_adzuna_jobs(what=what, country=country)

    # Vom contoriza câte am inserat și câte am sărit.
    inserted = 0
    skipped = 0

    # Parcurgem joburile primite de la Adzuna.
    for item in jobs_from_api:
        # Luăm external_id și îl transformăm în string.
        external_id = str(item.get("id"))

        # Verificăm dacă avem deja acest job în baza noastră de date.
        existing_job = db.query(Job).filter(Job.external_id == external_id).first()

        # Dacă există, îl sărim pentru a evita duplicatele.
        if existing_job:
            skipped += 1
            continue

        # Construim obiectul ORM pentru jobul nou.
        new_job = Job(
            external_id=external_id,
            source="adzuna",
            title=item.get("title"),
            company=(item.get("company") or {}).get("display_name"),
            location=(item.get("location") or {}).get("display_name"),
            description=item.get("description"),
        )

        # Îl adăugăm în sesiunea DB.
        db.add(new_job)
        inserted += 1

    # Facem un singur commit la final,
    # ceea ce este mai eficient decât commit după fiecare job.
    db.commit()

    # Returnăm un mic rezumat al operației.
    return {
        "inserted": inserted,
        "skipped": skipped
    }