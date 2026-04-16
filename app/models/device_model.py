from app.database import Base
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
   from .specialist_model import Specialist
   from  .service_model  import Service


class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.service_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # foreignkey
    specialist_id: Mapped[int] = mapped_column(ForeignKey("specialists.specialist_id"), nullable=False)

    # relationship
    service: Mapped["Service"] = relationship("Service", back_populates="devices")
    specialist: Mapped["Specialist"] = relationship("Specialist", back_populates="devices", foreign_keys=[specialist_id])
