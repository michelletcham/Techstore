# Script pour créer toutes les tables de la base de données
from app.models import Base
from app.database import engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")
