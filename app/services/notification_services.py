from sqlalchemy.orm import Session
from app.models.notification_model import Notification
from app.models.user_model import User, UserRoleEnum
from typing import Optional

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
    ):
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            is_read=False
        )
        db.add(notif)
        db.commit()
        return notif

    @staticmethod
    def notify_all_patients(db_factory, title: str, message: str):
        db = db_factory()
        try:
            patients = db.query(User).filter(User.role == UserRoleEnum.PATIENT).all()
            notifications = [
                Notification(
                    user_id=p.user_id,
                    title=title,
                    message=message,
                    is_read=False
                ) for p in patients
            ]
            db.add_all(notifications)
            db.commit()
        except Exception as e:
            print(f"Error in notify_all_patients: {e}")
        finally:
            db.close()