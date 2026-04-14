from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class News(Base):
    __tablename__ = "news"

    news_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())