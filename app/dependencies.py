from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user_model import User, UserRoleEnum
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])  # bcrypt limit


bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.user_id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user
def get_current_secretary(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRoleEnum.SECRETARY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Only secretaries can perform this action."
        )

    if not current_user.secretary_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Secretary profile not found."
        )

    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Only admins can perform this action."
        )

    return current_user