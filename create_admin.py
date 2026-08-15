"""
Script a lancer UNE SEULE FOIS pour creer le tout premier utilisateur,
avant que l'authentification ne soit utilisable.

Usage :
    python create_admin.py

Il utilise directement ta procedure stockee PS_ACTION_UTILISATEURS (mode 1),
avec p_idUtilisateurConnecte = NULL (personne n'est connecte au moment de
la creation du tout premier compte, la colonne CreePar accepte NULL).
"""

from database import get_connection
from security import hash_password

print("=== Création du premier utilisateur admin ===\n")

nom = input("Nom : ").strip()
prenom = input("Prénom : ").strip()
mot_de_passe = input("Mot de passe (sera haché) : ").strip()
id_role = input("IdRole (voir table ROLES, ex: 1 pour admin) : ").strip()

if not nom or not prenom or not mot_de_passe or not id_role:
    print("Tous les champs sont obligatoires.")
    raise SystemExit(1)

hashed = hash_password(mot_de_passe)

conn = get_connection()
cursor = conn.cursor()
try:
    cursor.execute(
        """
        EXEC PS_ACTION_UTILISATEURS
            @p_mode = ?, @p_nom = ?, @p_prenom = ?, @p_motdepasse = ?,
            @p_idRole = ?, @p_idUtilisateurConnecte = ?
        """,
        (1, nom, prenom, hashed, int(id_role), None),
    )
    conn.commit()
    print(f"\nUtilisateur '{nom} {prenom}' créé avec succès.")
    print("Tu peux maintenant te connecter via POST /auth/login.")
finally:
    cursor.close()
    conn.close()