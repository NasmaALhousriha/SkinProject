
import enum
from typing import List, TYPE_CHECKING
from datetime import date
from sqlalchemy import Integer, String, Date as SQLAlchemyDate, Text, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .user_model import User
    from .report_model import Report
    from .appointment_model import Appointment
    from .diagnosis_model import Diagnosis

class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    patient_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    date_of_birth: Mapped[date] = mapped_column(SQLAlchemyDate, nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(SQLAlchemyEnum(GenderEnum,name="gender_enum"), nullable=True)
    medical_history: Mapped[str] = mapped_column(Text, nullable=True)

    # Foreign Key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="patient")
    user: Mapped["User"] = relationship("User", back_populates="patient_profile")
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )
    diagnoses: Mapped[List["Diagnosis"]] = relationship(
        "Diagnosis", back_populates="patient", cascade="all, delete-orphan"
    )