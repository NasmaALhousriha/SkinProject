import os
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.device_model import Device
from app.models.service_model import Service



class DeviceResponse(BaseModel):
    device_id: int
    service_id: int
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

IMAGEDIR = "static/devices/"
os.makedirs(IMAGEDIR, exist_ok=True)



@router.get("/by-service/{service_id}", response_model=List[DeviceResponse])
def get_devices_by_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    devices = db.query(Device).filter(Device.service_id == service_id).all()
    return devices


