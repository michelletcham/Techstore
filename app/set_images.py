# Script pour associer des images aux produits existants
import os
from app.database import SessionLocal
from app.models import Product

def main():
    db = SessionLocal()
    # Dictionnaire d'association nom produit -> image (à adapter selon tes produits)
    image_map = {
        "ordinateur": "/static/images/laptop.jpg",
        "phone": "/static/images/phone.jpg",
        "casque": "/static/images/headphones.jpg",
        "clavier": "/static/images/keyboard.jpg",
        "souris": "/static/images/mouse.jpg",
        # Ajoute d'autres associations ici
    }
    default_image = "/static/images/default.jpg"
    products = db.query(Product).all()
    for product in products:
        # Associe une image selon le nom du produit (en minuscule)
        img = default_image
        for key, url in image_map.items():
            if key in product.name.lower():
                img = url
                break
        product.image_url = img
    db.commit()
    db.close()
    print("Images associées aux produits existants.")

if __name__ == "__main__":
    main()
