# Script pour associer une URL d'image à chaque produit existant
from app.database import SessionLocal
from app.models import Product

def main():
    db = SessionLocal()
    # Associe une image par nom de produit (exemples génériques, à adapter)
    url_map = {
        'ordinateur': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80',
        'phone': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80',
        'casque': 'https://images.unsplash.com/photo-1511367461989-f85a21fda167?auto=format&fit=crop&w=400&q=80',
        'clavier': 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80',
        'souris': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80',
        'tablette': 'https://images.unsplash.com/photo-1510557880182-3d4d3c1b9021?auto=format&fit=crop&w=400&q=80',
        'imprimante': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80',
        # Ajoute d'autres associations ici
    }
    default_url = 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80'
    products = db.query(Product).all()
    for product in products:
        url = default_url
        for key, val in url_map.items():
            if key in product.name.lower():
                url = val
                break
        product.image_url = url
    db.commit()
    db.close()
    print("URLs d'images associées à chaque produit.")

if __name__ == "__main__":
    main()
