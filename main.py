from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from sqlalchemy.orm import Session
from app.database import engine, Base, LocalSession
from app.models.user_model import User, UserRoleEnum
from app.models.patient_model import PatientProfile
from app.models.doctor_model import DoctorProfile
from app.models.appointment_model import Appointment

from app.models.diagnosis_model import Diagnosis
from app.models.notification_model import Notification
from app.models.doctorschedule_model import DoctorSchedule
from app.models.offer_model import Offer
from app.models.service_model import Service
from app.models.device_model import Device
from app.models.specialist_model import Specialist
from app.models.report_model import Report
from app.models.new_model import News
from app.models.doctor_services_model import DoctorService
from app.models.secretary_model import SecretaryProfile

# Middlewares
from fastapi.middleware.cors import CORSMiddleware

# Routers
# from app.routers.audio.audio_router import router as audio_router
from app.routers.auth.auth import router as auth_router
from app.routers.report.add_report import router as add_report_router
from  app.routers.patient.edit_patient import router as patient_router
from  app.routers.patient.changePassword import router as change_password_router
from app.routers.doctors.view_doctorProfile import router as doctor_profile_router
from app.routers.service.view_service import router as service_router
from app.routers.device.view_device import router as device_router
from app.routers.new.add_new import router as add_new_router
from app.routers.offer.add_offer import router as add_offer_router
from app.routers.new.view_new import router as view_new_router
from app.routers.offer.view_offer import router as view_offer_router
from app.routers.device.add_device import router as add_device_router
from app.routers.doctors.add_doctor import router as add_doctor_router
from app.routers.secretary.add_secretary import router as add_secretary_router
from app.routers.specialist.add_specialist import router as add_specialist_router


app = FastAPI()

Base.metadata.create_all(bind=engine)

# Static files
UPLOAD_DIR = os.path.join(os.getcwd(), "static")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(device_router)
app.include_router(add_new_router)
app.include_router(add_offer_router)
app.include_router(view_offer_router)
app.include_router(add_device_router)
app.include_router(view_new_router)
app.include_router(service_router)
app.include_router(change_password_router)
app.include_router(patient_router)
app.include_router(doctor_profile_router)
app.include_router(add_report_router)
app.include_router(add_doctor_router)
app.include_router(add_secretary_router)
app.include_router(add_specialist_router)

