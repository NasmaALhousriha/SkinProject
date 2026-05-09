from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Appointment, PatientProfile, DoctorProfile, Notification
from app.models.user_model import User, UserRoleEnum
from app.models.secretary_model import SecretaryProfile
from app.schemas import SecretaryCreate, SecretaryResponse
from app.dependencies import hash_password, get_current_admin

router = APIRouter(prefix="/secretaries", tags=["Secretaries"])


@router.post("/create",response_model=SecretaryResponse)
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

    return SecretaryResponse(
        secretary_id=secretary_profile.secretary_id,
        user=user
    )



@router.get("/appointments")
def get_secretary_appointments(
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):

    query = db.query(Appointment).options(
        joinedload(Appointment.patient).joinedload(PatientProfile.user),
        joinedload(Appointment.doctor).joinedload(DoctorProfile.user)
    )

    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)

    appointments = query.all()

    return [
        {
            "appointment_id": a.appointment_id,
            "patientName": a.patient.user.name,
            "doctorName": a.doctor.user.name,
            "phone": a.patient.user.phone,
            "date": a.date_time.strftime("%Y-%m-%d"),
            "time": a.date_time.strftime("%H:%M"),
            "status": a.status.value,
            "approved": a.approved_by_secretary
        }
        for a in appointments
    ]


@router.get("/notifications")
def get_secretary_notifications(
                                db: Session = Depends(get_db)):

    notifications = db.query(Notification).all()

    return [
        {
            "notification_id": n.notification_id,
            "title": n.title,
            "message": n.message,
            "created_at": n.created_at
        }
        for n in notifications
    ]