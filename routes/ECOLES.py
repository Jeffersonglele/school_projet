from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date

from database import get_connection  # adapte l'import selon ton projet (pyodbc/pymssql)
from auth import get_current_user

router = APIRouter(prefix="/ecoles", tags=["Ecoles"])


# ---------- Schémas ----------

class EcoleOut(BaseModel):
    IdEcole: int
    Nom: str
    Telephone: Optional[str] = None
    Adresse: Optional[str] = None
    SiteWeb: Optional[str] = None
    Facebook: Optional[str] = None
    Visite: Optional[bool] = None
    Valide: Optional[bool] = None
    Actif: bool
    Directeur: Optional[str] = None
    AnneeEnregistrement: Optional[int] = None


class EcoleCreate(BaseModel):
    nom: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    directeur: Optional[str] = None
    siteweb: Optional[str] = None
    facebook: Optional[str] = None
    visite: Optional[bool] = None
    valide: Optional[bool] = None


class EcoleUpdate(BaseModel):
    nom: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    directeur: Optional[str] = None
    siteweb: Optional[str] = None
    facebook: Optional[str] = None
    visite: Optional[bool] = None
    valide: Optional[bool] = None


# ---------- Helper ----------

def row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def call_ps_action_ecoles(p_mode: int, p_idEcole=None, p_nom=None, p_telephone=None,
                           p_adresse=None, p_directeur=None, p_siteweb=None,
                           p_facebook=None, p_visite=None, p_valide=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            EXEC PS_ACTION_ECOLES
                @p_mode = ?, @p_idEcole = ?, @p_nom = ?, @p_telephone = ?,
                @p_adresse = ?, @p_directeur = ?, @p_siteweb = ?,
                @p_facebook = ?, @p_visite = ?, @p_valide = ?
            """,
            (p_mode, p_idEcole, p_nom, p_telephone, p_adresse,
             p_directeur, p_siteweb, p_facebook, p_visite, p_valide),
        )

        rows = []
        if cursor.description:
            rows = [row_to_dict(cursor, row) for row in cursor.fetchall()]

        conn.commit()
        return rows
    finally:
        cursor.close()
        conn.close()


# ---------- Routes ----------

@router.get("", response_model=list[EcoleOut])
def lister_ecoles():
    """Liste toutes les écoles (mode 0)."""
    return call_ps_action_ecoles(p_mode=0)


@router.get("/{id_ecole}", response_model=EcoleOut)
def obtenir_ecole(id_ecole: int):
    """Récupère une école précise (mode 0 filtré)."""
    rows = call_ps_action_ecoles(p_mode=0, p_idEcole=id_ecole)
    if not rows:
        raise HTTPException(status_code=404, detail="École introuvable")
    return rows[0]


@router.post("", status_code=201)
def creer_ecole(ecole: EcoleCreate, user: dict = Depends(get_current_user)):
    """Crée une nouvelle école (mode 1)."""
    call_ps_action_ecoles(
        p_mode=1,
        p_nom=ecole.nom,
        p_telephone=ecole.telephone,
        p_adresse=ecole.adresse,
        p_directeur=ecole.directeur,
        p_siteweb=ecole.siteweb,
        p_facebook=ecole.facebook,
        p_visite=ecole.visite,
        p_valide=ecole.valide,
    )
    return {"message": "École créée avec succès"}


@router.put("/{id_ecole}")
def modifier_ecole(id_ecole: int, ecole: EcoleUpdate, user: dict = Depends(get_current_user)):
    """Modifie une école existante (mode 2)."""
    call_ps_action_ecoles(
        p_mode=2,
        p_idEcole=id_ecole,
        p_nom=ecole.nom,
        p_telephone=ecole.telephone,
        p_adresse=ecole.adresse,
        p_directeur=ecole.directeur,
        p_siteweb=ecole.siteweb,
        p_facebook=ecole.facebook,
        p_visite=ecole.visite,
        p_valide=ecole.valide,
    )
    return {"message": "École modifiée avec succès"}


@router.patch("/{id_ecole}/desactiver")
def desactiver_ecole(id_ecole: int, user: dict = Depends(get_current_user)):
    """Désactive une école (mode 3, soft delete)."""
    call_ps_action_ecoles(p_mode=3, p_idEcole=id_ecole)
    return {"message": "École désactivée"}


@router.patch("/{id_ecole}/activer")
def activer_ecole(id_ecole: int, user: dict = Depends(get_current_user)):
    """Réactive une école (mode 4)."""
    call_ps_action_ecoles(p_mode=4, p_idEcole=id_ecole)
    return {"message": "École activée"}