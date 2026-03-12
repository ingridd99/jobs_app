# Importăm FastAPI pentru a crea aplicația principală.
from fastapi import FastAPI

# Importăm load_dotenv pentru a încărca variabilele de mediu din fișierul .env.
from dotenv import load_dotenv

# Încărcăm variabilele de mediu cât mai devreme,
# înainte să folosim module care citesc os.getenv().
load_dotenv()

# Importăm engine-ul DB și clasa Base a modelelor ORM.
from src.core.config import engine
from src.db.models import Base

# Importăm routerul care conține endpointurile API.
from src.api.routes import router


# Creăm aplicația FastAPI.
# Acesta este obiectul principal al aplicației.
app = FastAPI()


# Creăm în baza de date toate tabelele definite în modele,
# dacă ele nu există deja.
# IMPORTANT:
# create_all() creează tabelele lipsă, dar NU modifică tabele existente.
Base.metadata.create_all(bind=engine)


# Înregistrăm routerul în aplicația principală.
# Asta face ca endpointurile din api/routes.py să devină active.
app.include_router(router)