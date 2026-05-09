import os
import uuid
import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.device_model import Device
from app.models.service_model import Service
from app.models.specialist_model import Specialist
from app.models.user_model import UserRoleEnum
from app.dependencies import get_current_user
from app.schemas import DeviceResponse

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

IMAGEDIR = "static/devices/"
os.makedirs(IMAGEDIR, exist_ok=True)


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    name: str = Form(...),
    # service_id: int = Form(...),
    # specialist_id: int = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != UserRoleEnum.SECRETARY:
        raise HTTPException(
            status_code=403,
            detail="Only Secretaries can add devices"
        )

    # # service = db.query(Service).filter(Service.service_id == service_id).first()
    # if not service:
    #     raise HTTPException(status_code=404, detail="Service not found")

    # specialist = db.query(Specialist).filter(Specialist.specialist_id == specialist_id).first()
    # if not specialist:
    #     raise HTTPException(status_code=404, detail="Specialist not found")

    image_path = None

    if image:
        ext = image.filename.split(".")[-1].lower()
        allowed = {"jpg", "jpeg", "png", "webp"}

        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail="Invalid image type"
            )

        filename = f"{uuid.uuid4()}.{ext}"
        file_location = os.path.join(IMAGEDIR, filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/static/devices/{filename}"

    new_device = Device(
        name=name,
        # service_id=service_id,
        # specialist_id=specialist_id,
        description=description,
        image=image_path
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device

@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    name: str = Form(None),
    # service_id: int = Form(None),
    # specialist_id: int = Form(None),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != UserRoleEnum.SECRETARY:
        raise HTTPException(status_code=403, detail="Only Secretaries can update devices")

    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # if service_id:
    #     service = db.query(Service).filter(Service.service_id == service_id).first()
    #     if not service:
    #         raise HTTPException(status_code=404, detail="Service not found")
    #     device.service_id = service_id
    #
    # if specialist_id:
    #     specialist = db.query(Specialist).filter(Specialist.specialist_id == specialist_id).first()
    #     if not specialist:
    #         raise HTTPException(status_code=404, detail="Specialist not found")
    #     device.specialist_id = specialist_id

    if name:
        device.name = name

    if description:
        device.description = description

    if image:
        ext = image.filename.split(".")[-1].lower()
        allowed = {"jpg", "jpeg", "png", "webp"}

        if ext not in allowed:
            raise HTTPException(status_code=400, detail="Invalid image type")

        if device.image:
            old_path = device.image.replace("/static/devices/", "static/devices/")
            if os.path.exists(old_path):
                os.remove(old_path)

        filename = f"{uuid.uuid4()}.{ext}"
        file_location = os.path.join(IMAGEDIR, filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        device.image = f"/static/devices/{filename}"

    db.commit()
    db.refresh(device)

    return device


@router.delete("/{device_id}", status_code=200)
def delete_device(
        device_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    if current_user.role != UserRoleEnum.SECRETARY:
        raise HTTPException(
            status_code=403,
            detail="Only Secretaries can delete devices"
        )

    device = db.query(Device).filter(Device.device_id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    if device.image:
        image_path = device.image.replace("/static/devices/", "static/devices/")

        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete(device)
    db.commit()

    return {"message": "Device deleted successfully"}


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.is_active = False
    db.commit()
    return {"message": "Device deactivated successfully"}