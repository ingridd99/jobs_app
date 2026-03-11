##########
#This file describes how the in and out data looks like for this API
##########


# Importăm BaseModel din Pydantic.
# Pydantic este folosit de FastAPI pentru validarea datelor primite în request.
from pydantic import BaseModel
from typing import Optional


# Această clasă descrie forma datelor pe care le așteptăm
# când cineva vrea să creeze manual un job nou prin POST /jobs.
class JobCreate(BaseModel):
    title: str
    company: str
    location: str

# Această schemă descrie cum arată un job returnat de API.
class JobResponse(BaseModel):
    # ID-ul intern din baza noastră de date
    id: int

    # ID-ul extern din sursa de joburi.
    # Optional[str] înseamnă că poate fi string sau None.
    external_id: Optional[str] = None

    # Numele sursei, ex. "adzuna"
    source: Optional[str] = None

    # Câmpurile principale
    title: str
    company: str
    location: str

    # Descrierea poate lipsi
    description: Optional[str] = None