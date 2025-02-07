from fastapi import APIRouter

from app.services.correos.newsletter_mail import newsletter_no_leidas

router = APIRouter()


@router.get("/newsletter/")
def get_newsletter():

    respuesta = newsletter_no_leidas()

    return respuesta
