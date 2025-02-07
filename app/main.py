from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.days import router as days_router
from app.api.v1.get_newsletter import router as correos_router
from app.core.database import Base, engine

app = FastAPI()

# Permitir todos los orígenes
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
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
