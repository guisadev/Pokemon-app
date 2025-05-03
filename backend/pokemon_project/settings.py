# pokemon_project/settings.py

import os # Asegúrate de que os esté importado si usas os.environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key' 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # Deja esto en True para desarrollo

ALLOWED_HOSTS = [] # Añade tus hosts de producción aquí

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps de terceros y locales:
    'rest_framework', # Django REST Framework
    'corsheaders',    # Para manejar CORS con el frontend
    'api',            # Tu aplicación API local
    
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Debe ir lo más arriba posible, antes de CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pokemon_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pokemon_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Usamos SQLite por defecto. Si no guardas datos de Pokémon aquí,
# igual se usa para usuarios, sesiones, etc.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# ¡Asegúrate de que NO haya configuración de PostgreSQL activa si no la quieres!


# Cache
# https://docs.djangoproject.com/en/5.2/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pokemon-app-locmem-cache', # Nombre único para este cache
        'TIMEOUT': 60 * 15, # Tiempo de vida por defecto en segundos (15 minutos)
        'OPTIONS': {
            'MAX_ENTRIES': 1000 # Número máximo de entradas en cache
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericAttributeValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us' # O 'es-cl' si prefieres español de Chile

TIME_ZONE = 'UTC' # O 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS Settings (required for frontend on different port/domain)
# https://github.com/adamchainz/django-cors-headers

CORS_ALLOW_ALL_ORIGINS = True # ¡Permite cualquier origen! Solo para desarrollo.
# En producción, cambia a:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173", # Ejemplo si tu frontend corre en este puerto
#     # Añade aquí los dominios y puertos EXACTOS de tu frontend en producción
# ]
# CORS_ALLOWED_METHODS = [...] # Opcional: Limitar métodos HTTP
# CORS_ALLOWED_HEADERS = [...] # Opcional: Limitar headers