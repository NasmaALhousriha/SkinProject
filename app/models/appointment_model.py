
import enum
from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .doctor_model import DoctorProfile
    from .patient_model import PatientProfile


class AppointmentTypeEnum(str, enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentTypeEnum] = mapped_column(
        SQLAlchemyEnum(AppointmentTypeEnum, name="appointment_status_enum"), nullable=False, )
    approved_by_secretary: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(String(200), nullable=True)

    # Foreign keys
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor_profiles.doctor_id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.patient_id"),
                                            nullable=False)

    # Relationships
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", back_populates="appointments")
    patient: Mapped["PatientProfile"] = relationship("PatientProfile",
                                                     back_populates="appointments")
