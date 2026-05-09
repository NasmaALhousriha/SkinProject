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

    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient