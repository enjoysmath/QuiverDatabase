"""
Django settings for QuiverDatabase project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import django_heroku
import dj_database_url


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            },
        },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
        },
} 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'TODO: use secret key in deployment')

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get('ON_HEROKU', '0') == '0':
    DEBUG = True
else:
    DEBUG = False

DEBUG = True    # TODO comment out

ALLOWED_HOSTS = [
    '127.0.0.1',
    'quiver-database.herokuapp.com'
]


# Application definition

INSTALLED_APPS = [
    'password_reset',
    'django.contrib.messages',
    'django_neomodel',    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'database_service.apps.DatabaseServiceConfig',
    'whitenoise.runserver_nostatic',
    'crispy_forms',
    'rules.apps.RulesConfig',
    'accounts.apps.AccountsConfig',
    'diagram_editor.apps.DiagramEditorConfig',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',    
    'django.contrib.messages.middleware.MessageMiddleware',    
    'django.middleware.security.SecurityMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'QuiverDatabase.urls'

TEMPLATES = [
    # Tried Jinja2 template engine, and it didn't work with crispy forms (unfixable errors when doing forms)
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('QuiverDatabase', 'templates'),
                 BASE_DIR.joinpath('accounts', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]
    
#TEMPLATES = [
    #{
        #'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': [str(BASE_DIR.joinpath('templates'))],
        #'APP_DIRS': True,
        #'OPTIONS': {
            #'debug': True,
            #'context_processors': [
                #'django.template.context_processors.debug',
                #'django.template.context_processors.request',
                #'django.contrib.auth.context_processors.auth',
                #'django.contrib.messages.context_processors.messages',
            #],
        #},
    #},
    #{
        #"BACKEND": "django.template.backends.jinja2.Jinja2",
        #"DIRS": [os.path.join(BASE_DIR, "templates")],
        #"APP_DIRS": True,
        #'OPTIONS': {
            #"environment": "QuiverDatabase.jinja2.environment",
        #},
    #},    
#]

WSGI_APPLICATION = 'QuiverDatabase.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if os.environ.get('ON_HEROKU', '0') == '0':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        # TODO: what does this max_age setting do?
        'default' : dj_database_url.config(conn_max_age=600)
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'diagrams/static'),
    os.path.join(BASE_DIR, 'static'),    
    os.path.join(BASE_DIR,'QuiverDatabase/static'),
    # ^^^ BUGFIX: this fixes a lot of issues such as KaTeX load error
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


def neo4j_url():
    url = os.environ.get('NEO4J_SCHEMA', 'bolt') + "://"
    url += os.environ.get('NEO4J_USERNAME', 'neo4j') + ":"
    url += os.environ.get('NEO4J_PASSWORD', 'neo4j') + "@"
    url += os.environ.get('NEO4J_HOST', 'localhost') + ":"
    url += os.environ.get('NEO4J_PORT', '7687')
    return url

NEOMODEL_NEO4J_BOLT_URL = neo4j_url()

NEOMODEL_SIGNALS = True
NEOMODEL_FORCE_TIMEZONE = False
NEOMODEL_ENCRYPTED_CONNECTION = False  # TODO: how do we switch this on without error?

from neomodel import config   # BUGFIX: had to do it this way
config.MAX_POOL_SIZE = 50  # TODO: what does this affect?

#LOGIN_REDIRECT_URL = 'home'
#LOGOUT_REDIRECT_URL = 'home'

# Activate Django-Heroku.
django_heroku.settings(locals())

MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MAX_TEXT_LENGTH = 150

MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 50

MAX_USER_EDIT_DIAGRAMS = 8

#CSRF_USE_SESSIONS = False
#CSRF_COOKIE_HTTPONLY = False
#CSRF_COOKIE_DOMAIN = 'localhost'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#By default, SESSION_EXPIRE_AT_BROWSER_CLOSE is set to False, which means session cookies 
#will be stored in users' browsers for as long as SESSION_COOKIE_AGE. 
#Use this if you don't want people to have to log in every time they open a browser.
SESSSION_EXPIRE_AT_BROWSER_CLOSE = False

#TODO:
#Clearing the session store¶
#As users create new sessions on your website, session data can accumulate in your session store. If you're using the database backend, the django_session database table will grow. If you're using the file backend, your temporary directory will contain an increasing number of files.

#To understand this problem, consider what happens with the database backend. When a user logs in, Django adds a row to the django_session database table. Django updates this row each time the session data changes. If the user logs out manually, Django deletes the row. But if the user does not log out, the row never gets deleted. A similar process happens with the file backend.

#Django does not provide automatic purging of expired sessions. Therefore, it's your job to purge expired sessions on a regular basis. Django provides a clean-up management command for this purpose: clearsessions. It's recommended to call this command on a regular basis, for example as a daily cron job.

#Note that the cache backend isn't vulnerable to this problem, because caches automatically delete stale data. Neither is the cookie backend, because the session data is stored by the users' browsers.

#from jinja2 import Undefined
#JINJA2_ENVIRONMENT_OPTIONS = { 'undefined' : Undefined }

# TODO: Enable Click-jacking protection
X_FRAME_OPTIONS = 'ALLOW'   # ie set this to "DENY"
# https://docs.djangoproject.com/en/1.11/ref/clickjacking/

#CSRF_COOKIE_SAMESITE = None
#CSRF_COOKIE_SECURE = True

LOGIN_URL = '/sign-in'     # this should coinside with url pattern of login view
LOGOUT_URL = '/sign-out'   # same but for logout view
LOGIN_REDIRECT_URL = '/' # url to main page