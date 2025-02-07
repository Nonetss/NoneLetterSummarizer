from fastapi import FastAPI

from app.api.v1.get_newsletter import router as correos_router
from app.core.database import Base, engine

app = FastAPI()

# Crear la base de datos y las tablas al iniciar la app
print("🔄 Verificando y creando tablas si no existen...")
Base.metadata.create_all(bind=engine)

# Registrar los endpoints de correos
app.include_router(correos_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "API de Correos funcionando 🚀"}
