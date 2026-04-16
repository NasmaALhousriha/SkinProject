from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User, UserRoleEnum
from app.models.secretary_model import SecretaryProfile
from app.schemas import SecretaryCreate, SecretaryCreateResponse
from app.dependencies import hash_password, get_current_admin

router = APIRouter(prefix="/secretaries", tags=["Secretaries"])


@router.post("/create", response_model=SecretaryCreateResponse)
def create_secretary(
    secretary_data: SecretaryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # check email
    existing_user = db.query(User).filter(User.email == secretary_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # create user
    user = User(
        name=secretary_data.name,
        email=secretary_data.email,
        password_hash=hash_password(secretary_data.password),
        role=UserRoleEnum.SECRETARY,
        phone=secretary_data.phone
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # create profile
    secretary_profile = SecretaryProfile(user_id=user.user_id)
    db.add(secretary_profile)
    db.commit()
    db.refresh(secretary_profile)

    return {
        "message": "Secretary created successfully",
        "user_id": user.user_id,
        "secretary_id": secretary_profile.secretary_id
    }