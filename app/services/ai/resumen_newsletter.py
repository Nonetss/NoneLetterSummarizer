import logging

from google import genai
from sqlalchemy.orm import Session

from app.core.config import GEMINI_KEY, MODEL_GEMINI
from app.core.database import SessionLocal
from app.models.newsletter import Newsletter, NewsletterDia

# Configurar el cliente de Gemini con la API Key
client = genai.Client(api_key=GEMINI_KEY)
logger = logging.getLogger(__name__)


def summarize_newsletter(content: str) -> str:
    """
    Genera un resumen usando Gemini a partir del contenido proporcionado.

    :param content: Texto completo de la newsletter.
    :return: Resumen generado o un mensaje de error.
    """
    try:
        prompt = f"Resumir el siguiente texto en menos de 100 palabras de manera clara y concisa:\n{content}"
        summary_response = client.models.generate_content(
            model=MODEL_GEMINI, contents=prompt
        )
        summary_text = summary_response.text
        logger.info(f"Resumen generado: {summary_text}")
        return summary_text
    except Exception as e:
        logger.error(f"Error generando resumen: {e}")
        return "Error al generar el resumen."


def summarize_day(day_id: int, db: Session) -> str:
    """
    Busca el registro diario en la BD, concatena el contenido de todas las newsletters asociadas a ese día,
    usa Gemini para generar un resumen del día y lo guarda en la BD.

    :param day_id: ID del registro diario (NewsletterDia).
    :param db: Sesión de la base de datos.
    :return: Resumen generado o un mensaje de error.
    """
    # Suponiendo que el modelo NewsletterDia tiene la relación "newsletters"
    day_record = db.query(NewsletterDia).filter(NewsletterDia.id == day_id).first()
    if not day_record:
        logger.error(f"Registro diario con ID {day_id} no encontrado.")
        return "Registro diario no encontrado."
    try:
        combined_content = " ".join(
            [
                newsletter.body
                for newsletter in day_record.newsletters
                if newsletter.body
            ]
        )
        if not combined_content:
            logger.warning(f"No hay contenido en las newsletters para el día {day_id}.")
            return "No hay contenido para resumir en este día."

        prompt = (
            f"Resumir el siguiente conjunto de newsletters en menos de 100 palabras de manera clara y concisa:\n"
            f"{combined_content}"
        )
        summary_response = client.models.generate_content(
            model=MODEL_GEMINI, contents=prompt
        )
        summary_text = summary_response.text

        day_record.resumen = summary_text
        db.commit()
        logger.info(f"Resumen del día {day_id} guardado en la BD: {summary_text}")
        return summary_text
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error en la generación del resumen diario para el día {day_id}: {e}"
        )
        return "Error al generar el resumen diario."
