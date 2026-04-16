from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.doctor_model import DoctorProfile
from app.models.appointment_model import Appointment
from app.models.diagnosis_model import Diagnosis
from app.models.doctorschedule_model import DoctorSchedule

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)




class ClinicHour(BaseModel):
    day: str
    start: Optional[str]
    end: Optional[str]

    class Config:
        from_attributes = True


class DoctorProfileResponse(BaseModel):
    doctor_id: int
    name: str
    photo: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    education: Optional[str] = None
    clinical_expertise: Optional[str] = None
    description: Optional[str] = None
    professionalBiography: Optional[str] = None

    starRating: Optional[float] = 0.0
    patientReviews: Optional[int] = 0
    patientNumbers: Optional[int] = 0
    clinicHours: List[ClinicHour] = []

    class Config:
        from_attributes = True



def format_doctor_data(doctor, db: Session):
    try:
        patient_count = db.query(func.count(Appointment.patient_id)).filter(
            Appointment.doctor_id == doctor.doctor_id).scalar() or 0
        reviews_count = db.query(func.count(Diagnosis.diagnosis_id)).filter(
            Diagnosis.doctor_id == doctor.doctor_id).scalar() or 0

        schedules = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor.doctor_id).all()
        clinic_hours = [
            {"day": s.day_of_week.value, "start": s.start_time.strftime("%H:%M") if s.start_time else None,
             "end": s.end_time.strftime("%H:%M") if s.end_time else None}
            for s in schedules
        ]

        return {
            "doctor_id": doctor.doctor_id,  
            "name": doctor.user.name if doctor.user else "Unknown",
            "photo": doctor.user.photo if doctor.user else None,
            "phone": doctor.user.phone if doctor.user else None,
            "email": doctor.user.email if doctor.user else None,
            "position": doctor.position,
            "yearsOfExperience": doctor.years_of_experience,
            "education": doctor.education,
            "clinical_expertise": doctor.clinical_expertise,
            "description": doctor.bio,
            "professionalBiography": doctor.bio,
            "starRating": 0.0,
            "patientReviews": reviews_count,
            "patientNumbers": patient_count,
            "clinicHours": clinic_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting doctor data: {str(e)}")



@router.get("/", response_model=List[DoctorProfileResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    doctors = db.query(DoctorProfile).options(joinedload(DoctorProfile.user)).all()

    return [format_doctor_data(doc, db) for doc in doctors]


@router.get("/{doctor_id}", response_model=DoctorProfileResponse)
def view_doctor_profile(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorProfile).options(joinedload(DoctorProfile.user)).filter(
        DoctorProfile.doctor_id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return format_doctor_data(doctor, db)