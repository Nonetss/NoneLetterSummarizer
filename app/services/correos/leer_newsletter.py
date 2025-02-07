import email
import imaplib
import logging
import os
from email.header import decode_header

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import HTTPException

from app.core.sesion import inicio_sesion

load_dotenv()

# Configura el nivel de logs para ver detalles en caso de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Proton Bridge (IMAP)
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = os.getenv("IMAP_PORT")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
FOLDER = os.getenv("FOLDER")


def newsletter_no_leidas():
    """
    Conecta a Proton Bridge mediante IMAP y devuelve una lista
    con los correos no leídos (asunto y cuerpo) de la carpeta especificada.
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

        correos = []
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

                    # Decodificar el Asunto
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
                                    # Extraer solo el texto del HTML
                                    soup = BeautifulSoup(html_content, "html.parser")
                                    body = soup.get_text(separator="\n", strip=True)
                                    break
                    else:
                        # En caso de que no sea multipart
                        try:
                            body = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or "utf-8", errors="replace"
                            )
                        except Exception as ex:
                            logger.error(f"Error decodificando payload: {ex}")
                            body = ""

                        # Si es HTML, lo procesamos
                        if "<html" in body.lower():
                            soup = BeautifulSoup(body, "html.parser")
                            body = soup.get_text(separator="\n", strip=True)

                    # Agregar el correo a la lista de resultados
                    correos.append(
                        {
                            "id": msg_id.decode(),
                            "subject": subject,
                            "body": body.strip(),
                        }
                    )

        mail.logout()
        logger.info("Desconectado del servidor IMAP.")
        return correos

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
    correos = newsletter_no_leidas()
    for correo in correos:
        print(f"Asunto: {correo['subject']}")
        print(f"Cuerpo:\n{correo['body']}\n{'-'*40}")
