import email
import imaplib
import logging
import os
from email.header import decode_header
from typing import Optional

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


# Iniciamos sesión en el correo
def inicio_sesion():
    mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
    mail.login(USERNAME, PASSWORD)
    return mail
