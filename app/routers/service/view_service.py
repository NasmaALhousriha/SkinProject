from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.service_model import Service
from pydantic import BaseModel
from typing import Optional
from app.schemas import ServiceResponse


router = APIRouter(
    prefix="/services",
    tags=["Services"]
)




@router.get("/", response_model=List[ServiceResponse])
def get_all_services(db: Session = Depends(get_db)):

    services = db.query(Service).options(
        joinedload(Service.devices)
    ).all()

    return services

@router.get("/{service_id}", response_model=ServiceResponse)
def get_single_service_details(
    service_id: int,
    db: Session = Depends(get_db)
):

    service = db.query(Service).options(
        joinedload(Service.devices)
    ).filter(
        Service.service_id == service_id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service