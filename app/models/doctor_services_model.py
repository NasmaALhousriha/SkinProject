from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class DoctorService(Base):
    __tablename__ = "doctor_services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor_profiles.doctor_id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.service_id"), nullable=False)