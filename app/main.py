from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.days import router as days_router
from app.api.v1.get_newsletter import router as correos_router
from app.core.database import Base, engine

app = FastAPI()

# Lista de orígenes permitidos (ajusta esto al origen de tu frontend, por ejemplo, http://localhost:3000 si Astro se sirve ahí)
origins = [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    # Agrega otros orígenes si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite peticiones de estos orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Crear la base de datos y las tablas al iniciar la app
print("🔄 Verificando y creando tablas si no existen...")
Base.metadata.create_all(bind=engine)

# Registrar los endpoints de correos
app.include_router(correos_router, prefix="/api/v1")
app.include_router(days_router, prefix="/api/v1", tags=["Days"])


@app.get("/")
def read_root():
    return {"message": "API de Correos funcionando 🚀"}
