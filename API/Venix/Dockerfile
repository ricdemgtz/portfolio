# Usa una imagen base de Python oficial (versión 3.10 más ligera)
FROM python:3.10-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos al contenedor
COPY requirements.txt .

# Instala las dependencias de Python.
# --no-cache-dir para no guardar la caché de pip, reduciendo el tamaño de la imagen.
# -r requirements.txt para instalar todas las dependencias listadas.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de tu aplicación al directorio de trabajo en el contenedor
COPY . .

# Expón el puerto 5000, que es donde tu aplicación Flask escuchará.
EXPOSE 5000

# Define variables de entorno necesarias para Flask.
# FLASK_APP apunta a tu archivo principal.
# FLASK_RUN_HOST=0.0.0.0 hace que Flask escuche en todas las interfaces, necesario en Docker.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando por defecto para ejecutar la aplicación cuando el contenedor se inicie.
# Usa 'flask run' que es el comando recomendado por Flask para desarrollo.
CMD ["flask", "run"]
