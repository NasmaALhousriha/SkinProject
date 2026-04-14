import enum

from typing import TYPE_CHECKING
from datetime import time
from sqlalchemy import Integer, Time as SQLAlchemyTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .doctor_model import DoctorProfile


class DayOfWeekEnum(str, enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    # Columns
    doctor_schedule_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    day_of_week: Mapped[DayOfWeekEnum] = mapped_column(SQLAlchemyEnum(DayOfWeekEnum, name="day_of_week_enum"),
                                                       nullable=False)
    start_time: Mapped[time] = mapped_column(SQLAlchemyTime, nullable=False)
    end_time: Mapped[time] = mapped_column(SQLAlchemyTime, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(default=30)

    # Foreign Key
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor_profiles.doctor_id"), nullable=False)
    # Relationship
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", back_populates="schedules")









































