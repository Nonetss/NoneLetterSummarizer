from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ai.resumen_newsletter import summarize_day

router = APIRouter()


@router.post("/summarize/day/{day_id}", response_model=dict)
def summarize_day_endpoint(day_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para generar el resumen de un día específico a partir de sus newsletters.

    - `day_id`: ID del registro diario en la base de datos.
    """
    try:
        resumen = summarize_day(day_id, db)
        if "Error" in resumen:
            raise HTTPException(status_code=500, detail=resumen)

        return {"day_id": day_id, "resumen": resumen}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
