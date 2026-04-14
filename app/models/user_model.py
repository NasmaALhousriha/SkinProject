import enum
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


if TYPE_CHECKING:
    from .doctor_model import DoctorProfile
    from .patient_model import PatientProfile
    from .notification_model import Notification
    from .secretary_model import SecretaryProfile

class UserRoleEnum(str, enum.Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"
    SECRETARY = "secretary"

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(SQLAlchemyEnum(UserRoleEnum), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctor_profile: Mapped[Optional["DoctorProfile"]] = relationship(
        "DoctorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    patient_profile: Mapped[Optional["PatientProfile"]] = relationship(
        "PatientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    secretary_profile: Mapped[Optional["SecretaryProfile"]] = relationship(
        "SecretaryProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

# class SecretaryProfile(Base):
#     """
#     موديل للمساعدين / السكرتارية لو بدك تخصيص بيانات إضافية.
#     """
#     __tablename__ = "secretary_profiles"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     phone_number = Column(String)
#     assigned_doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"))  # لو السكرتير مرتبط بدكتور محدد
#
#     user = relationship("User")
#     assigned_doctor = relationship("DoctorProfile")

# class MedicalRecord(Base):
#     """
#     سجل طبي شامل لكل مريض، يمكن ربطه بالـ PatientProfile
#     """
#     __tablename__ = "medical_records"
#     id = Column(Integer, primary_key=True)
#     patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=False)
#     record_text = Column(Text)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#
#     patient = relationship("PatientProfile")

# class Prescription(Base):
#     """
#     وصفات الأدوية للمرضى مرتبطة بالدكتور والمريض
#     """
#     __tablename__ = "prescriptions"
#     id = Column(Integer, primary_key=True)
#     doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
#     patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=False)
#     prescription_text = Column(Text)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#
#     doctor = relationship("DoctorProfile")
#     patient = relationship("PatientProfile")











