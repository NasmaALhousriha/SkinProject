from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.patient_model import PatientProfile
from app.models.user_model import User, UserRoleEnum
from app.schemas import PatientUpdateRequest, PatientUpdateResponse

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.patch("/me")
def update_patient(
    data: PatientUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    patient = db.query(PatientProfile).filter(
        PatientProfile.user_id == current_user.user_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404)

    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        current_user.name = update_data.pop("name")

    if "phone" in update_data:
        current_user.phone = update_data.pop("phone")

    if "email" in update_data:
        current_user.email = update_data.pop("email")


    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(current_user)
    db.refresh(patient)

    return {
        "message": "Patient updated successfully",
        "patient_id": patient.patient_id,
        "user_id": current_user.user_id,
        "name": current_user.name,
        "phone": current_user.phone,
        "email": current_user.email
    }