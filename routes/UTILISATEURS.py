from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from database import get_connection  # adapte l'import selon ton projet (pyodbc/pymssql)
from security import hash_password
from auth import require_role

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])


# ---------- Schémas ----------

class UtilisateurOut(BaseModel):
    IdUtilisateur: int
    Nom: str
    Prenom: str
    IdRole: int
    CreePar: Optional[int] = None
    CreeParNom: Optional[str] = None
    ModifiePar: Optional[int] = None
    ModifieParNom: Optional[str] = None
    # MotdePasse volontairement absent : jamais renvoyé au client


class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    motdepasse: str
    id_role: int


class UtilisateurUpdate(BaseModel):
    nom: str
    prenom: str
    id_role: int


class MotDePasseUpdate(BaseModel):
    motdepasse: str


# ---------- Helper ----------

def row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def call_ps_action_utilisateurs(p_mode: int, p_idUtilisateur=None, p_nom=None, p_prenom=None,
                                 p_motdepasse=None, p_idRole=None, p_idUtilisateurConnecte=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            EXEC PS_ACTION_UTILISATEURS
                @p_mode = ?, @p_idUtilisateur = ?, @p_nom = ?, @p_prenom = ?,
                @p_motdepasse = ?, @p_idRole = ?, @p_idUtilisateurConnecte = ?
            """,
            (p_mode, p_idUtilisateur, p_nom, p_prenom,
             p_motdepasse, p_idRole, p_idUtilisateurConnecte),
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
# p_idUtilisateurConnecte vient maintenant du token JWT (via get_current_user),
# plus question que le client le fournisse lui-même.

@router.get("", response_model=list[UtilisateurOut])
def lister_utilisateurs():
    """Liste tous les utilisateurs (mode 0)."""
    return call_ps_action_utilisateurs(p_mode=0)


@router.get("/{id_utilisateur}", response_model=UtilisateurOut)
def obtenir_utilisateur(id_utilisateur: int):
    """Récupère un utilisateur précis (mode 0 filtré)."""
    rows = call_ps_action_utilisateurs(p_mode=0, p_idUtilisateur=id_utilisateur)
    if not rows:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return rows[0]


@router.post("", status_code=201)
def creer_utilisateur(utilisateur: UtilisateurCreate, user: dict = Depends(require_role(1))):
    """Crée un nouvel utilisateur (mode 1)."""
    call_ps_action_utilisateurs(
        p_mode=1,
        p_nom=utilisateur.nom,
        p_prenom=utilisateur.prenom,
        p_motdepasse=hash_password(utilisateur.motdepasse),
        p_idRole=utilisateur.id_role,
        p_idUtilisateurConnecte=user["id_utilisateur"],
    )
    return {"message": "Utilisateur créé avec succès"}


@router.put("/{id_utilisateur}")
def modifier_utilisateur(id_utilisateur: int, utilisateur: UtilisateurUpdate, user: dict = Depends(require_role(1))):
    """Modifie un utilisateur existant, hors mot de passe (mode 2)."""
    call_ps_action_utilisateurs(
        p_mode=2,
        p_idUtilisateur=id_utilisateur,
        p_nom=utilisateur.nom,
        p_prenom=utilisateur.prenom,
        p_idRole=utilisateur.id_role,
        p_idUtilisateurConnecte=user["id_utilisateur"],
    )
    return {"message": "Utilisateur modifié avec succès"}


@router.patch("/{id_utilisateur}/mot-de-passe")
def changer_mot_de_passe(id_utilisateur: int, payload: MotDePasseUpdate, user: dict = Depends(require_role(1))):
    """Change uniquement le mot de passe (mode 3)."""
    call_ps_action_utilisateurs(
        p_mode=3,
        p_idUtilisateur=id_utilisateur,
        p_motdepasse=hash_password(payload.motdepasse),
        p_idUtilisateurConnecte=user["id_utilisateur"],
    )
    return {"message": "Mot de passe modifié avec succès"}