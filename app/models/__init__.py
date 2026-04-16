# Import Base first
from app.database import Base

# Import Enums and base models (no dependencies)
from .user_model import User, UserRoleEnum
from .service_model import Service
from .specialist_model import Specialist

# Import profile models that depend on User
from .secretary_model import SecretaryProfile
from .doctor_model import DoctorProfile
from .patient_model import PatientProfile

# Import models that depend on multiple entities
from .appointment_model import Appointment
from .diagnosis_model import Diagnosis
from .doctorschedule_model import DoctorSchedule
from .notification_model import Notification
from .offer_model import Offer
from .device_model import Device
from .new_model import News
from .report_model import Report
from .doctor_services_model import DoctorService

# Export all models
__all__ = [
    "Base",
    "User",
    "UserRoleEnum",
    "Service",
    "Specialist",
    "SecretaryProfile",
    "DoctorProfile",
    "PatientProfile",
    "Appointment",
    "Diagnosis",
    "DoctorSchedule",
    "Notification",
    "Offer",
    "Device",
    "News",
    "Report",
    "DoctorService",
]
