from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user
from app.models.patient_model import PatientProfile
from app.models.user_model import User, UserRoleEnum
from  app.schemas import PatientUpdate, UpdatePatientResponse

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.put("/edit/{patient_id}", response_model=UpdatePatientResponse)
def edit_patient(
    patient_id: int,
    data: PatientUpdate = Depends(PatientUpdate.as_form),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    if current_user.role != UserRoleEnum.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can update this profile"
        )


    patient = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    user = db.query(User).filter(User.user_id == patient.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # تحديث بيانات المستخدم
    if data.name:
        user.name = data.name
    if data.phone:
        user.phone = data.phone


    # تحديث بيانات المريض
    if data.date_of_birth:
        patient.date_of_birth = data.date_of_birth
    if data.gender:
        patient.gender = data.gender
    if data.medical_history:
        patient.medical_history = data.medical_history

    db.commit()
    db.refresh(patient)

    return UpdatePatientResponse(
        message="Patient updated successfully",
        patient_id=patient.patient_id,
        user_id=patient.user_id
    )