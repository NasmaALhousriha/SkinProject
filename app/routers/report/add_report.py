from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
import shutil
import os
import uuid

from app.database import get_db
from app.dependencies import get_current_user
from app.models.report_model import Report
from app.models.patient_model import PatientProfile
from app.models.doctor_model import DoctorProfile
from app.models.user_model import UserRoleEnum

class ReportCreate(BaseModel):
    content: str
    doctor_id: int
    patient_id: int
    audio: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        content: str = Form(...),
        doctor_id: int = Form(...),
        patient_id: int = Form(...),
        audio: UploadFile = File(None),
    ):
        return cls(
            content=content,
            doctor_id=doctor_id,
            patient_id=patient_id,
            audio=audio,
        )

class ReportResponse(BaseModel):
    report_id: int
    created_at: datetime
    audio_url: Optional[str] = None
    content: str
    doctor_id: int
    patient_id: int

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

AUDIODIR = "static/reports/audio/"
os.makedirs(AUDIODIR, exist_ok=True)

@router.post("/add", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def add_report(
        report_data: ReportCreate = Depends(ReportCreate.as_form),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    if current_user.role != UserRoleEnum.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can create reports")
    doctor_check = db.query(DoctorProfile).filter(DoctorProfile.doctor_id == report_data.doctor_id).first()
    if not doctor_check:
        raise HTTPException(status_code=404, detail="Doctor not found")

    patient_check = db.query(PatientProfile).filter(PatientProfile.patient_id == report_data.patient_id).first()
    if not patient_check:
        raise HTTPException(status_code=404, detail="Patient not found")
    audio_path = None

    if report_data.audio:
        file_extension = report_data.audio.filename.split(".")[-1].lower()
        ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "aac"}

        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid audio type")

        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_location = os.path.join(AUDIODIR, unique_filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(report_data.audio.file, buffer)

        audio_path = f"/static/reports/audio/{unique_filename}"

        new_report = Report(
            content=report_data.content,
            doctor_id=report_data.doctor_id,
            patient_id=report_data.patient_id,
            audio_url=audio_path
        )

        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return new_report