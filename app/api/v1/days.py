from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.newsletter import Newsletter, NewsletterDia
from app.services.ai.resumen_newsletter import summarize_day

router = APIRouter()


@router.get("/days", response_model=list)
def get_days(db: Session = Depends(get_db)):
    """
    Obtiene todos los registros diarios (NewsletterDia) ordenados por fecha (descendente),
    con el resumen general (si existe) y la lista de newsletters (con sus resúmenes) asociadas.
    """
    days = db.query(NewsletterDia).order_by(NewsletterDia.fecha.desc()).all()
    result = []
    for day in days:
        newsletters = []
        for n in day.newsletters:
            newsletters.append(
                {
                    "id": n.id,
                    "subject": n.subject,
                    "summary": n.summary,
                    "received_at": n.received_at.isoformat(),
                    "author": n.author,
                }
            )
        result.append(
            {
                "id": day.id,
                "fecha": day.fecha.isoformat(),
                "summary": day.summary,
                "newsletters": newsletters,
            }
        )
    return result


@router.get("/days/{day_id}", response_model=dict)
def get_day(day_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un registro diario (NewsletterDia) específico,
    incluyendo la lista completa de newsletters con sus resúmenes.
    """
    day = db.query(NewsletterDia).filter(NewsletterDia.id == day_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Registro diario no encontrado")
    newsletters = []
    for n in day.newsletters:
        newsletters.append(
            {
                "id": n.id,
                "subject": n.subject,
                "body": n.body,
                "summary": n.summary,
                "received_at": n.received_at.isoformat(),
                "author": n.author,
            }
        )
    return {
        "id": day.id,
        "fecha": day.fecha.isoformat(),
        "summary": day.summary,
        "newsletters": newsletters,
    }


@router.post("/days/{day_id}/summarize", response_model=dict)
def generate_day_summary(day_id: int, db: Session = Depends(get_db)):
    """
    Genera (o regenera) el resumen general para un día específico usando la función summarize_day.
    Luego, devuelve el registro diario actualizado con el resumen.
    """
    summary = summarize_day(day_id, db)
    # Reconsultamos el registro diario para devolver la información actualizada.
    day = db.query(NewsletterDia).filter(NewsletterDia.id == day_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Registro diario no encontrado")
    newsletters = []
    for n in day.newsletters:
        newsletters.append(
            {
                "id": n.id,
                "subject": n.subject,
                "summary": n.summary,
                "received_at": n.received_at.isoformat(),
                "author": n.author,
            }
        )
    return {
        "id": day.id,
        "fecha": day.fecha.isoformat(),
        "summary": day.summary,
        "newsletters": newsletters,
    }
