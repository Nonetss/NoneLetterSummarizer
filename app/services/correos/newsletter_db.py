from datetime import datetime, time

from app.core.database import SessionLocal
from app.models.newsletter import Newsletter, NewsletterDia


def save_newsletter_to_db(
    email_id: str, subject: str, body: str, received_at: datetime, summary: str
) -> Newsletter:
    """
    Guarda la newsletter en la tabla 'newsletters'. Si ya existe, devuelve el registro existente.
    """
    db = SessionLocal()
    existing = db.query(Newsletter).filter(Newsletter.email_id == email_id).first()
    if existing:
        db.close()
        return existing

    new_newsletter = Newsletter(
        email_id=email_id,
        subject=subject,
        body=body,
        received_at=received_at,
        summary=summary,
    )
    db.add(new_newsletter)
    db.commit()
    db.refresh(new_newsletter)
    db.close()
    return new_newsletter


def update_newsletter_summary(email_id: str, summary: str):
    """
    Actualiza el campo 'resumen' de la newsletter identificada por email_id.
    """
    db = SessionLocal()
    try:
        newsletter = (
            db.query(Newsletter).filter(Newsletter.email_id == email_id).first()
        )
        if newsletter:
            newsletter.resumen = summary
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def add_newsletter_to_day(newsletter_obj: Newsletter, received_at: datetime):
    """
    Agrega la newsletter al registro del día correspondiente en la tabla 'newsletters_dias'.
    Si no existe un registro para ese día, lo crea.
    """
    db = SessionLocal()
    # Definir el inicio del día (medianoche) a partir de la fecha del email
    day_start = datetime.combine(received_at.date(), time.min)

    # Buscar si ya existe un registro de día con esa fecha
    day_record = (
        db.query(NewsletterDia).filter(NewsletterDia.fecha == day_start).first()
    )
    if not day_record:
        day_record = NewsletterDia(fecha=day_start, summary=None)
        db.add(day_record)
        db.commit()
        db.refresh(day_record)

    # Agregar la newsletter a la relación many-to-many, si aún no está asociada
    if newsletter_obj not in day_record.newsletters:
        day_record.newsletters.append(newsletter_obj)
        db.commit()
    db.close()
