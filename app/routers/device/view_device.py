from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.device_model import Device
from app.schemas import DeviceResponse

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)


@router.get("/all", response_model=List[DeviceResponse])
def get_all_devices(
    db: Session = Depends(get_db)
):
    devices = db.query(Device).all()

    return devices