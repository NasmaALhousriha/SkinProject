from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .patient_model import PatientProfile
    from  .doctor_model import DoctorProfile

class Report(Base):
        __tablename__ = "reports"
        report_id : Mapped[int] = mapped_column(primary_key=True , autoincrement=True)
        created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
        audio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
        content: Mapped[str] = mapped_column(Text)

        doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor_profiles.doctor_id"))
        patient_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.patient_id"))

        doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", back_populates="reports")
        patient: Mapped["PatientProfile"] = relationship("PatientProfile", back_populates="reports")
