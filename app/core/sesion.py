import imaplib
import logging

from app.core.config import IMAP_PORT, IMAP_SERVER, PASSWORD, USERNAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Iniciamos sesión en el correo
def inicio_sesion():
    mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
    mail.login(USERNAME, PASSWORD)
    return mail
