from fastapi import APIRouter
from pydantic import BaseModel

from database import get_connection

router = APIRouter(prefix="/roles", tags=["Roles"])


class RoleOut(BaseModel):
    IdRole: int
    LibelleRole: str


def row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


@router.get("", response_model=list[RoleOut])
def lister_roles():
    """Liste tous les rôles disponibles (pour remplir une liste déroulante)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IdRole, LibelleRole FROM ROLES ORDER BY LibelleRole")
        return [row_to_dict(cursor, row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()