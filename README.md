# Techstore By Michelle

Application web FastAPI pour la vente de produits tech.

## Structure du projet

- `app/`
  - `auth.py` : Authentification
  - `database.py` : Connexion à la base de données
  - `main.py` : Point d'entrée FastAPI
  - `models.py` : Modèles de données
  - `stripe_service.py` : Paiement Stripe
- `templates/`
  - `admin.html`, `cart.html`, `home.html`, `login.html`

## Installation

1. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
2. Lancez le serveur :
   ```bash
   uvicorn app.main:app --reload
   ```

## Déploiement

- Prêt pour Render et GitHub.

---

Remplacez les contenus des fichiers HTML et Python par vos besoins réels.
