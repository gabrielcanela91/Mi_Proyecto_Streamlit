# Imagen base con Python
FROM python:3.13.2

# Carpeta dentro del contenedor
WORKDIR /login

# Copia todo el contenido de tu carpeta al contenedor
COPY . /login

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar tu app
CMD ["streamlit", "run", "login.py"]

