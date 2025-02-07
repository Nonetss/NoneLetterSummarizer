import os

from dotenv import load_dotenv

load_dotenv()


# Configuración de Proton Bridge (IMAP)
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = os.getenv("IMAP_PORT")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
FOLDER = os.getenv("FOLDER")

DATABASE_URL = os.getenv("DATABASE_URL")
