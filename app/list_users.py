# Script pour lister tous les utilisateurs
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
print("Utilisateurs en base :")
for u in users:
    print(f"- {u.username} | {u.email}")
db.close()
