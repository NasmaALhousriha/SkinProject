from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import os

from app.database import get_db
from app.models.user_model import User, UserRoleEnum
from app.models.patient_model import PatientProfile
from app.schemas import RegisterPatientRequest, TokenResponse, LoginRequest
from app.dependencies import hash_password

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 30)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Auth"])


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=TokenResponse)
def register_patient(data: RegisterPatientRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRoleEnum.PATIENT
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(PatientProfile(user_id=user.user_id))
    db.commit()

    token = create_access_token({
        "sub": str(user.user_id),
        "role": user.role.value
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.user_id
    )


@router.post("/login", response_model=TokenResponse)
def login_user(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.role == UserRoleEnum.DOCTOR and not user.doctor_profile:
        raise HTTPException(status_code=403, detail="Doctor profile missing")

    if user.role == UserRoleEnum.SECRETARY and not user.secretary_profile:
        raise HTTPException(status_code=403, detail="Secretary profile missing")

    token = create_access_token({
        "sub": str(user.user_id),
        "role": user.role.value
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.user_id
    )