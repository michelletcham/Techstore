
# stripe_service.py
# Gestion des paiements Stripe pour Techstore By Michelle
import os
import stripe
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
stripe.api_key = STRIPE_API_KEY

def create_checkout_session(cart_items, success_url, cancel_url):
	try:
		line_items = []
		for item in cart_items:
			line_items.append({
				'price_data': {
					'currency': 'eur',
					'product_data': {
						'name': item['name'],
						'description': item.get('description', '')
					},
					'unit_amount': int(item['price'] * 100),
				},
				'quantity': item['quantity'],
			})
		session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=line_items,
			mode='payment',
			success_url=success_url,
			cancel_url=cancel_url
		)
		return session
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

def handle_webhook(payload, sig_header, endpoint_secret):
	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, endpoint_secret
		)
		return event
	except stripe.error.SignatureVerificationError as e:
		raise HTTPException(status_code=400, detail="Webhook signature verification failed")
