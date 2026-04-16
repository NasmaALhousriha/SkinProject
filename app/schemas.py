from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from fastapi import Form, UploadFile, File
from app.models.patient_model import GenderEnum


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    medical_history: Optional[str] = None

    class Config:
        orm_mode = True

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        phone: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        date_of_birth: Optional[date] = Form(None),
        gender: Optional[GenderEnum] = Form(None),
        medical_history: Optional[str] = Form(None),
    ):
        return cls(
            name=name,
            phone=phone,
            email=email,
            date_of_birth=date_of_birth,
            gender=gender,
            medical_history=medical_history,
        )


class PatientProfileResponse(BaseModel):
    user_id: int
    name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    medical_history: Optional[str]

    class Config:
        from_attributes = True


class UpdatePatientResponse(BaseModel):
    message: str
    patient_id: int
    user_id: int


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # doctor / patient / secretary

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    class Config:
        orm_mode = True

# Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

#  Appointments
class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    date_time: datetime
    notes: Optional[str] = None

class AppointmentOut(BaseModel):
    appointment_id: int
    doctor_id: int
    patient_id: int
    date_time: datetime
    status: str
    approved_by_secretary: bool
    notes: Optional[str]
    class Config:
        orm_mode = True

# Diagnosis
class DiagnosisCreate(BaseModel):
    doctor_id: int
    patient_id: int
    diagnosis_text: str
    audio_url: Optional[str] = None

class DiagnosisOut(BaseModel):
    diagnosis_id: int
    doctor_id: int
    patient_id: int
    diagnosis_text: str
    audio_url: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

#Doctors
class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    photo: Optional[UploadFile] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None
    position: Optional[str] = None
    education: Optional[str] = None
    clinical_expertise: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        phone: Optional[str] = Form(None),
        photo: UploadFile = File(None),
        bio: Optional[str] = Form(None),
        years_of_experience: Optional[int] = Form(None),
        position: Optional[str] = Form(None),
        education: Optional[str] = Form(None),
        clinical_expertise: Optional[str] = Form(None),
    ):
        return cls(
            name=name,
            email=email,
            password=password,
            phone=phone,
            photo=photo,
            bio=bio,
            years_of_experience=years_of_experience,
            position=position,
            education=education,
            clinical_expertise=clinical_expertise,
        )

class DoctorCreateResponse(BaseModel):
    message: str
    doctor_id: int
    user_id: int

#  Secretaries
class SecretaryCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        phone: Optional[str] = Form(None),
    ):
        return cls(
            name=name,
            email=email,
            password=password,
            phone=phone,
        )

class SecretaryCreateResponse(BaseModel):
    message: str
    secretary_id: int
    user_id: int
