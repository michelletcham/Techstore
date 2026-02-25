# Script interactif pour promouvoir un utilisateur en admin
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
print("Utilisateurs existants :")
users = db.query(User).all()
for u in users:
    print(f"- {u.username} | {u.email}")

ident = input("Entrez le nom d'utilisateur ou l'email à promouvoir : ").strip()
user = db.query(User).filter((User.username == ident) | (User.email == ident)).first()
if user:
    user.is_admin = True
    db.commit()
    print(f"{user.username} ({user.email}) est maintenant admin.")
else:
    print("Utilisateur non trouvé.")
db.close()
