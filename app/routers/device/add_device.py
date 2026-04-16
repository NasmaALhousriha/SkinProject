import shutil
import os
import uuid
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.device_model import Device
from app.models.service_model import Service
from app.models.user_model import UserRoleEnum
from app.dependencies import get_current_user


class DeviceCreate(BaseModel):
    name: str
    service_id: int
    description: Optional[str] = None
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., description="اسم الجهاز"),
        service_id: int = Form(..., description="ID الخدمة التي يتبع لها الجهاز"),
        description: str = Form(None),
        image: UploadFile = File(None),
    ):
        return cls(
            name=name,
            service_id=service_id,
            description=description,
            image=image,
        )


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

@router.post("/add", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def add_device(
        device_data: DeviceCreate = Depends(DeviceCreate.as_form),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    if current_user.role != UserRoleEnum.SECRETARY:
        raise HTTPException(status_code=403, detail="Only Secretaries can add devices")
    # اول شي بدي اتحقق اذا الخدمة موجودة مشان ضيف جهاز
    service_check = db.query(Service).filter(Service.service_id == device_data.service_id).first()
    if not service_check:
        raise HTTPException(status_code=404, detail="Service ID not found")


    image_path = None
    if device_data.image:
        file_extension = device_data.image.filename.split(".")[-1].lower()
        ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid image type")

        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_location = os.path.join(IMAGEDIR, unique_filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(device_data.image.file, buffer)

        image_path = f"/static/devices/{unique_filename}"
    new_device = Device(
        name=device_data.name,
        service_id=device_data.service_id,
        description=device_data.description,
        image=image_path
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device
