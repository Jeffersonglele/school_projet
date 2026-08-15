from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from database import get_connection  # adapte l'import selon ton projet (pyodbc/pymssql)
from auth import get_current_user

router = APIRouter(prefix="/entreprises", tags=["Entreprises"])


# ---------- Schémas ----------

class EntrepriseOut(BaseModel):
    IdEntreprise: int
    Nom: str
    Telephone: Optional[str] = None
    Adresse: Optional[str] = None
    SiteWeb: Optional[str] = None
    Facebook: Optional[str] = None
    Email: Optional[str] = None
    RCCM: Optional[str] = None
    IFU: Optional[str] = None
    Visite: Optional[bool] = None
    Valide: Optional[bool] = None
    Actif: bool
    Responsable: Optional[str] = None
    AnneeEnregistrement: Optional[int] = None


class EntrepriseCreate(BaseModel):
    nom: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    siteweb: Optional[str] = None
    facebook: Optional[str] = None
    email: Optional[str] = None
    rccm: Optional[str] = None
    ifu: Optional[str] = None
    visite: Optional[bool] = None
    valide: Optional[bool] = None
    responsable: Optional[str] = None


class EntrepriseUpdate(BaseModel):
    nom: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    siteweb: Optional[str] = None
    facebook: Optional[str] = None
    email: Optional[str] = None
    rccm: Optional[str] = None
    ifu: Optional[str] = None
    visite: Optional[bool] = None
    valide: Optional[bool] = None
    responsable: Optional[str] = None


# ---------- Helper ----------

def row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def call_ps_action_entreprises(p_mode: int, p_idEntreprise=None, p_nom=None, p_telephone=None,
                                p_adresse=None, p_siteweb=None, p_facebook=None,
                                p_email=None, p_rccm=None, p_ifu=None,
                                p_visite=None, p_valide=None, p_responsable=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            EXEC PS_ACTION_ENTREPRISES
                @p_mode = ?, @p_idEntreprise = ?, @p_nom = ?, @p_telephone = ?,
                @p_adresse = ?, @p_siteweb = ?, @p_facebook = ?,
                @p_email = ?, @p_rccm = ?, @p_ifu = ?,
                @p_visite = ?, @p_valide = ?, @p_responsable = ?
            """,
            (p_mode, p_idEntreprise, p_nom, p_telephone, p_adresse,
             p_siteweb, p_facebook, p_email, p_rccm, p_ifu,
             p_visite, p_valide, p_responsable),
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

@router.get("", response_model=list[EntrepriseOut])
def lister_entreprises():
    """Liste toutes les entreprises (mode 0)."""
    return call_ps_action_entreprises(p_mode=0)


@router.get("/{id_entreprise}", response_model=EntrepriseOut)
def obtenir_entreprise(id_entreprise: int):
    """Récupère une entreprise précise (mode 0 filtré)."""
    rows = call_ps_action_entreprises(p_mode=0, p_idEntreprise=id_entreprise)
    if not rows:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    return rows[0]


@router.post("", status_code=201)
def creer_entreprise(entreprise: EntrepriseCreate, user: dict = Depends(get_current_user)):
    """Crée une nouvelle entreprise (mode 1)."""
    call_ps_action_entreprises(
        p_mode=1,
        p_nom=entreprise.nom,
        p_telephone=entreprise.telephone,
        p_adresse=entreprise.adresse,
        p_siteweb=entreprise.siteweb,
        p_facebook=entreprise.facebook,
        p_email=entreprise.email,
        p_rccm=entreprise.rccm,
        p_ifu=entreprise.ifu,
        p_visite=entreprise.visite,
        p_valide=entreprise.valide,
        p_responsable=entreprise.responsable,
    )
    return {"message": "Entreprise créée avec succès"}


@router.put("/{id_entreprise}")
def modifier_entreprise(id_entreprise: int, entreprise: EntrepriseUpdate, user: dict = Depends(get_current_user)):
    """Modifie une entreprise existante (mode 2)."""
    call_ps_action_entreprises(
        p_mode=2,
        p_idEntreprise=id_entreprise,
        p_nom=entreprise.nom,
        p_telephone=entreprise.telephone,
        p_adresse=entreprise.adresse,
        p_siteweb=entreprise.siteweb,
        p_facebook=entreprise.facebook,
        p_email=entreprise.email,
        p_rccm=entreprise.rccm,
        p_ifu=entreprise.ifu,
        p_visite=entreprise.visite,
        p_valide=entreprise.valide,
        p_responsable=entreprise.responsable,
    )
    return {"message": "Entreprise modifiée avec succès"}


@router.patch("/{id_entreprise}/desactiver")
def desactiver_entreprise(id_entreprise: int, user: dict = Depends(get_current_user)):
    """Désactive une entreprise (mode 3, soft delete)."""
    call_ps_action_entreprises(p_mode=3, p_idEntreprise=id_entreprise)
    return {"message": "Entreprise désactivée"}


@router.patch("/{id_entreprise}/activer")
def activer_entreprise(id_entreprise: int, user: dict = Depends(get_current_user)):
    """Réactive une entreprise (mode 4)."""
    call_ps_action_entreprises(p_mode=4, p_idEntreprise=id_entreprise)
    return {"message": "Entreprise activée"}