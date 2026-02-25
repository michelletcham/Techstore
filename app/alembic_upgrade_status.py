# Script temporaire pour ajouter le champ statut aux commandes existantes
from app.database import SessionLocal
from sqlalchemy import text

def main():
    db = SessionLocal()
    try:
        db.execute(text('ALTER TABLE orders ADD COLUMN statut VARCHAR DEFAULT "En cours"'))
        db.commit()
        print("Champ 'statut' ajouté à la table orders.")
    except Exception as e:
        print("Déjà appliqué ou erreur :", e)
    db.close()

if __name__ == "__main__":
    main()
