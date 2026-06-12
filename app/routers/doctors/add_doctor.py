import json

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile
from pydantic import EmailStr
from sqlalchemy.orm import Session, joinedload
import os, shutil
from datetime import datetime
from fastapi import UploadFile, File, Form


from app.database import get_db

from app.models.doctorschedule_model import DoctorSchedule, DayOfWeekEnum
from app.models.appointment_model import AppointmentTypeEnum
from app.models.user_model import User, UserRoleEnum
from app.models.doctor_model import DoctorProfile
from app.schemas import DoctorCreate, DoctorResponse, DoctorUpdate
from app.dependencies import get_current_secretary, hash_password

router = APIRouter(prefix="/doctors", tags=["Doctors"])






def parse_time(t: str):
    return datetime.strptime(t, "%H:%M").time()



@router.post("/create")
def create_doctor(
    name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    phone: str = Form(None),

    position: str = Form(None),
    education: str = Form(None),
    clinical_expertise: str = Form(None),
    years_of_experience: int = Form(None),
    bio: str = Form(None),

    clinicHours: str = Form("[]"),   # JSON string
    photo: UploadFile = File(None),

    db: Session = Depends(get_db)
):


    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")


    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRoleEnum.DOCTOR,
        phone=phone
    )

    db.add(user)
    db.commit()
    db.refresh(user)


    doctor = DoctorProfile(
        user_id=user.user_id,
        bio=bio,
        years_of_experience=years_of_experience,
        position=position,
        education=education,
        clinical_expertise=clinical_expertise
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)


    if photo:
        upload_dir = os.path.join("static", "doctor_photos")
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{datetime.now().timestamp()}_{photo.filename}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        doctor.user.photo = f"/static/doctor_photos/{filename}"
        db.commit()


    try:
        clinic_hours_data = json.loads(clinicHours)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="clinicHours must be valid JSON string"
        )


    for h in clinic_hours_data:
        db.add(DoctorSchedule(
            doctor_id=doctor.doctor_id,
            day_of_week=h["day"],  # MUST match Enum
            start_time=parse_time(h["start"]),
            end_time=parse_time(h["end"])
        ))

    db.commit()

    schedules = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor.doctor_id
    ).all()

    return {
        "doctor_id": doctor.doctor_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "photo": user.photo,

        "position": doctor.position,
        "education": doctor.education,
        "clinical_expertise": doctor.clinical_expertise,
        "years_of_experience": doctor.years_of_experience,
        "bio": doctor.bio,

        "clinicHours": [
            {
                "day": s.day_of_week,
                "start": s.start_time.strftime("%H:%M"),
                "end": s.end_time.strftime("%H:%M")
            }
            for s in schedules
        ]
    }

def format_doctor(doctor, db):

    user = doctor.user

    if not user:
        raise HTTPException(500, "Doctor user relation missing")

    schedules = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor.doctor_id
    ).all()

    return {
        "doctor_id": doctor.doctor_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,

        "position": doctor.position,
        "education": doctor.education,
        "clinical_expertise": doctor.clinical_expertise,
        "years_of_experience": doctor.years_of_experience,
        "bio": doctor.bio,

        "clinicHours": [
            {
                "day": s.day_of_week,
                "start": s.start_time.strftime("%H:%M"),
                "end": s.end_time.strftime("%H:%M")
            }
            for s in schedules
        ]
    }

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, data: DoctorUpdate, db: Session = Depends(get_db)):

    doctor = db.query(DoctorProfile).filter(
        DoctorProfile.doctor_id == doctor_id,
        DoctorProfile.is_deleted == False
    ).first()

    if not doctor:
        raise HTTPException(404, "Doctor not found")

    # user fields
    if data.name:
        doctor.user.name = data.name
    if data.phone:
        doctor.user.phone = data.phone

    # doctor fields
    for field in [
        "bio", "years_of_experience",
        "position", "education", "clinical_expertise"
    ]:
        value = getattr(data, field)
        if value is not None:
            setattr(doctor, field, value)

    db.commit()

    # schedules replace
    if data.clinicHours is not None:

        db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id
        ).delete()

        for h in data.clinicHours:
            db.add(DoctorSchedule(
                doctor_id=doctor_id,
                day_of_week=h.day,
                start_time=parse_time(h.start),
                end_time=parse_time(h.end)
            ))

        db.commit()

    return format_doctor(doctor, db)

@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):

    doctor = db.query(DoctorProfile).filter(
        DoctorProfile.doctor_id == doctor_id,
        DoctorProfile.is_deleted == False
    ).first()

    if not doctor:
        raise HTTPException(404, "Doctor not found")

    doctor.is_deleted = True
    db.commit()

    return {"message": "Doctor deleted"}

@router.get("/", response_model=list[DoctorResponse])
def get_all(db: Session = Depends(get_db)):
    doctors = db.query(DoctorProfile).options(
        joinedload(DoctorProfile.user)
    ).filter(
        DoctorProfile.is_deleted == False
    ).all()

    return [format_doctor(d, db) for d in doctors]


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_one(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorProfile).options(
        joinedload(DoctorProfile.user)
    ).filter(
        DoctorProfile.doctor_id == doctor_id,
        DoctorProfile.is_deleted == False
    ).first()

    if not doctor:
        raise HTTPException(404, "Doctor not found")

    return format_doctor(doctor, db)

