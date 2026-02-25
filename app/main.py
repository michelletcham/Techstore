from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
from app import models, database, auth
from app.models import Product, Cart, Order, OrderItem, User

from dotenv import load_dotenv
import os
import datetime

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
templates = Jinja2Templates(directory="templates")

# --- CHAT CLIENT/SERVICE ---
from fastapi.responses import JSONResponse
from app.models import ChatMessage
from sqlalchemy import or_

# Récupérer les messages du chat pour l'utilisateur courant (client ou admin)
@app.get("/api/chat/messages")
def get_chat_messages(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Non authentifié"})
    # L'admin peut voir tous les messages, le client seulement les siens
    if getattr(user, "is_admin", False):
        messages = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
    else:
        messages = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).order_by(ChatMessage.created_at.asc()).all()
    return [{
        "id": m.id,
        "user_id": m.user_id,
        "sender": m.sender,
        "message": m.message,
        "created_at": m.created_at.strftime('%d/%m/%Y %H:%M') if m.created_at else ""
    } for m in messages]

# Envoyer un message (client ou admin)
@app.post("/api/chat/send")
async def send_chat_message(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Non authentifié"})
    data = await request.json()
    msg = data.get("message", "").strip()
    if not msg:
        return JSONResponse(status_code=400, content={"error": "Message vide"})
    sender = "admin" if getattr(user, "is_admin", False) else "client"
    chat_msg = ChatMessage(user_id=user.id if sender=="client" else data.get("user_id", user.id), sender=sender, message=msg)
    db.add(chat_msg)
    db.commit()
    # Si c'est le premier message du client, ajouter une réponse automatique
    if sender == "client":
        count = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).count()
        if count == 1:
            auto = ChatMessage(user_id=user.id, sender="admin", message="Bonjour, merci pour votre message. Un conseiller va vous répondre.")
            db.add(auto)
            db.commit()
    return {"success": True}


# Action retour admin
@app.post("/admin/order-retour-action")
def admin_retour_action(request: Request, order_id: int = Form(...), retour_action: str = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order and order.retour_statut and order.retour_statut.startswith("Demandé"):
        # On garde la raison si elle existe
        raison = ""
        if "(" in order.retour_statut:
            raison = order.retour_statut[order.retour_statut.find("(") : ]
        else:
            raison = ""
        order.retour_statut = retour_action + (f" {raison}" if raison else "")
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# Action remboursement admin
@app.post("/admin/order-remboursement-action")
def admin_remboursement_action(request: Request, order_id: int = Form(...), remboursement_action: str = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.remboursement_statut = remboursement_action
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)
# Demande de retour/remboursement (client)
@app.post("/orders/{order_id}/retour")
def demande_retour(order_id: int, request: Request, raison_retour: str = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order or order.statut != "Livré":
        return RedirectResponse(url="/profile", status_code=303)
    # Permettre une nouvelle demande si refusé ou aucun retour
    if not order.retour_statut or order.retour_statut == "Aucun" or order.retour_statut.startswith("Refusé"):
        order.retour_statut = f"Demandé ({raison_retour})"
        db.commit()
    return RedirectResponse(url="/profile", status_code=303)

# Détail produit (GET)
@app.get("/product/{product_id}", response_class=HTMLResponse)
def product_detail(request: Request, product_id: int, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/", status_code=303)
    ratings = db.query(models.ProductRating).filter(models.ProductRating.product_id == product_id).order_by(models.ProductRating.created_at.desc()).limit(10).all()
    # Récupérer les médias du produit (images/vidéos)
    media = db.query(models.ProductMedia).filter(models.ProductMedia.product_id == product_id).all()
    return templates.TemplateResponse("product_detail.html", {"request": request, "product": product, "user": user, "ratings": ratings, "media": media})

# Noter un produit (POST)
@app.post("/product/{product_id}/rate", response_class=HTMLResponse)
def rate_product(request: Request, product_id: int, rating: int = Form(...), comment: str = Form(None), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/", status_code=303)
    # Enregistrer l'évaluation
    new_rating = models.ProductRating(product_id=product_id, user_id=user.id, rating=rating, comment=comment)
    db.add(new_rating)
    db.commit()
    # Mettre à jour la note moyenne
    ratings = db.query(models.ProductRating).filter(models.ProductRating.product_id == product_id).all()
    if ratings:
        avg = sum(r.rating for r in ratings) / len(ratings)
        product.rating = round(avg, 2)
        db.commit()
    return RedirectResponse(url=f"/product/{product_id}", status_code=303)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    products = db.query(Product).all()
    year = datetime.datetime.now().year
    return templates.TemplateResponse("home.html", {"request": request, "products": products, "user": user, "year": year})



# Route pour changer le statut d'une commande (doit être après app = FastAPI())
@app.post("/admin/order-status")
def update_order_status(request: Request, order_id: int = Form(...), statut: str = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)

    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.statut = statut
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)



# Connexion (GET)
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse("login.html", {"request": request, "user": user})

# Connexion (POST)
@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    from app.auth import verify_password, create_access_token
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides."})
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

# Liste des produits
@app.get("/products", response_class=HTMLResponse)
def list_products(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    products = db.query(Product).all()
    return templates.TemplateResponse("product.html", {"request": request, "products": products, "user": user})



# Panier - Affichage sécurisé
def get_current_user_from_cookie(request: Request, db: Session = Depends(database.get_db)):
    from jose import JWTError, jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "changez_moi")
    ALGORITHM = "HS256"
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        scheme, _, param = token.partition(" ")
        if scheme.lower() != "bearer":
            return None
        payload = jwt.decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user

# Profil utilisateur (GET)

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    for order in orders:
        order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order.items:
            item.product = db.query(Product).filter(Product.id == item.product_id).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "orders": orders})

# Profil utilisateur (POST)
@app.post("/profile", response_class=HTMLResponse)
def update_profile(request: Request, email: str = Form(...), address: str = Form(None), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    user.email = email
    user.address = address
    db.commit()
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    for order in orders:
        order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order.items:
            item.product = db.query(Product).filter(Product.id == item.product_id).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "orders": orders, "success": "Profil mis à jour."})

