from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Offer(Base):
    __tablename__ = "offers"

    offer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    discount: Mapped[float | None] = mapped_column(Float, nullable=True)