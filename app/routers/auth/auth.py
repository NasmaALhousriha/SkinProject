from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import os

from app.database import get_db
from app.models.user_model import User, UserRoleEnum
from app.models.patient_model import PatientProfile

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 30)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterPatientRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])  # bcrypt limit

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", status_code=201, response_model=TokenResponse)
def register_patient(data: RegisterPatientRequest, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # إنشاء User
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRoleEnum.PATIENT
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    patient_profile = PatientProfile(user_id=user.user_id)
    db.add(patient_profile)
    db.commit()

    access_token = create_access_token(data={"sub": str(user.user_id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

@router.post("/login", response_model=TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.role == UserRoleEnum.DOCTOR and not user.doctor_profile:
        raise HTTPException(status_code=403, detail="Doctor profile not found")
    if user.role == UserRoleEnum.SECRETARY and not user.secretary_profile:
        raise HTTPException(status_code=403, detail="Secretary profile not found")

    access_token = create_access_token(data={
        "sub": str(user.user_id),
        "role": user.role.value
    })

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


