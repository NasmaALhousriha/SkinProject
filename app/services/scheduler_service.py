from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
from app.models.appointment_model import Appointment, AppointmentTypeEnum
from app.services.email_service import send_appointment_reminder_email
from app.database import LocalSession


scheduler = BackgroundScheduler()


def check_and_send_reminders():
    db = LocalSession()
    try:
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        appointments = db.query(Appointment).filter(
            Appointment.date_time >= now,
            Appointment.date_time <= tomorrow,
            Appointment.status == AppointmentTypeEnum.PENDING
        ).all()
        
        for appointment in appointments:
            if not hasattr(appointment, 'reminder_sent') or not appointment.reminder_sent:
                try:
                    patient = appointment.patient
                    doctor = appointment.doctor
                    
                    if patient and patient.user and doctor and doctor.user:
                        asyncio.run(send_appointment_reminder_email(
                            patient_name=patient.user.name,
                            patient_email=patient.user.email,
                            doctor_name=doctor.user.name,
                            appointment_date=appointment.date_time,
                            appointment_time=appointment.date_time.strftime('%H:%M')
                        ))
                        
                        # حدّث الإشعار كمرسل (إذا كان هناك حقل)
                        if hasattr(appointment, 'reminder_sent'):
                            appointment.reminder_sent = True
                            db.commit()
                            
                except Exception as e:
                    print(f"خطأ في إرسال التذكير للتعيين {appointment.appointment_id}: {str(e)}")
                    
    except Exception as e:
        print(f"خطأ في فحص التعييناتللتذكيرات: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            check_and_send_reminders,
            trigger=IntervalTrigger(hours=1),
            id='appointment_reminder_job',
            name='Check and send appointment reminders',
            replace_existing=True
        )
        scheduler.start()
        print("✓ تم بدء جدولة التذكيرات")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("✓ تم إيقاف جدولة التذكيرات")

