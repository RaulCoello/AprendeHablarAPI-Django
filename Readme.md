# Guia para el desarrrollo del caso 1

## Creacion y uso del entorno

1. python -m venv venv
2. venv\Scripts\activate
3. pip install --upgrade pip

## Instalacion de Django

1. pip install django psycopg2-binary
2. pip install django-crispy-forms

## Crear proyecto de Django

1. django-admin startproject config
2. cd config

## Crear App principal

1. python manage.py startapp core

> Registrar app en settings.py:

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'core',
]

## Configurar conexion Postgresql

> En settings.py:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': 'gestion_tareas',
'USER': 'gestor',
'PASSWORD': '123456',
'HOST': 'localhost',
'PORT': '5432',
}
}

## Para crear modelos ORM

> EN core/models.py


## Migraciones

1. python manage.py makemigrations
2. python manage.py migrate

## Crear superusuario

1. python manage.py createsuperuser

## Ejecutar servidor

python manage.py runserver

## Registrar modelos en Admin
> EN core/admin.py

> Esto permite ver los modelos en la app web en /

## Vistas Basicas (CRUD con JSON)

> En core/views.py

## URLs

>EN core/urls.py
>En config/urls.py

## Templates 

> Crear carpeta core/templates/core/
> Archivo index.html

## JavaScript + AJAX

> Crear core/static/app.js