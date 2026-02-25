# Script de migration pour ajouter le champ address à la table users
from sqlalchemy import create_engine, text
import os

db_url = os.getenv("DATABASE_URL", "sqlite:///techstore.db")
engine = create_engine(db_url)

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN address VARCHAR"))
        print("Champ 'address' ajouté à la table users.")
    except Exception as e:
        print("Déjà appliqué ou erreur :", e)
