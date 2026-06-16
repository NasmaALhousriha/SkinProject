from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.models.notification_model import Notification
from app.models.appointment_model import Appointment, AppointmentTypeEnum
from app.dependencies import get_current_user

from app.schemas import NotificationResponse, RescheduleRequest

router = APIRouter(prefix="/notifications",
                   tags=["Notifications"])



@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.user_id
    ).order_by(Notification.created_at.desc()).all()
    return notifications



# @router.patch("/{notification_id}/read")
# def mark_as_read(
#         notification_id: int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     notification = db.query(Notification).filter(
#         Notification.notification_id == notification_id,
#         Notification.user_id == current_user.user_id
#     ).first()
#
#     if not notification:
#         raise HTTPException(status_code=404, detail="Notification not found")
#
#     notification.is_read = True
#     db.commit()
#     return {"message": "Notification marked as read"}



# @router.patch("/appointments/{appointment_id}/cancel")
# def secretary_cancel_appointment(
#         appointment_id: int,
#         db: Session = Depends(get_db),
# ):
#     appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
#
#     if not appointment:
#         raise HTTPException(status_code=404, detail="الموعد غير موجود")
#
#     appointment.status = AppointmentTypeEnum.CANCELLED
#
#
#     new_notification = Notification(
#         user_id=appointment.patient.user.user_id,
#         title="تنبيه: إلغاء موعد",
#         message=f"تم إلغاء موعدك المحجوز بتاريخ {appointment.date_time.strftime('%Y-%m-%d')}. يمكنك إعادة الجدولة الآن.",
#         is_read=False,
#
#     )
#
#     db.add(new_notification)
#     db.commit()
#
#     return {"message": "تم إلغاء الموعد وإشعار المريض بنجاح"}
#

@router.patch("/appointments/{appointment_id}/reschedule")
def reschedule_appointment(
        appointment_id: int,
        data: RescheduleRequest,
        db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    old_datetime = appointment.date_time
    old_date = old_datetime.date()
    old_time = old_datetime.time()

    date_changed = data.new_date is not None and data.new_date != old_date
    time_changed = data.new_time is not None and data.new_time != old_time

    # 3. بناء الرسالة الذكية
    if date_changed and time_changed:
        message = (f"تم تغيير موعدك بالكامل: من يوم {old_date} الساعة {old_time.strftime('%H:%M')} "
                   f"إلى يوم {data.new_date} الساعة {data.new_time.strftime('%H:%M')}.")

    elif date_changed:
        message = (f"تم تغيير تاريخ موعدك من {old_date} إلى {data.new_date} "
                   f"(الوقت لا يزال كما هو في تمام الساعة {old_time.strftime('%H:%M')}).")

    elif time_changed:
        message = (f"تم تغيير وقت موعدك في يوم {old_date} من الساعة {old_time.strftime('%H:%M')} "
                   f"إلى الساعة {data.new_time.strftime('%H:%M')}.")

    else:
        return {"message": "لا يوجد تغيير في البيانات"}

    updated_date = data.new_date if data.new_date else old_date
    updated_time = data.new_time if data.new_time else old_time
    appointment.date_time = datetime.combine(updated_date, updated_time)

    notif = Notification(
        user_id=appointment.patient.user.user_id,
        title="تحديث في الموعد",
        message=message,
        is_read=False,

    )

    db.add(notif)
    db.commit()

    return {"message": "تم تحديث الموعد وإرسال الإشعار بنجاح", "details": message}