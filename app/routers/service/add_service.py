import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.service_model import Service
from app.models.device_model import Device
from app.schemas import ServiceResponse
from typing import List

router = APIRouter(
    prefix="/services",
    tags=["Services"]
)

SERVICE_UPLOAD_DIR = "static/services/"
os.makedirs(SERVICE_UPLOAD_DIR, exist_ok=True)


def save_image(image: UploadFile):
    ext = image.filename.split(".")[-1].lower()
    filename = f"{uuid4()}.{ext}"
    path = os.path.join(SERVICE_UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return f"/static/services/{filename}"


@router.post("/", response_model=ServiceResponse)
def create_service(
        name: str = Form(...),
        description: str = Form(None),
        device_ids: List[int] = Form([]),
        image: UploadFile = File(None),
        db: Session = Depends(get_db)
):

    image_path = save_image(image) if image else None

    new_service = Service(
        name=name,
        description=description,
        image=image_path
    )

    db.add(new_service)
    if device_ids:
        db.query(Device).filter(Device.device_id.in_(device_ids)).update(
            {"service_id": new_service.service_id},
            synchronize_session=False
        )

    db.commit()
    db.refresh(new_service)
    return new_service


@router.get("/", response_model=List[ServiceResponse])
def get_services(db: Session = Depends(get_db)):

    services = db.query(Service) \
        .filter(Service.is_active == True) \
        .options(joinedload(Service.devices)) \
        .all()


    for service in services:
        service.devices = [d for d in service.devices if d.is_active]

    return services


@router.delete("/{service_id}")
def soft_delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.is_active = False

    db.query(Device).filter(Device.service_id == service_id).update({"is_active": False})

    db.commit()
    return {"message": "Service and its devices deactivated successfully"}