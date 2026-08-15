from dotenv import load_dotenv
load_dotenv()  # charge le .env AVANT les autres imports, qui en dependent

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from auth import router as auth_router
from routes.ECOLES import router as ecoles_router
from routes.ENTREPRISES import router as entreprises_router
from routes.UTILISATEURS import router as utilisateurs_router
from routes.ROLES import router as roles_router

app = FastAPI(title="API SCHOOL")

# Ouvert a toutes les origines pour le developpement (double-clic sur le HTML,
# Live Server, ngrok...). A restreindre a une liste precise le jour du deploiement.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ecoles_router)
app.include_router(entreprises_router)
app.include_router(utilisateurs_router)
app.include_router(roles_router)


@app.get("/")
def read_root():
    return {"message": "API SCHOOL opérationnelle"}

@app.get("/{filename}.html")
def serve_html(filename: str):
    file_path = Path(f"{filename}.html")
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page introuvable")