# Imagen base ligera de Python
FROM python:3.11-slim

# Instala dependencias del sistema necesarias para uvicorn[standard]
RUN apt-get update && apt-get install -y build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo requirements y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia la carpeta app (solo necesario si no usas volumen)
# COPY ./app ./app

# Expone el puerto 8000
EXPOSE 8000

# Ejecuta uvicorn en modo recarga (desarrollo)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
