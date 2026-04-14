from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.offer_model import Offer



class OfferBase(BaseModel):
    title: str
    description: str
    image: Optional[str] = None
    duration: Optional[str] = None
    discount: Optional[float] = None

class OfferResponse(OfferBase):
    offer_id: int

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/offers",
    tags=["offers"]
)

# جلب كل العروض
@router.get("/", response_model=List[OfferResponse])
def get_all_offers(db: Session = Depends(get_db)):
    offers_list = db.query(Offer).all()
    return offers_list

# جلب عرض واحد عن طريق ID
@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer_by_id(offer_id: int, db: Session = Depends(get_db)):
    offer_item = db.query(Offer).filter(Offer.offer_id == offer_id).first()
    if not offer_item:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer_item