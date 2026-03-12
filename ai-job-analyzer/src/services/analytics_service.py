# Importăm Counter pentru a număra aparițiile skill-urilor.
from collections import Counter

# Importăm Session pentru query-uri DB.
from sqlalchemy.orm import Session

# Importăm modelul Job.
from src.db.models import Job

def get_skill_counts(db: Session):
    """
    Analizează toate joburile din baza de date și numără de câte ori
    apar anumite skill-uri în title și description.
    """

    # Lista de skill-uri pe care vrem să le urmărim.
    # Pentru început folosim o listă fixă, relevantă pentru rolurile tale.
    tracked_skills = [
        "python",
        "aws",
        "docker",
        "kubernetes",
        "sql",
        "nosql",
        "fastapi",
        "django",
        "flask",
        "git",
        "ci/cd",
        "lambda",
        "s3",
        "dynamodb",
        "ec2",
        "rag",
        "llm",
        "genai",
        "prompt engineering"
    ]

    # Luăm toate joburile din baza de date.
    jobs = db.query(Job).all()

    # Counter ne ajută să numărăm ușor aparițiile.
    skill_counts = Counter()

    # Parcurgem fiecare job.
    for job in jobs:
        # Luăm title și description.
        # Dacă vreunul este None, folosim string gol.
        title = (job.title or "").lower()
        description = (job.description or "").lower()

        # Combinăm cele două câmpuri într-un singur text.
        full_text = f"{title} {description}"

        # Verificăm pentru fiecare skill dacă apare în text.
        for skill in tracked_skills:
            if skill in full_text:
                skill_counts[skill] += 1

    # Convertim Counter în dicționar simplu și îl returnăm.
    return dict(skill_counts)