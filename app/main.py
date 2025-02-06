# app/main.py
import email
import imaplib
import logging
import os
from email.header import decode_header
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

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

app = FastAPI(title="API para Leer Correos de Proton Bridge")


def listar_carpetas():
    """
    Conecta al servidor IMAP y devuelve una lista de todas las carpetas disponibles.
    """
    try:
        logger.info("Conectando al servidor IMAP para listar carpetas...")
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)

        # Listar todas las carpetas
        status, mailboxes = mail.list()
        if status != "OK":
            raise Exception("No se pudieron listar las carpetas.")

        # Procesar la lista de carpetas
        carpetas = []
        for mailbox in mailboxes:
            # La respuesta de mail.list() puede tener el siguiente formato:
            # b'(\\HasNoChildren) "/" "INBOX"'
            parts = mailbox.decode().split(' "/" ')
            if len(parts) == 2:
                carpeta = parts[1].strip('"')
                carpetas.append(carpeta)

        mail.logout()
        logger.info("Desconectado del servidor IMAP después de listar carpetas.")
        return carpetas

    except imaplib.IMAP4.error as e:
        logger.error(f"Error de IMAP: {e}")
        raise HTTPException(
            status_code=500, detail="Error al conectar con el servidor IMAP."
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def obtener_correos_no_leidos(
    cantidad: Optional[int] = None, folder: Optional[str] = FOLDER
):
    """
    Conecta a Proton Bridge mediante IMAP y devuelve una lista
    con los correos no leídos (asunto y cuerpo) de la carpeta especificada.
    Si 'cantidad' es proporcionada, devuelve solo los últimos 'cantidad' correos no leídos.
    """
    try:
        logger.info("Conectando al servidor IMAP...")
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)
        logger.info(f"Seleccionando la carpeta: {folder}")
        status, _ = mail.select(folder)
        if status != "OK":
            raise Exception(f"No se pudo seleccionar la carpeta: {folder}")

        # Buscar solo los correos no leídos
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            raise Exception("No se pudieron buscar los correos no leídos.")

        mail_ids = messages[0].split()
        total_correos = len(mail_ids)
        logger.info(f"Total de correos no leídos en '{folder}': {total_correos}")

        # Si 'cantidad' está especificada, obtener solo los últimos 'cantidad' correos
        if cantidad is not None and cantidad > 0:
            ultimos_ids = mail_ids[-cantidad:]
        else:
            ultimos_ids = mail_ids

        correos = []
        for msg_id in ultimos_ids:
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
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")

                    # Obtener el cuerpo del correo
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if (
                                content_type == "text/plain"
                                and "attachment" not in content_disposition
                            ):
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    body = part.get_payload(decode=True).decode(
                                        "utf-8", errors="replace"
                                    )
                                break
                            elif (
                                content_type == "text/html"
                                and "attachment" not in content_disposition
                            ):
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    body = part.get_payload(decode=True).decode(
                                        "utf-8", errors="replace"
                                    )
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            body = msg.get_payload(decode=True).decode(
                                "utf-8", errors="replace"
                            )

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


@app.get("/carpetas/", response_model=List[str])
async def listar_carpetas_endpoint():
    """
    Endpoint para listar todas las carpetas disponibles en el servidor IMAP.
    """
    return listar_carpetas()


@app.get("/correos/no_leidos/", response_model=List[dict])
async def obtener_correos_no_leidos_endpoint(cantidad: Optional[int] = None):
    """
    Endpoint para obtener todos los correos no leídos de la carpeta 'Newsletter'.
    Si 'cantidad' es proporcionada, devuelve solo los últimos 'cantidad' correos no leídos.
    """
    return obtener_correos_no_leidos(cantidad=cantidad)
