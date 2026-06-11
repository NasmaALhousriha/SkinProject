from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import os, shutil
from datetime import datetime

from app.database import get_db
from app.models import Appointment, PatientProfile
from app.models.appointment_model import AppointmentTypeEnum
from app.models.user_model import User, UserRoleEnum
from app.models.doctor_model import DoctorProfile
from app.schemas import DoctorCreate, DoctorResponse
from app.dependencies import get_current_secretary, hash_password

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/create", response_model=DoctorResponse)
def create_doctor(
    doctor_data: DoctorCreate,
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
    db.refresh(user)

    return DoctorResponse(
        doctor_id=doctor_profile.doctor_id,
        user=user,
        bio=doctor_profile.bio,
        years_of_experience=doctor_profile.years_of_experience,
        position=doctor_profile.position,
        education=doctor_profile.education,
        clinical_expertise=doctor_profile.clinical_expertise
    )



@router.get("/doctor/{doctor_id}/cancelled")
def get_doctor_cancelled_appointments(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    appointments = db.query(Appointment).options(
        joinedload(Appointment.patient).joinedload(PatientProfile.user)
    ).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == AppointmentTypeEnum.CANCELLED
    ).all()

    return [
        {
            "appointment_id": a.appointment_id,
            "patientName": a.patient.user.name,
            "phone": a.patient.user.phone,
            "date": a.date_time.strftime("%Y-%m-%d"),
            "time": a.date_time.strftime("%H:%M"),
            "status": a.status.value
        }
        for a in appointments
    ]