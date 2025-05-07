# React + Vite

# Despliegue de la Aplicación Pokémon

Este documento describe cómo desplegar la aplicación Pokémon, que consiste en un backend construido con Django REST Framework (Python) y un frontend desarrollado con React (utilizando Vite).

## Estructura del Proyecto


# Despliegue de la Aplicación Pokémon

Este documento describe cómo desplegar la aplicación Pokémon, que consiste en un backend construido con Django REST Framework (Python) y un frontend desarrollado con React (utilizando Vite).

## Estructura del Proyecto

La estructura general del proyecto es la siguiente:

```pokemon-app/
├── backend/         # Proyecto Django REST Framework
│   ├── pokemon-app 
│   │   ├── init.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── pokemon-app/ 
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ...
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
└── frontend/        # Proyecto React con Vite
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── components/
│   ├── hooks/
│   ├── assets/
│   └── ...
├── public/
├── index.html
├── vite.config.js
├── package.json
├── yarn.lock
└── ... ```

## Despliegue para Desarrollo Local

Para ejecutar el proyecto localmente durante el desarrollo, sigue estos pasos en terminales separadas:

### Backend (Django REST Framework)

1.  **Navega al directorio del backend:**
    ```bash
    cd pokemon-app/backend
    ```

2.  **Activa tu entorno virtual de Python:**
    ```bash
    # Si usas venv
    source venv/bin/activate
    # Si usas Conda
    conda activate tu_entorno
    # ... (otros entornos virtuales)
    ```

3.  **Instala las dependencias del backend:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplica las migraciones de Django:**
    ```bash
    python manage.py migrate
    ```

5.  **Ejecuta el servidor de desarrollo de Django:**
    ```bash
    python manage.py runserver
    ```
    El backend estará disponible en `http://127.0.0.1:8000/` por defecto.

### Frontend (React con Vite)

1.  **Navega al directorio del frontend:**
    ```bash
    cd ../frontend
    ```

2.  **Instala las dependencias del frontend:**
    ```bash
    npm install
    # o
    yarn install
    # o
    pnpm install
    ```

3.  **Ejecuta el servidor de desarrollo de Vite:**
    ```bash
    npm run dev
    # o
    yarn dev
    # o
    pnpm dev
    ```
    El frontend estará disponible en `http://localhost:5173/` por defecto (el puerto puede variar).

## Despliegue para Producción

El despliegue para producción requiere una configuración más robusta y depende de tu proveedor de hosting. Aquí te presento una guía general:

### Backend (Django REST Framework)

1.  **Prepara tu servidor:** Necesitarás un servidor con Python instalado, así como las bibliotecas necesarias (Django, DRF, la base de datos, etc.).

2.  **Instala las dependencias:** Transfiere el directorio `backend` a tu servidor e instala las dependencias dentro de un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configura la base de datos:** Asegúrate de que la base de datos esté configurada correctamente en `tu_proyecto/settings.py` para el entorno de producción. Aplica las migraciones:
    ```bash
    python manage.py migrate
    ```

4.  **Recopila los archivos estáticos:** Si tu backend sirve archivos estáticos (aunque en este caso el frontend los sirve principalmente), recógelos:
    ```bash
    python manage.py collectstatic
    ```

5.  **Configura un servidor web:** Necesitarás un servidor web como **Nginx** o **Apache** para servir tu aplicación Django. También necesitarás un servidor de aplicaciones WSGI como **Gunicorn** o **uWSGI** para interactuar con Django.

    * **Ejemplo con Gunicorn y Nginx:**
        * Instala Gunicorn: `pip install gunicorn`
        * Ejecuta Gunicorn: `gunicorn tu_proyecto.wsgi:application --bind 0.0.0.0:8000` (ajusta la dirección y el puerto según tu configuración).
        * Configura Nginx como proxy inverso para dirigir las solicitudes al puerto de Gunicorn.

6.  **Configura un sistema de gestión de procesos:** Utiliza herramientas como **systemd** (en Linux) para gestionar el proceso de Gunicorn y asegurarte de que se reinicie automáticamente en caso de fallos.

7.  **Consideraciones de seguridad:**
    * Configura `SECRET_KEY` de forma segura (usando variables de entorno).
    * Desactiva el modo `DEBUG` en `settings.py`.
    * Configura HTTPS.
    * Aplica otras medidas de seguridad recomendadas para Django.

### Frontend (React con Vite)

1.  **Construye la aplicación:** En tu entorno de desarrollo local, construye la aplicación React para producción:
    ```bash
    cd pokemon-app/frontend
    npm run build
    # o
    yarn build
    # o
    pnpm build
    ```
    Esto creará una carpeta `dist` que contiene los archivos estáticos optimizados para producción (HTML, CSS, JavaScript, assets).

2.  **Prepara un servidor web para servir los archivos estáticos:** Necesitarás un servidor web como **Nginx** o **Apache** para servir los archivos de la carpeta `dist`.

    * **Ejemplo con Nginx:**
        Configura un bloque de servidor en Nginx para servir los archivos desde la ubicación de tu carpeta `dist`.

3.  **Carga los archivos construidos al servidor:** Transfiere el contenido de la carpeta `dist` a la ubicación configurada en tu servidor web.

4.  **Configura las variables de entorno:** Si tu frontend necesita variables de entorno para la API del backend (por ejemplo, la URL del backend), configúralas en tu entorno de producción (ya sea directamente en la configuración del servidor web o a través de variables de entorno que la aplicación React pueda leer durante la construcción o en tiempo de ejecución).

### Interacción Frontend - Backend

* Asegúrate de que la URL del backend a la que hace peticiones tu frontend en producción sea la correcta (la dirección y el puerto donde está sirviendo tu backend). Esto a menudo se configura a través de variables de entorno en el frontend.
* Configura **CORS (Cross-Origin Resource Sharing)** en tu backend de Django para permitir las peticiones desde el dominio de tu frontend en producción. Esto generalmente implica instalar `django-cors-headers` y configurarlo en `settings.py` con los dominios permitidos.
