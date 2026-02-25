# Script d'initialisation des produits pour Techstore By Michelle
from app.database import SessionLocal
from app.models import Product

products = [
    {"name": "Souris sans fil Logitech", "description": "Souris ergonomique et précise.", "price": 120, "stock": 20, "image_url": "https://cdn.pixabay.com/photo/2016/03/27/19/40/mouse-1284257_1280.jpg"},
    {"name": "Clavier mécanique Redragon", "description": "Clavier RGB compact.", "price": 150, "stock": 15, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/keyboard-1959544_1280.jpg"},
    {"name": "Casque audio Sony", "description": "Son stéréo, micro intégré.", "price": 180, "stock": 10, "image_url": "https://cdn.pixabay.com/photo/2016/11/29/09/32/headphones-1868612_1280.jpg"},
    {"name": "Webcam HD Logitech", "description": "Webcam 1080p pour visioconférence.", "price": 110, "stock": 12, "image_url": "https://cdn.pixabay.com/photo/2014/12/21/23/50/webcam-579127_1280.png"},
    {"name": "Enceinte Bluetooth JBL", "description": "Portable, autonomie 12h.", "price": 130, "stock": 18, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/speaker-1959546_1280.jpg"},
    {"name": "Chargeur rapide Anker", "description": "USB-C, 30W.", "price": 100, "stock": 25, "image_url": "https://cdn.pixabay.com/photo/2016/03/27/19/40/charger-1284258_1280.jpg"},
    {"name": "Batterie externe Xiaomi", "description": "10 000 mAh, compacte.", "price": 140, "stock": 22, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/powerbank-1959545_1280.jpg"},
    {"name": "Montre connectée Amazfit", "description": "Suivi santé, notifications.", "price": 200, "stock": 8, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/smartwatch-1959547_1280.jpg"},
    {"name": "Lampe LED USB", "description": "Flexible, faible conso.", "price": 105, "stock": 30, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/usb-lamp-1959548_1280.jpg"},
    {"name": "Support téléphone voiture", "description": "Magnétique, universel.", "price": 115, "stock": 16, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/phone-holder-1959549_1280.jpg"},
    {"name": "Clé USB 64Go SanDisk", "description": "USB 3.0, rapide.", "price": 110, "stock": 40, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/usb-1959550_1280.jpg"},
    {"name": "Mini drone caméra", "description": "Caméra HD, pilotage facile.", "price": 300, "stock": 5, "image_url": "https://cdn.pixabay.com/photo/2016/11/29/09/32/drone-1868613_1280.jpg"},
    {"name": "Tapis de souris XXL", "description": "Antidérapant, grande taille.", "price": 100, "stock": 35, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/mousepad-1959551_1280.jpg"},
    {"name": "Hub USB 4 ports", "description": "USB 3.0, compact.", "price": 125, "stock": 28, "image_url": "https://cdn.pixabay.com/photo/2017/01/06/19/15/usb-hub-1959552_1280.jpg"},
    {"name": "Caméra de surveillance WiFi", "description": "Vision nocturne, application mobile.", "price": 500, "stock": 6, "image_url": "https://cdn.pixabay.com/photo/2016/11/29/09/32/security-camera-1868614_1280.jpg"}
]

def init_products():
    db = SessionLocal()
    for prod in products:
        exists = db.query(Product).filter(Product.name == prod["name"]).first()
        if not exists:
            p = Product(
                name=prod["name"],
                description=prod["description"],
                price=prod["price"],
                stock=prod["stock"]
            )
            # Ajout du champ image_url si le modèle Product le permet
            if hasattr(p, "image_url"):
                p.image_url = prod["image_url"]
            db.add(p)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_products()