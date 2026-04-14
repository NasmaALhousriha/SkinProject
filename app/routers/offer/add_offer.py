import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Offer
from pydantic import BaseModel
from typing import Optional
from app.models.user_model import UserRoleEnum
from app.dependencies import get_current_user


class OfferBase(BaseModel):
    title: str
    description: str
    image: Optional[str] = None
    duration: int
    discount: int



class OfferResponse(OfferBase):
    offer_id: int

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/offers",
    tags=["offers"]
)

UPLOAD_DIR = "static/offer_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=OfferResponse)
def add_offer(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    duration: int = Form(...),
    discount: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)

):
    if current_user.role != UserRoleEnum.SECRETARY:
        raise HTTPException(status_code=403, detail="Only Secretaries can add offers")


    saved_image_path = None

    if image:
        try:
            extension = image.filename.split(".")[-1].lower()
            unique_filename = f"{uuid4()}.{extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            saved_image_path = f"/{UPLOAD_DIR}/{unique_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    offer_item = Offer(
        title=title,
        description=description,
        image=saved_image_path,
        duration=duration,
        discount=discount
    )

    db.add(offer_item)
    db.commit()
    db.refresh(offer_item)

    return offer_item