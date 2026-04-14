from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import News
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NewsBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None


class NewsResponse(NewsBase):
    news_id: int
    date: datetime
    # هي الطريقة الحديثة بالكتابة بستخدم الاتربيوت بشكل مباشر
    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

# جلب كل الأخبار
@router.get("/", response_model=List[NewsResponse])
def get_all_news(db: Session = Depends(get_db)):
    news_list = db.query(News).all()
    return news_list

# جلب خبر واحد عن طريق الـ ID
@router.get("/{news_id}", response_model=NewsResponse)
def get_news_by_id(news_id: int, db: Session = Depends(get_db)):
    news_item = db.query(News).filter(News.news_id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News not found")
    return news_item