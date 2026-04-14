from app.database import get_db
from app.models.user_model import User, UserRoleEnum
from app.models.patient_model import PatientProfile
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.service_model import Service


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_user(db: Session):
    existing = db.query(User).filter(User.email=="nasma@gmail.com").first()
    if existing:
        return
    hashed_password = pwd_context.hash("123")

    user = User(
        name="nasma",
        email="nasma@gmail.com",
        password_hash=hashed_password,
        role=UserRoleEnum.PATIENT
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    patient = PatientProfile(user_id=user.user_id)
    db.add(patient)
    db.commit()
    db.refresh(patient)

    print(f"Created patient_id={patient.patient_id}, user_id={user.user_id}")


def seed_services(db: Session):
    static_services = [
        {
            "name": "Medical Dermatology",
        },
        {
            "name": "Cosmetic Treatments",
        },
        {
            "name": "Laser Therapy",
        },
        {
            "name": "Cancer Screening",
        }
    ]

    print("Checking services...")

    for svc in static_services:
        # نفحص هل الخدمة موجودة مسبقاً؟
        existing_service = db.query(Service).filter(Service.name == svc["name"]).first()

        if not existing_service:
            # إذا غير موجودة، نقوم بإنشائها
            new_service = Service(
                name=svc["name"],
            )
            db.add(new_service)
            print(f"Added service: {svc['name']}")
        else:
            print(f"Service already exists: {svc['name']}")

    db.commit()
    print("Services seeding completed.")

# تشغيل الـ Seeder مباشرة
if __name__ == "__main__":
    from app.database import LocalSession
    with LocalSession() as db:
        seed_user(db)
        seed_services(db)