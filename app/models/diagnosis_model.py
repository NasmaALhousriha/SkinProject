# diagnosis
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from .doctor_model import DoctorProfile
    from .patient_model import PatientProfile


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    # Columns
    diagnosis_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    diagnosis_text: Mapped[str] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Foreign Keys
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor_profiles.doctor_id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.patient_id"), nullable=False)

    # Relationships
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", back_populates="diagnoses")
    patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="diagnoses")


