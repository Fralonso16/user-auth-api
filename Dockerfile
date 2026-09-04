# Imagen base: Python 3.12 en su version "slim"
FROM python:3.12-slim

# Carpeta de trabajo DENTRO del contenedor
WORKDIR /app

# Copiamos primero requirements.txt para aprovechar el cacheo de capas de Docker
COPY requirements.txt .

# Instalamos las dependencias dentro del contenedor
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del codigo del proyecto
COPY . .

# Documenta que el contenedor escucha en el puerto 8000
EXPOSE 8000

# Comando que arranca la API al iniciar el contenedor
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]