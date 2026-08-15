import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt

def hash_password(plain_password: str) -> str:
    """Hache un mot de passe en clair."""
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare un mot de passe en clair à son hash stocké en base."""
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


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