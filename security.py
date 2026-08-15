import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError

# ---------------------------------------------------------------------------
# Hachage des mots de passe (bcrypt)
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hache un mot de passe en clair. À utiliser à la création d'un
    utilisateur et au changement de mot de passe, avant l'INSERT/UPDATE."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare un mot de passe en clair (saisi au login) à son hash stocké en base."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT — session après authentification réussie
# ---------------------------------------------------------------------------
# SECRET_KEY : à mettre dans .env, jamais en dur. Génère-la avec :
#   python -c "import secrets; print(secrets.token_hex(32))"

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-moi-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8h de session


def create_access_token(id_utilisateur: int, id_role: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(id_utilisateur),
        "id_role": id_role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Lève jose.JWTError si le token est invalide ou expiré."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])