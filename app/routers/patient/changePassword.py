from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.dependencies import get_current_user
from app.routers.auth.auth import  verify_password, pwd_context


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
   )


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="Current old password")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_password: str = Field(..., description="Confirm password")

@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
        password_data: ChangePasswordRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # لجلب المستخدم المسجل حالياً
):
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match"
        )

    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the old password"
        )

    hashed_new_password = pwd_context.hash(password_data.new_password)

    current_user.password_hash = hashed_new_password

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password changed successfully"}

