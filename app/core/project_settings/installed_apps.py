from dotenv import load_dotenv
import os

load_dotenv()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'drf_spectacular',

    'corsheaders',

    # ckeditor
    'ckeditor',
    'ckeditor_uploader',
    'django_resized',

    # auth / jwt
    'rest_framework_simplejwt',

    # apps
    'apps.base',
    'apps.cms',
    'apps.contacts',
    'apps.accounts',
]
