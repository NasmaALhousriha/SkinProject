from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import News
from app.schemas import NewsResponse

router = APIRouter(
    prefix="/news",
    tags=["news"]
)


@router.get("/add_news", response_model=List[NewsResponse])
def get_all_news(db: Session = Depends(get_db)):
    return db.query(News).all()


@router.get("/{news_id}", response_model=NewsResponse)
def get_news_by_id(news_id: int, db: Session = Depends(get_db)):

    news_item = db.query(News).filter(
        News.news_id == news_id
    ).first()

    if not news_item:
        raise HTTPException(
            status_code=404,
            detail="News not found"
        )

    return news_item