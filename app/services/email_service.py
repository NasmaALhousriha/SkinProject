import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_path = os.path.join(BASE_DIR, "..", "templates")

env = Environment(loader=FileSystemLoader(templates_path))


class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MAIL_FROM: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_FROM,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_appointment_confirmation_email(
    patient_name: str,
    patient_email: str,
    doctor_name: str,
    appointment_date: datetime,
    appointment_time: str
):
    template = env.get_template("appointment_confirmation.html")

    html_content = template.render(
        patient_name=patient_name,
        doctor_name=doctor_name,
        date=appointment_date.strftime('%Y-%m-%d'),
        time=appointment_time
    )

    message = MessageSchema(
        subject="تأكيد موعدك الطبي",
        recipients=[patient_email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_appointment_reminder_email(
    patient_name: str,
    patient_email: str,
    doctor_name: str,
    appointment_date: datetime,
    appointment_time: str
):
    template = env.get_template("appointment_reminder.html")

    html_content = template.render(
        patient_name=patient_name,
        doctor_name=doctor_name,
        date=appointment_date.strftime('%Y-%m-%d'),
        time=appointment_time
    )

    message = MessageSchema(
        subject="تذكير: موعدك الطبي غداً",
        recipients=[patient_email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)