import email
import imaplib
import logging
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.core.config import FOLDER
from app.core.sesion import inicio_sesion
from app.services.correos.newsletter_db import (
    add_newsletter_to_day,
    save_newsletter_to_db,
)

# Configura el nivel de logs para ver detalles en caso de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def newsletter_no_leidas():
    """
    Conecta a Proton Bridge mediante IMAP, procesa los correos no leídos y
    guarda su contenido en la base de datos usando las nuevas tablas (Newsletter y NewsletterDia).
    Devuelve una lista con los correos procesados.
    """
    try:
        mail = inicio_sesion()
        mail.select(mailbox=FOLDER)

        status, ids = mail.search(None, "UNSEEN")
        if status != "OK":
            raise Exception("No se pudieron buscar los correos no leídos.")

        newsletter_ids = ids[0].split()
        total_correos = len(newsletter_ids)
        logger.info(f"Total de correos no leídos son: {total_correos}")

        newsletters_list = []
        for msg_id in newsletter_ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                logger.warning(
                    f"No se pudo obtener el correo con ID {msg_id.decode()}."
                )
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Decodificar el asunto
                    subject_raw = msg.get("Subject", "Sin Asunto")
                    subject_tuple = decode_header(subject_raw)[0]
                    subject = subject_tuple[0]
                    encoding = subject_tuple[1]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="replace")

                    # Obtener el cuerpo del correo
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            # Procesar solo partes de texto que no sean adjuntos
                            if "attachment" not in content_disposition:
                                if content_type == "text/plain":
                                    try:
                                        body = part.get_payload(decode=True).decode(
                                            part.get_content_charset() or "utf-8",
                                            errors="replace",
                                        )
                                    except Exception as ex:
                                        logger.error(
                                            f"Error decodificando texto plano: {ex}"
                                        )
                                    break  # Preferimos texto plano si está disponible
                                elif content_type == "text/html":
                                    try:
                                        html_content = part.get_payload(
                                            decode=True
                                        ).decode(
                                            part.get_content_charset() or "utf-8",
                                            errors="replace",
                                        )
                                    except Exception as ex:
                                        logger.error(f"Error decodificando HTML: {ex}")
                                        html_content = ""
                                    soup = BeautifulSoup(html_content, "html.parser")
                                    body = soup.get_text(separator="\n", strip=True)
                                    break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8", errors="replace"
                            )
                        except Exception as ex:
                            logger.error(f"Error decodificando payload: {ex}")
                            body = ""
                        if "<html" in body.lower():
                            soup = BeautifulSoup(body, "html.parser")
                            body = soup.get_text(separator="\n", strip=True)

                    # Obtener la fecha en que se recibió el email (a partir del header "Date")
                    date_header = msg.get("Date")
                    if date_header:
                        try:
                            received_at = parsedate_to_datetime(date_header)
                        except Exception as ex:
                            logger.error(f"Error parseando fecha del email: {ex}")
                            received_at = datetime.utcnow()
                    else:
                        received_at = datetime.utcnow()

                    email_id = msg_id.decode()

                    # Guardar la newsletter en la base de datos (nueva tabla)
                    newsletter_obj = save_newsletter_to_db(
                        email_id, subject, body, received_at
                    )

                    # Agregar la newsletter al resumen diario (NewsletterDia)
                    add_newsletter_to_day(newsletter_obj, received_at)

                    newsletters_list.append(
                        {
                            "id": email_id,
                            "subject": subject,
                            "body": body.strip(),
                            "received_at": received_at.isoformat(),
                        }
                    )

        mail.logout()
        logger.info("Desconectado del servidor IMAP.")
        return newsletters_list

    except imaplib.IMAP4.error as e:
        logger.error(f"Error de IMAP: {e}")
        raise HTTPException(
            status_code=500, detail="Error al conectar con el servidor IMAP."
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Llamada de ejemplo
if __name__ == "__main__":
    newsletters = newsletter_no_leidas()
    for n in newsletters:
        print(f"Asunto: {n['subject']}")
        print(f"Cuerpo:\n{n['body']}\n{'-'*40}")
