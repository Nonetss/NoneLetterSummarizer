# Usa una imagen base de Python 3.11 (por ejemplo)
FROM python:3.11

# Crea un directorio de trabajo
WORKDIR /app

# Copia los requerimientos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código (incl. app/, newsletters.db si quisieras copiarlo también)
COPY . .

# Expón el puerto 8080 (FastAPI por defecto)
EXPOSE 8080

# Comando para iniciar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
