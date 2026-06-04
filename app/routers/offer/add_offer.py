import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Offer
from app.services.notification_services import NotificationService
from app.database import SessionLocal
from app.models.user_model import UserRoleEnum
from app.dependencies import get_current_user
from app.schemas import OfferCreate, OfferResponse

router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)

UPLOAD_DIR = "static/offer_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/add", response_model=OfferResponse)
def add_offer(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(...),
    start_date: datetime = Form(...),
    end_date: datetime = Form(...),
    discount: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):


    image_path = None

    if image:
        ext = image.filename.split(".")[-1].lower()
        allowed = {"jpg", "jpeg", "png", "webp"}

        if ext not in allowed:
            raise HTTPException(status_code=400, detail="Invalid image type")

        filename = f"{uuid4()}.{ext}"
        file_location = os.path.join(UPLOAD_DIR, filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/{UPLOAD_DIR}/{filename}"

    new_offer = Offer(
        title=title,
        description=description,
        image=image_path,
        start_date=start_date,
        end_date=end_date,
        discount=discount

    )

    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    background_tasks.add_task(
        NotificationService.notify_all_patients,
        SessionLocal,
        title="🔥 عرض جديد!",
        message=f"لقد أضفنا عرضاً جديداً: {title}",

    )

    return {
        "offer_id": new_offer.offer_id,
        "title": new_offer.title,
        "description": new_offer.description,
        "image": new_offer.image,
        "start_date": new_offer.start_date,
        "end_date": new_offer.end_date,
        "discount": new_offer.discount
    }


@router.put("/{offer_id}", response_model=OfferResponse)
def update_offer(
    offer_id: int,
    title: str = Form(None),
    description: str = Form(None),
    start_date: datetime = Form(None),
    end_date: datetime = Form(None),
    discount: float = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    offer = db.query(Offer).filter(Offer.offer_id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if title:
        offer.title = title

    if description:
        offer.description = description

    if start_date:
        offer.start_date = start_date

    if end_date:
        offer.end_date = end_date

    if discount is not None:
        offer.discount = discount

    if image:
        ext = image.filename.split(".")[-1].lower()
        allowed = {"jpg", "jpeg", "png", "webp"}

        if ext not in allowed:
            raise HTTPException(status_code=400, detail="Invalid image type")

        if offer.image:
            old_path = offer.image.replace("/", "", 1)
            if os.path.exists(old_path):
                os.remove(old_path)

        filename = f"{uuid4()}.{ext}"
        file_location = os.path.join(UPLOAD_DIR, filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        offer.image = f"/{UPLOAD_DIR}/{filename}"

    db.commit()
    db.refresh(offer)

    return offer

@router.delete("/{offer_id}")
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
):
    offer = db.query(Offer).filter(
        Offer.offer_id == offer_id
    ).first()

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found"
        )

    offer.is_active = False

    db.commit()

    return {"message": "Offer deactivated successfully"}