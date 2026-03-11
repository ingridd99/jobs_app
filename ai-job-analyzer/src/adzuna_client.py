# Importăm os pentru a citi variabilele de mediu din .env.
import os

# Importăm requests pentru a face apeluri HTTP către API-ul Adzuna.
import requests


def fetch_adzuna_jobs(
    what: str = "python developer",
    country: str = "gb",
    page: int = 1,
    results_per_page: int = 5
):
    """
    Face un request către API-ul Adzuna și întoarce lista de joburi.

    Parametri:
    - what: cuvinte-cheie pentru căutare
    - country: țara în care căutăm
    - page: pagina de rezultate
    - results_per_page: câte rezultate vrem să cerem
    """

    # Citim valorile din variabilele de mediu.
    # Acestea trebuie să existe în fișierul .env și să fi fost încărcate prin load_dotenv().
    adzuna_app_id = os.getenv("ADZUNA_APP_ID")
    adzuna_app_key = os.getenv("ADZUNA_APP_KEY")

    # Verificăm explicit că valorile există.
    # Dacă lipsesc, ridicăm o eroare clară.
    if not adzuna_app_id or not adzuna_app_key:
        raise ValueError(
            "Missing ADZUNA_APP_ID or ADZUNA_APP_KEY. Check your .env file."
        )

    # Construim URL-ul endpointului Adzuna.
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

    # Construim query parameters pentru request.
    params = {
        # Credentialele Adzuna
        "app_id": adzuna_app_id,
        "app_key": adzuna_app_key,

        # Parametrii de căutare
        "what": what,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    # Trimitem requestul HTTP GET către Adzuna.
    response = requests.get(url, params=params, timeout=30)

    # Dacă răspunsul este eroare (4xx / 5xx), requests va arunca excepție.
    response.raise_for_status()

    # Transformăm răspunsul JSON într-un dicționar Python.
    data = response.json()

    # Returnăm lista de joburi din cheia "results".
    # Dacă nu există, întoarcem listă goală.
    return data.get("results", [])