import os
import shutil
from uuid import uuid4
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.specialist_model import Specialist
from app.models.user_model import User
from app.dependencies import get_current_secretary


class SpecialistCreate(BaseModel):
    name: str
    position: Optional[str] = None
    years_of_experience: Optional[int] = None
    photo: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        position: Optional[str] = Form(None),
        years_of_experience: Optional[int] = Form(None),
        photo: UploadFile = File(None),
    ):
        return cls(
            name=name,
            position=position,
            years_of_experience=years_of_experience,
            photo=photo,
        )


class SpecialistResponse(BaseModel):
    specialist_id: int
    name: str
    position: Optional[str] = None
    years_of_experience: Optional[int] = None
    photo: Optional[str] = None

    class Config:
        from_attributes = True


router = APIRouter(
    prefix="/specialists",
    tags=["Specialists"]
)

UPLOAD_DIR = "static/specialist_photos/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/add", response_model=SpecialistResponse, status_code=status.HTTP_201_CREATED)
def add_specialist(
    specialist_data: SpecialistCreate = Depends(SpecialistCreate.as_form),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary)
):
   
    photo_path = None
    
    if specialist_data.photo:
        try:
            file_extension = specialist_data.photo.filename.split(".")[-1].lower()
            ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
            
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Invalid image type. Only jpg, jpeg, png, webp are allowed")
            
            unique_filename = f"{uuid4()}.{file_extension}"
            file_location = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(specialist_data.photo.file, buffer)
            
            photo_path = f"/static/specialist_photos/{unique_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving photo: {str(e)}")
    
    # إنشاء الاختصاصي
    new_specialist = Specialist(
        name=specialist_data.name,
        position=specialist_data.position,
        years_of_experience=specialist_data.years_of_experience,
        photo=photo_path
    )
    
    db.add(new_specialist)
    db.commit()
    db.refresh(new_specialist)
    
    return new_specialist


@router.get("/", response_model=list[SpecialistResponse])
def get_all_specialists(db: Session = Depends(get_db)):

    specialists = db.query(Specialist).all()
    return specialists


@router.get("/{specialist_id}", response_model=SpecialistResponse)
def get_specialist(specialist_id: int, db: Session = Depends(get_db)):
   
    specialist = db.query(Specialist).filter(Specialist.specialist_id == specialist_id).first()
    
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    
    return specialist


@router.put("/{specialist_id}", response_model=SpecialistResponse)
def update_specialist(
    specialist_id: int,
    specialist_data: SpecialistCreate = Depends(SpecialistCreate.as_form),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary)
):
    
    specialist = db.query(Specialist).filter(Specialist.specialist_id == specialist_id).first()
    
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    
    
    specialist.name = specialist_data.name
    specialist.position = specialist_data.position
    specialist.years_of_experience = specialist_data.years_of_experience
    
    
    if specialist_data.photo:
        try:
           
            if specialist.photo:
                old_file = specialist.photo.lstrip("/")
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            file_extension = specialist_data.photo.filename.split(".")[-1].lower()
            ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
            
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Invalid image type. Only jpg, jpeg, png, webp are allowed")
            
            unique_filename = f"{uuid4()}.{file_extension}"
            file_location = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(specialist_data.photo.file, buffer)
            
            specialist.photo = f"/static/specialist_photos/{unique_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating photo: {str(e)}")
    
    db.commit()
    db.refresh(specialist)
    
    return specialist




