# doctor
import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


if TYPE_CHECKING:
    from .user_model import User
    from .report_model import Report
    from .service_model  import Service
    from .appointment_model import Appointment
    from .diagnosis_model import Diagnosis
    from .doctorschedule_model import DoctorSchedule


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    doctor_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bio: Mapped[str] = mapped_column(String(200), nullable=True)
    years_of_experience: Mapped[int] = mapped_column(Integer, nullable=True)
    position: Mapped[str] = mapped_column(String(100), nullable=True)
    education: Mapped[str] = mapped_column(String(200), nullable=True)
    clinical_expertise: Mapped[str] = mapped_column(String(200), nullable=True)
    # Foreign Key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="doctor")
    user: Mapped["User"] = relationship("User", back_populates="doctor_profile")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="doctor")
    diagnoses: Mapped[List["Diagnosis"]] = relationship("Diagnosis", back_populates="doctor")
    schedules: Mapped[List["DoctorSchedule"]] = relationship("DoctorSchedule", back_populates="doctor")
    services: Mapped[List["Service"]] = relationship( "Service",   secondary="doctor_services", back_populates="doctors" )

