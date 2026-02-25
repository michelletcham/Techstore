
# auth.py
# Gestion de l'authentification pour Techstore By Michelle
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from app import models, database
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "changez_moi")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
	return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@router.post("/signup")
async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
	user = db.query(models.User).filter((models.User.username == username) | (models.User.email == email)).first()
	if user:
		return templates.TemplateResponse("signup.html", {"request": request, "error": "Nom d'utilisateur ou email déjà utilisé."})
	hashed_password = get_password_hash(password)
	new_user = models.User(username=username, email=email, hashed_password=hashed_password)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	response = RedirectResponse(url="/login", status_code=303)
	return response


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
	user = db.query(models.User).filter(models.User.username == username).first()
	if not user or not verify_password(password, user.hashed_password):
		return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides."})
	access_token = create_access_token(data={"sub": user.username})
	response = RedirectResponse(url="/", status_code=303)
	response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
	return response
