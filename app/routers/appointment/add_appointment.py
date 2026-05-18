from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel

from app.database import get_db
from app.models import Notification, User, UserRoleEnum
from app.models.appointment_model import Appointment, AppointmentTypeEnum
from app.models.patient_model import PatientProfile
from app.models.doctor_model import DoctorProfile
from app.schemas import AppointmentCreate, AppointmentResponse
from app.services.email_service import send_appointment_confirmation_email



router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("/add")
async def add_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    try:
        date_time = datetime.strptime(
            f"{data.date} {data.time}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date/time format. Use YYYY-MM-DD and HH:MM"
        )

    if date_time < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointment in the past"
        )

    start_time = date_time
    end_time = start_time + timedelta(minutes=30)

    existing_appointment = db.query(Appointment).filter(

        Appointment.date_time >= start_time,
        Appointment.date_time < end_time
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="This time slot is already booked"
        )

    doctor = db.query(DoctorProfile).filter(
        DoctorProfile.doctor_id == data.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(404, "Doctor not found")

    patient = db.query(PatientProfile).join(PatientProfile.user).filter(
        PatientProfile.user.has(email=data.email)
    ).first()

    if not patient:
        raise HTTPException(404, "Patient not found")

    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.doctor_id,
        Appointment.date_time >= start_time,
        Appointment.date_time < end_time
    ).first()

    if existing_appointment:
        raise HTTPException(400, "This time slot is already booked")

    new_appointment = Appointment(
        doctor_id=doctor.doctor_id,
        patient_id=patient.patient_id,
        date_time=date_time,
        status=AppointmentTypeEnum.PENDING,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    try:
        await send_appointment_confirmation_email(
            patient_name=patient.user.name,
            patient_email=patient.user.email,
            doctor_name=doctor.user.name,
            appointment_date=date_time,
            appointment_time=date_time.strftime('%H:%M')
        )
    except Exception as e:
        print("Email error:", e)

    return {
        "message": "Appointment created successfully",
        "appointment_id": new_appointment.appointment_id,

        "name": patient.user.name,

        "email": patient.user.email,

        "phone": patient.user.phone,

        "doctorName": doctor.user.name,

        "date": data.date,

        "time": data.time,

        "status": new_appointment.status.value
    }

@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    data: AppointmentCreate,
    db: Session = Depends(get_db)
):

    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(404, "Appointment not found")

    now = datetime.now(timezone.utc)

    time_difference = appointment.date_time - now

    if time_difference < timedelta(hours=24):
        raise HTTPException(
            status_code=400,
            detail="Appointments cannot be modified within 24 hours"
        )

    appointment.date_time = datetime.strptime(
        f"{data.date} {data.time}",
        "%Y-%m-%d %H:%M"
    )

    appointment.doctor_id = data.doctor_id

    secretaries = db.query(User).filter(
        User.role == UserRoleEnum.SECRETARY
    ).all()

    for sec in secretaries:
        notification = Notification(
            user_id=sec.user_id,
            title="تعديل موعد",
            message=(
                f"المريض {appointment.patient.user.name} "
                f"عدّل موعده مع الدكتور {appointment.doctor.user.name} "
                f"إلى {appointment.date_time.strftime('%Y-%m-%d %H:%M')}"
            )
        )
        db.add(notification)

    db.commit()

    return {
        "message": "Appointment updated"
    }

@router.get("/patient/{patient_id}")
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):

    appointments = db.query(Appointment).options(
        joinedload(Appointment.doctor).joinedload(DoctorProfile.user)
    ).filter(
        Appointment.patient_id == patient_id
    ).all()

    return [
        {
            "appointment_id": a.appointment_id,
            "doctorName": a.doctor.user.name,
            "date": a.date_time.strftime("%Y-%m-%d"),
            "time": a.date_time.strftime("%H:%M"),
            "status": a.status.value
        }
        for a in appointments
    ]

@router.get("/doctor/{doctor_id}")
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):

    appointments = db.query(Appointment).options(
        joinedload(Appointment.patient).joinedload(PatientProfile.user)
    ).filter(
        Appointment.doctor_id == doctor_id
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


