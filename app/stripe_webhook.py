# stripe_webhook.py
# Endpoint pour recevoir les notifications Stripe et créer la commande après paiement
import os
import stripe
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.models import User, Product, Cart, Order, OrderItem
from app.database import SessionLocal
from dotenv import load_dotenv

load_dotenv()
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
stripe.api_key = STRIPE_API_KEY

app = FastAPI()

@app.post("/stripe/webhook")
def stripe_webhook(request: Request):
    payload = request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get('customer_email')
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        if user:
            cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()
            if cart_items:
                total = 0
                order = Order(user_id=user.id, total=0)
                db.add(order)
                db.commit()
                db.refresh(order)
                for item in cart_items:
                    prod = db.query(Product).filter(Product.id == item.product_id).first()
                    if prod:
                        total += prod.price * item.quantity
                        order_item = OrderItem(order_id=order.id, product_id=prod.id, quantity=item.quantity)
                        db.add(order_item)
                order.total = total
                db.query(Cart).filter(Cart.user_id == user.id).delete()
                db.commit()
        db.close()
    return JSONResponse(status_code=200, content={"status": "success"})
