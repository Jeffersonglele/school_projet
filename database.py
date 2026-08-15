import os
import pyodbc
from fastapi import HTTPException


# Lit le serveur et la base depuis le .env — avec valeur par defaut si absent
SERVER = os.getenv("DB_SERVER", r"GUILLAUME-AHIVO\SQLEXPRESS")
DATABASE = os.getenv("DB_DATABASE", "SCHOOL")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")

# Selection du pilote ODBC disponible
drivers = pyodbc.drivers()
if "ODBC Driver 17 for SQL Server" in drivers:
    DRIVER_NAME = "ODBC Driver 17 for SQL Server"
elif "ODBC Driver 18 for SQL Server" in drivers:
    DRIVER_NAME = "ODBC Driver 18 for SQL Server"
else:
    DRIVER_NAME = "SQL Server"

# Chaine de connexion ODBC construite dynamiquement
if USER and PASSWORD:
    CONNECTION_STRING = (
        f"DRIVER={{{DRIVER_NAME}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USER};"
        f"PWD={PASSWORD};"
    )
else:
    CONNECTION_STRING = (
        f"DRIVER={{{DRIVER_NAME}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )


# ─────────────────────────────────────────
# FONCTION DE CONNEXION
# ─────────────────────────────────────────

# Ouvre et retourne une nouvelle connexion a la base de donnees.
# Appelee a chaque requete API.
# timeout=5 : si le serveur SQL ne repond pas en 5 secondes, on abandonne
# au lieu de bloquer la requete FastAPI indefiniment.
def get_connection():
    try:
        conn = pyodbc.connect(CONNECTION_STRING, timeout=5)
        return conn
    except pyodbc.Error as e:
        # HTTPException au lieu d'une Exception generique : FastAPI sait la
        # transformer en vraie reponse HTTP 503, avec un message clair pour
        # le client, au lieu d'un 500 brut illisible.
        raise HTTPException(
            status_code=503,
            detail="Impossible de se connecter à la base de données. Réessaie dans quelques instants.",
        )