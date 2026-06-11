from typing import List, Optional
from datetime import date, datetime, time
from pydantic import BaseModel, EmailStr
from fastapi import Form, UploadFile, File
from app.models.patient_model import GenderEnum
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, ConfigDict

from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel
from typing import Optional



class GenderEnum(str, Enum):
    male = "MALE"
    female = "FEMALE"

class DeviceShortResponse(BaseModel):
    device_id: int
    name: str
    image: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ServiceResponse(BaseModel):
    service_id: int
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    is_active: bool
    devices: List[DeviceShortResponse] = []

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: str
    password: str


class SpecialistCreate(BaseModel):
    name: str
    position: Optional[str] = None
    years_of_experience: Optional[int] = None

class SpecialistResponse(BaseModel):
    specialist_id: int
    name: str
    position: Optional[str]
    years_of_experience: Optional[int]
    photo: Optional[str]

    class Config:
        from_attributes = True


class OfferCreate(BaseModel):
    title: str
    description: str
    discount: Optional[float]
    start_date: datetime
    end_date: datetime

class OfferResponse(BaseModel):
    offer_id: int
    title: str
    description: str
    image: Optional[str] = None
    discount: Optional[float]
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True


class RegisterPatientRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int

class NewsBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None

class NewsResponse(BaseModel):
    news_id: int
    title: str
    content: str
    image: Optional[str] = None
    date: datetime

    class Config:
        from_attributes = True


class DeviceCreate(BaseModel):
    name: str
    # service_id: int
    # specialist_id: int
    description: Optional[str] = None
class DeviceResponse(BaseModel):
    device_id: int
    # service_id: int
    # specialist_id: int
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    phone: Optional[str]
    photo: Optional[str]

    class Config:
        from_attributes = True


class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None
    position: Optional[str] = None
    education: Optional[str] = None
    clinical_expertise: Optional[str] = None

class DoctorResponse(BaseModel):
    doctor_id: int
    user: UserResponse
    bio: Optional[str]
    years_of_experience: Optional[int]
    position: Optional[str]
    education: Optional[str]
    clinical_expertise: Optional[str]

    class Config:
        from_attributes = True


class SecretaryCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

class SecretaryResponse(BaseModel):
    secretary_id: int
    user: UserResponse

    class Config:
        from_attributes = True


class PatientResponse(BaseModel):
    patient_id: int
    user: UserResponse
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    medical_history: Optional[str]

    class Config:
        from_attributes = True
class PatientUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum]
    medical_history: Optional[str] = None

    class Config:
        from_attributes = True
class PatientUpdateResponse(BaseModel):
    message: str
    patient_id: int
    user_id: int


class AppointmentCreate(BaseModel):
    doctor_id: int
    name: str
    email: str
    phone:  str
    date: str
    time: str

class AppointmentResponse(BaseModel):
    appointment_id: int
    name: str
    phone: Optional[str] = None
    email: str
    date: str
    time: str
    doctorName: str
    status: str

    class Config:
        from_attributes = True


class DiagnosisCreate(BaseModel):
    doctor_id: int
    patient_id: int
    diagnosis_text: str

class DiagnosisResponse(BaseModel):
    diagnosis_id: int
    doctor_id: int
    patient_id: int
    diagnosis_text: str
    audio_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# class ServiceCreate(BaseModel):
#     name: str
#     description: Optional[str] = None
#
# class ServiceResponse(BaseModel):
#     service_id: int
#     name: str
#     description: Optional[str]
#
#     class Config:
#         from_attributes = True



class ReportCreate(BaseModel):
    doctor_id: int
    patient_id: int
    report_text: str
    recommendations: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: int
    doctor_id: int
    patient_id: int
    report_text: str
    recommendations: Optional[str]
    audio_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    notification_id: int
    title: str
    message: Optional[str]
    is_read: bool
    created_at: datetime
    appointment_id: Optional[int] = None

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool

class RescheduleRequest(BaseModel):
    new_date: Optional[date] = None  # تاريخ فقط
    new_time: Optional[time] = None  # وقت فقط