@app.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()
    products = []
    for item in cart_items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if prod:
            products.append({
                "id": prod.id,
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "quantity": item.quantity
            })
    return templates.TemplateResponse("cart.html", {"request": request, "cart": products, "user": user})

# Ajouter au panier (sécurisé)
@app.post("/cart/add")
def add_to_cart(request: Request, product_id: int = Form(...), quantity: int = Form(1), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_item = db.query(Cart).filter(Cart.user_id == user.id, Cart.product_id == product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=user.id, product_id=product_id, quantity=quantity)
        db.add(cart_item)
    db.commit()
    # Redirige vers /products avec un message de succès
    response = RedirectResponse(url="/products?added=1", status_code=303)
    return response


# Modifier quantité (sécurisé)
@app.post("/cart/update")
def update_cart(request: Request, product_id: int = Form(...), quantity: int = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_item = db.query(Cart).filter(Cart.user_id == user.id, Cart.product_id == product_id).first()
    if cart_item:
        cart_item.quantity = quantity
        db.commit()
    return RedirectResponse(url="/cart", status_code=303)


# Supprimer du panier (sécurisé)
@app.post("/cart/remove")
def remove_from_cart(request: Request, product_id: int = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_item = db.query(Cart).filter(Cart.user_id == user.id, Cart.product_id == product_id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
    return RedirectResponse(url="/cart", status_code=303)


# Paiement Stripe (sécurisé)
from app.stripe_service import create_checkout_session

@app.post("/create-checkout-session")
def create_checkout(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Panier vide")
    items = []
    for item in cart_items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if prod:
            items.append({
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "quantity": item.quantity
            })
    success_url = str(request.base_url) + "succes"
    cancel_url = str(request.base_url) + "cart"
    session = create_checkout_session(items, success_url, cancel_url)
    return RedirectResponse(url=session.url, status_code=303)


# Dépendance pour récupérer l'utilisateur connecté via JWT
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
SECRET_KEY = os.getenv("SECRET_KEY", "changez_moi")
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# Commandes - Historique utilisateur (sécurisé)
@app.get("/orders", response_class=HTMLResponse)
def view_orders(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    # Charger les items et produits pour chaque commande
    for order in orders:
        order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order.items:
            item.product = db.query(Product).filter(Product.id == item.product_id).first()
    return templates.TemplateResponse("order.html", {"request": request, "orders": orders, "user": user})

# Création de commande après paiement réussi (sécurisé)
@app.post("/orders/create")

def create_order_core(user, cart_items, db):
    total = 0
    order = Order(user_id=user.id, total=0)
    db.add(order)
    db.commit()
    db.refresh(order)
    for item in cart_items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if prod:
            if prod.stock is not None and prod.stock >= item.quantity:
                prod.stock -= item.quantity
            else:
                prod.stock = 0
            total += prod.price * item.quantity
            order_item = OrderItem(order_id=order.id, product_id=prod.id, quantity=item.quantity)
            db.add(order_item)
    db.commit()
    order.total = total
    db.query(Cart).filter(Cart.user_id == user.id).delete()
    db.commit()
    return order

def create_order(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Panier vide")
    order = create_order_core(user, cart_items, db)
    return {"message": "Commande créée", "order_id": order.id}


# Succès paiement
@app.get("/succes", response_class=HTMLResponse)
def payment_success(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()
    if cart_items:
        create_order_core(user, cart_items, db)
    return templates.TemplateResponse("succes.html", {"request": request, "user": user})


# Admin (protégé)
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    products = db.query(Product).all()
    users = db.query(User).all()
    orders = db.query(Order).all()
    # Charger les relations pour affichage (user, items, product)
    for order in orders:
        order.user = db.query(User).filter(User.id == order.user_id).first()
        order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order.items:
            item.product = db.query(Product).filter(Product.id == item.product_id).first()
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "products": products, "users": users, "orders": orders})

# Promouvoir un utilisateur admin
@app.post("/admin/promote")
def promote_user(request: Request, user_id: int = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    target = db.query(User).filter(User.id == user_id).first()
    if target:
        target.is_admin = True
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# Rétrograder un admin
@app.post("/admin/demote")
def demote_user(request: Request, user_id: int = Form(...), db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    target = db.query(User).filter(User.id == user_id).first()
    if target and target.id != user.id:
        target.is_admin = False
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# Ajout de produit avec upload d'image
from fastapi import UploadFile, File
import shutil


from fastapi import File, UploadFile
import shutil

@app.post("/admin/add-product")
async def add_product(request: Request,
                name: str = Form(...),
                description: str = Form(...),
                price: float = Form(...),
                stock: int = Form(...),
                media: list = File(None),
                media_urls: str = Form(None),
                db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    # Création du produit (on met la première image comme image_url principale)
    image_url = None
    product = Product(name=name, description=description, price=price, stock=stock)
    db.add(product)
    db.commit()
    # Gestion des fichiers uploadés et des URLs externes (max 5 au total)
    medias = []
    if media:
        medias.extend(media)
    url_list = []
    if media_urls:
        url_list = [u.strip() for u in media_urls.splitlines() if u.strip()]
    total = len(medias) + len(url_list)
    if total > 5:
        # On limite à 5 au total
        medias = medias[:max(0,5-len(url_list))]
        url_list = url_list[:5]
    image_folder = "static/images/"
    os.makedirs(image_folder, exist_ok=True)
    idx = 0
    # Fichiers uploadés
    for file in medias:
        filename = f"{product.id}_{idx}_{file.filename}"
        file_path = os.path.join(image_folder, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        url = f"/static/images/{filename}"
        ext = filename.split('.')[-1].lower()
        media_type = 'video' if ext in ['mp4', 'webm', 'ogg'] else 'image'
        pm = models.ProductMedia(product_id=product.id, media_url=url, media_type=media_type)
        db.add(pm)
        if idx == 0:
            image_url = url
        idx += 1
    # URLs externes
    for u in url_list:
        ext = u.split('.')[-1].lower()
        media_type = 'video' if ext in ['mp4', 'webm', 'ogg'] else 'image'
        pm = models.ProductMedia(product_id=product.id, media_url=u, media_type=media_type)
        db.add(pm)
        if idx == 0:
            image_url = u
        idx += 1
    # Mettre à jour l'image principale
    product.image_url = image_url
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

# Route GET pour afficher le formulaire d’édition de produit
@app.get("/admin/edit-product/{product_id}", response_class=HTMLResponse)
def edit_product_form(request: Request, product_id: int, db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse("edit_product.html", {"request": request, "product": product, "user": user})

# Route POST pour enregistrer les modifications
@app.post("/admin/edit-product/{product_id}")
def edit_product(request: Request,
                product_id: int,
                name: str = Form(...),
                description: str = Form(...),
                price: float = Form(...),
                stock: int = Form(...),
                image: UploadFile = File(None),
                image_url: str = Form(None),
                db: Session = Depends(database.get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, "is_admin", False):
        return RedirectResponse(url="/login", status_code=303)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/admin", status_code=303)
    # Mise à jour des champs
    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    # Gestion de l’image
    if image and image.filename:
        image_folder = "static/images/"
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join(image_folder, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product.image_url = f"/static/images/{image.filename}"
    elif image_url:
        product.image_url = image_url
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
