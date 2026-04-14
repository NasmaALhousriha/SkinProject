from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.service_model import Service
from pydantic import BaseModel
from typing import Optional


router = APIRouter(
    prefix="/services",
    tags=["Services"]
)


class DeviceSchema(BaseModel):
    device_id: int
    name: str
    description: Optional[str]
    image: Optional[str]

    class Config:
        from_attributes = True


class DoctorSchema(BaseModel):
    doctor_id: int
    position: Optional[str]


    class Config:
        from_attributes = True


class ServiceResponse(BaseModel):
    service_id: int
    name: str
    devices: List[DeviceSchema] = []
    doctors: List[DoctorSchema] = []



    class Config:
        from_attributes = True


@router.get("/", response_model=List[ServiceResponse])
def get_all_services(db: Session = Depends(get_db)):

    services = db.query(Service).all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
def get_single_service_details(service_id: int, db: Session = Depends(get_db)):

    service = db.query(Service).options(
        joinedload(Service.devices),
        joinedload(Service.doctors)
    ).filter(Service.service_id == service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service
