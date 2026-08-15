from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError

from database import get_connection
from security import verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentification"])

# OAuth2PasswordBearer lit le token depuis le header "Authorization: Bearer <token>"
# tokenUrl pointe vers l'endpoint de login (utilisé par la doc Swagger pour le bouton "Authorize")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_utilisateur: int
    nom: str
    prenom: str
    id_role: int


def row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
# OAuth2PasswordRequestForm attend des champs "username" et "password"
# (standard OAuth2, imposé par FastAPI) — on mappe "username" sur ton champ Nom.

@router.post("/login", response_model=TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Requête directe (pas de procédure stockée) : uniquement utilisée ici,
        # pour vérifier le mot de passe. Jamais renvoyée telle quelle au client.
        cursor.execute(
            "SELECT IdUtilisateur, Nom, Prenom, MotdePasse, IdRole "
            "FROM UTILISATEURS WHERE Nom = ?",
            (form_data.username,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom ou mot de passe incorrect",
            )
        user = row_to_dict(cursor, row)
    finally:
        cursor.close()
        conn.close()

    if not verify_password(form_data.password, user["MotdePasse"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom ou mot de passe incorrect",
        )

    token = create_access_token(id_utilisateur=user["IdUtilisateur"], id_role=user["IdRole"])
    return TokenOut(
        access_token=token,
        id_utilisateur=user["IdUtilisateur"],
        nom=user["Nom"],
        prenom=user["Prenom"],
        id_role=user["IdRole"],
    )


# ---------------------------------------------------------------------------
# Dépendance : utilisateur courant à partir du token
# ---------------------------------------------------------------------------
# À utiliser dans toutes les routes protégées : def route(user = Depends(get_current_user))

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session invalide ou expirée",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        id_utilisateur = int(payload.get("sub"))
        id_role = payload.get("id_role")
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    return {"id_utilisateur": id_utilisateur, "id_role": id_role}


# ---------------------------------------------------------------------------
# Dépendance : restreindre une route à certains rôles
# ---------------------------------------------------------------------------
# Usage : def route(user = Depends(require_role(1))) -> reserve a IdRole=1 (Administrateur)
# Usage : def route(user = Depends(require_role(1, 2))) -> autorise IdRole 1 OU 2

def require_role(*allowed_role_ids: int):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["id_role"] not in allowed_role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu n'as pas les droits pour effectuer cette action",
            )
        return user
    return checker