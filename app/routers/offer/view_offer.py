from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.models.offer_model import Offer
from app.schemas import OfferResponse
from datetime import datetime


router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)




@router.get("/active_offers", response_model=list[OfferResponse])
def get_active_offers(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    offers = db.query(Offer).filter(
        Offer.is_active.is_(True),
        Offer.start_date <= now,
        Offer.end_date >= now
    ).all()
    return offers

@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer_by_id(offer_id: int, db: Session = Depends(get_db)):

    offer = db.query(Offer).filter(
        Offer.offer_id == offer_id
    ).first()

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found"
        )

    return offer