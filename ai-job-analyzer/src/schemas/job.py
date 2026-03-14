##########
#This file describes how the in and out data looks like for this API
##########


# Importăm BaseModel din Pydantic.
# Pydantic este folosit de FastAPI pentru validarea datelor primite în request.
from pydantic import BaseModel
# În Python 3.9 folosim Optional pentru câmpurile care pot lipsi / pot fi None.
from typing import Optional


class JobCreate(BaseModel):
    # These two fields are needed for DynamoDB primary key
    external_id: str
    source: str

    # Job details
    title: str
    company: Optional[str] = ""
    location: Optional[str] = ""
    description: Optional[str] = ""

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