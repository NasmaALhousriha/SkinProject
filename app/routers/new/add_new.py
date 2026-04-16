import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException,File,Form,UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import News
# from app.schemas import NewsCreate, NewsResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NewsCreate(BaseModel):
    title: str
    content: str
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        content: str = Form(...),
        image: UploadFile = File(None),
    ):
        return cls(
            title=title,
            content=content,
            image=image,
        )

class NewsResponse(BaseModel):
    news_id: int
    title: str
    content: str
    image: Optional[str] = None
    date: datetime

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

UPLOAD_DIR = "static/news_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/", response_model=NewsResponse)
def add_news(
        news_data: NewsCreate = Depends(NewsCreate.as_form),
        db: Session = Depends(get_db)

):
    saved_image_path = None

    # 2. إذا وجد ملف، نقوم بحفظه على الهاردسك أولاً
    if news_data.image:
        try:
            # توليد اسم فريد للملف لمنع التكرار (مثلاً: a1b2c3d4.jpg)
            extension = news_data.image.filename.split(".")[-1]
            unique_filename = f"{uuid4()}.{extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            # حفظ الملف فعلياً
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(news_data.image.file, buffer)

            # 3. المسار الذي سيتم تخزينه في قاعدة البيانات (String)
            saved_image_path = f"/{UPLOAD_DIR}/{unique_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    # 4. الآن نمرر 'saved_image_path' (النص) وليس الـ 'image' (الكائن)

    new_item = News(
        title=news_data.title,
        content=news_data.content,
        image=saved_image_path
    )



    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item