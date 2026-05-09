import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import News
from app.schemas import NewsResponse

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

UPLOAD_DIR = "static/news_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/add", response_model=NewsResponse)
def add_news(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_path = None

    if image:
        ext = image.filename.split(".")[-1].lower()
        allowed = {"jpg", "jpeg", "png", "webp"}

        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail="Invalid image type"
            )

        filename = f"{uuid4()}.{ext}"
        file_location = os.path.join(UPLOAD_DIR, filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/{UPLOAD_DIR}/{filename}"

    new_item = News(
        title=title,
        content=content,
        image=image_path
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item

@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int,
    title: str = Form(None),
    content: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.news_id == news_id).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    if title:
        news.title = title

    if content:
        news.content = content

    if image:
        ext = image.filename.split(".")[-1].lower()
        allowed = {"jpg", "jpeg", "png", "webp"}

        if ext not in allowed:
            raise HTTPException(status_code=400, detail="Invalid image type")

        if news.image:
            old_path = news.image.replace("/", "", 1)
            if os.path.exists(old_path):
                os.remove(old_path)

        filename = f"{uuid4()}.{ext}"
        file_location = os.path.join(UPLOAD_DIR, filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        news.image = f"/{UPLOAD_DIR}/{filename}"

    db.commit()
    db.refresh(news)

    return news

@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.news_id == news_id).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    if news.image:
        image_path = news.image.replace("/", "", 1)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete(news)
    db.commit()

    return {"message": "News deleted successfully"}