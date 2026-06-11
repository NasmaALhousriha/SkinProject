import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.specialist_model import Specialist
from app.models.user_model import User
from app.models.device_model import Device
from app.dependencies import get_current_secretary
from app.schemas import SpecialistResponse

router = APIRouter(
    prefix="/specialists",
    tags=["Specialists"]
)

UPLOAD_DIR = "static/specialist_photos/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_image(image: UploadFile):
    ext = image.filename.split(".")[-1].lower()
    allowed = {"jpg", "jpeg", "png", "webp"}

    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Invalid image type")

    filename = f"{uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/static/specialist_photos/{filename}"


@router.post("/", response_model=SpecialistResponse)
def create_specialist(
    name: str = Form(...),
    position: str = Form(None),
    years_of_experience: int = Form(None),
    device_ids: list[int] = Form([]),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),

):

    photo_path = save_image(photo) if photo else None

    specialist = Specialist(
        name=name,
        position=position,
        years_of_experience=years_of_experience,
        photo=photo_path
    )
    if device_ids:
        devices = db.query(Device).filter(
            Device.device_id.in_(device_ids),
            Device.is_active == True
        ).all()
        specialist.devices = devices

    db.add(specialist)
    db.commit()
    db.refresh(specialist)

    return specialist


@router.get("/", response_model=list[SpecialistResponse])
def get_all_specialists(db: Session = Depends(get_db)):
    return db.query(Specialist).filter(
    Specialist.is_active == True
                          ).all()


@router.get("/{specialist_id}", response_model=SpecialistResponse)
def get_specialist(specialist_id: int, db: Session = Depends(get_db)):

    specialist = db.query(Specialist).filter(
        Specialist.specialist_id == specialist_id
    ).first()

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    return specialist


@router.patch("/{specialist_id}", response_model=SpecialistResponse)
def update_specialist(
    specialist_id: int,
    name: str = Form(None),
    position: str = Form(None),
    years_of_experience: int = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
):

    specialist = db.query(Specialist).filter(
        Specialist.specialist_id == specialist_id
    ).first()

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    if name is not None:
        specialist.name = name

    if position is not None:
        specialist.position = position

    if years_of_experience is not None:
        specialist.years_of_experience = years_of_experience

    if photo:
        if specialist.photo:
            old_path = specialist.photo.lstrip("/")
            if os.path.exists(old_path):
                os.remove(old_path)

        specialist.photo = save_image(photo)

    db.commit()
    db.refresh(specialist)

    return specialist


@router.delete("/{specialist_id}")
def delete_specialist(specialist_id: int,
                      db: Session = Depends(get_db)):
    specialist = db.query(Specialist).filter(Specialist.specialist_id == specialist_id).first()
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    specialist.is_active = False
    db.commit()
    return {"message": "Specialist deactivated successfully"}
