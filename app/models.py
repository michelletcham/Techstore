
# ...existing code...

# (après la déclaration de Base)


# models.py
# Modèles de données pour Techstore By Michelle
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

# Table pour les images/vidéos multiples par produit
class ProductMedia(Base):
    __tablename__ = "product_media"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    media_url = Column(String, nullable=False)
    media_type = Column(String, nullable=False)  # 'image' ou 'video'
    product = relationship("Product", backref="media")

# Placer ChatMessage ici, après Base
class ChatMessage(Base):
	__tablename__ = "chat_messages"
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	sender = Column(String, nullable=False)  # 'client' ou 'admin'
	message = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProductRating(Base):
	__tablename__ = "product_ratings"
	id = Column(Integer, primary_key=True, index=True)
	product_id = Column(Integer, ForeignKey("products.id"))
	user_id = Column(Integer, ForeignKey("users.id"))
	rating = Column(Integer, nullable=False)
	comment = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, index=True, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	is_active = Column(Boolean, default=True)
	is_admin = Column(Boolean, default=False)
	address = Column(String, nullable=True)  # Adresse de livraison
	orders = relationship("Order", back_populates="user")

class Product(Base):
	__tablename__ = "products"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	description = Column(String)
	price = Column(Float, nullable=False)
	stock = Column(Integer, default=0)
	image_url = Column(String, nullable=True)
	rating = Column(Float, nullable=True)  # Note moyenne du produit

class Order(Base):
	__tablename__ = "orders"
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_at = Column(DateTime, default=datetime.datetime.utcnow)
	total = Column(Float, nullable=False)
	statut = Column(String, default="En cours")  # Nouveau champ statut
	retour_statut = Column(String, default=None, nullable=True)  # Statut du retour ("Aucun", "Demandé", "Accepté", "Refusé", etc.)
	remboursement_statut = Column(String, default=None, nullable=True)  # Statut du remboursement
	user = relationship("User", back_populates="orders")
	items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
	__tablename__ = "order_items"
	id = Column(Integer, primary_key=True, index=True)
	order_id = Column(Integer, ForeignKey("orders.id"))
	product_id = Column(Integer, ForeignKey("products.id"))
	quantity = Column(Integer, default=1)
	order = relationship("Order", back_populates="items")
	product = relationship("Product")

class Cart(Base):
	__tablename__ = "carts"
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	product_id = Column(Integer, ForeignKey("products.id"))
	quantity = Column(Integer, default=1)
