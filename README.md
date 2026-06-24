# Backend Django – API con JWT, PostgreSQL y AWS S3

Este proyecto es un backend construido con **Django** y **Django REST Framework**, usando autenticación **JWT**, manejo de variables de entorno con **python-decouple**, base de datos **PostgreSQL**, soporte opcional para **AWS S3** y configuración de **CORS** para permitir interacción con clientes externos.

---

## Tecnologías principales

- Django 5
- Django REST Framework
- SimpleJWT (autenticación)
- PostgreSQL
- python-decouple
- django-storages + boto3 (S3)
- corsheaders

---

## Requisitos previos

- Python 3.10+
- PostgreSQL (local o remoto)
- pip y virtualenv
- Git

---

## Instalación

### Clonar el repositorio:

```bash
git clone <url-del-repo>
cd <carpeta-del-proyecto>
Crear entorno virtual:

python -m venv venv
source venv/bin/activate       # Linux / Mac
venv\Scripts\activate          # Windows
```

### Instalar dependencias:

```bash
pip install -r requirements.txt
```

### Configuración del archivo .env
Crear un archivo .env en la raíz del proyecto con:

env
```bash
# General
SECRET_KEY=tu_clave_secreta_super_larga
DEBUG=True
ALLOWED_HOSTS=*

# Base de datos (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=5432

# CORS
CORS_ALLOW_ALL=True
CORS_ALLOWED_ORIGINS=

# AWS S3 (opcional)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=
```

Configurar PostgreSQL (solo la primera vez)

### Migraciones y ejecución
Aplicar migraciones:

```bash
python manage.py migrate
```
### Iniciar servidor:

```bash
python manage.py runserver
```

API disponible en:

http://127.0.0.1:8000/

### Autenticación JWT
El backend usa SimpleJWT. Endpoints estándar:

```bash
POST /api/token/           # genera access + refresh token
POST /api/token/refresh/   # renueva access token
Enviar token en las peticiones:
```

Authorization: Bearer <tu-token>


### Almacenamiento de archivos (AWS S3)
Para activar S3, cambiar en .env:

```bash
USE_S3=True
```

### Instalar dependencias (si no están):
```bash
pip install django-storages boto3
```
Django comenzará a guardar archivos en el bucket indicado.

### CORS
Desarrollo:

```bash
CORS_ALLOW_ALL=True
```
Producción:
```bash
CORS_ALLOW_ALL=False
CORS_ALLOWED_ORIGINS=https://tudominio.com
```

## Comandos útiles
```bash
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Recomendaciones de desarrollo
Mantener .env fuera del repositorio.

Activar S3 solo en producción.

Desactivar DEBUG al desplegar.

Usar ALLOWED_HOSTS configurado correctamente en producción.

