from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os, shutil
from datetime import datetime

from app.database import get_db
from app.models.user_model import User, UserRoleEnum
from app.models.doctor_model import DoctorProfile
from app.schemas import DoctorCreate, DoctorCreateResponse
from app.dependencies import get_current_secretary, hash_password

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/create", response_model=DoctorCreateResponse)
def create_doctor(
    doctor_data: DoctorCreate = Depends(DoctorCreate.as_form),
    db: Session = Depends(get_db),
    current_secretary: User = Depends(get_current_secretary)
):

    existing_user = db.query(User).filter(User.email == doctor_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    photo_path = None
    if doctor_data.photo:
        upload_dir = os.path.join(os.getcwd(), "static", "doctor_photos")
        os.makedirs(upload_dir, exist_ok=True)

        file_extension = os.path.splitext(doctor_data.photo.filename)[1]
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{doctor_data.photo.filename}"
        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(doctor_data.photo.file, buffer)

        photo_path = f"/static/doctor_photos/{unique_filename}"

    user = User(
        name=doctor_data.name,
        email=doctor_data.email,
        password_hash=hash_password(doctor_data.password),
        role=UserRoleEnum.DOCTOR,
        phone=doctor_data.phone,
        photo=photo_path
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    doctor_profile = DoctorProfile(
        user_id=user.user_id,
        bio=doctor_data.bio,
        years_of_experience=doctor_data.years_of_experience,
        position=doctor_data.position,
        education=doctor_data.education,
        clinical_expertise=doctor_data.clinical_expertise
    )

    db.add(doctor_profile)
    db.commit()
    db.refresh(doctor_profile)

    return {
        "message": "Doctor created successfully",
        "user_id": user.user_id,
        "doctor_id": doctor_profile.doctor_id
    }