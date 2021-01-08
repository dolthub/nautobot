import importlib
import logging
import os
import platform
import re
import socket
import warnings
from urllib.parse import urlsplit

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import URLValidator

from extras.plugins.utils import load_plugins


#
# Environment setup
#

# FIXME(jathan): This should be defined in package metadata, not settings.
VERSION = '2.10.3'

# Hostname of the system. This is displayed in the web UI footers along with the
# version.
HOSTNAME = platform.node()

# Set the base directory two levels up
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# FIXME(jathan): This should be done as part of package install, not settings.
# Validate Python version
if platform.python_version_tuple() < ('3', '6'):
    raise RuntimeError(
        "NetBox requires Python 3.6 or higher (current: Python {})".format(platform.python_version())
    )


###########################################################
# NETBOX - Settings for NetBox internals/plugins/defaults #
###########################################################

#
# NetBox optional settings/defaults
#
ALLOWED_URL_SCHEMES = (
    'file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc', 'xmpp',
)
BANNER_BOTTOM = ''
BANNER_LOGIN = ''
BANNER_TOP = ''
BASE_PATH = ''
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip('/') + '/'  # Enforce trailing slash only
CACHE_TIMEOUT = 900
CUSTOM_JOBS_ROOT = os.path.join(BASE_DIR, 'custom_jobs').rstrip('/')
CHANGELOG_RETENTION = 90
DEVELOPER = False
DOCS_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'docs')
HIDE_RESTRICTED_UI = False

# This is a dict wrapper for the various default Django `EMAIL_*` settings
EMAIL = {}

ENFORCE_GLOBAL_UNIQUE = False

# Exclude potentially sensitive models from wildcard view exemption. These may still be exempted
# by specifying the model individually in the EXEMPT_VIEW_PERMISSIONS configuration parameter.
EXEMPT_EXCLUDE_MODELS = (
    ('auth', 'group'),
    ('auth', 'user'),
    ('users', 'objectpermission'),
)

EXEMPT_VIEW_PERMISSIONS = []
GIT_ROOT = os.path.join(BASE_DIR, 'git').rstrip('/')
HTTP_PROXIES = None
LOGIN_TIMEOUT = None  # FIXME(jathan): Custom alias for SESSION_COOKIE_AGE
MAINTENANCE_MODE = False
MAX_PAGE_SIZE = 1000  # FIXME(jathan): This duplicates DRF built-in for settings.REST_FRAMEWORK['PAGE_SIZE']

# Metrics
METRICS_ENABLED = False

# Napalm
NAPALM_ARGS = {}
NAPALM_PASSWORD = ''
NAPALM_TIMEOUT = 30
NAPALM_USERNAME = ''

# Pagination
PAGINATE_COUNT = 50  # FIXME(jathan): How does this differ from MAX_PAGE_SIZE?
PER_PAGE_DEFAULTS = [
    25, 50, 100, 250, 500, 1000
]
if PAGINATE_COUNT not in PER_PAGE_DEFAULTS:
    PER_PAGE_DEFAULTS.append(PAGINATE_COUNT)
    PER_PAGE_DEFAULTS = sorted(PER_PAGE_DEFAULTS)

# Plugins
PLUGINS = []
PLUGINS_CONFIG = {}

# IPv4?
PREFER_IPV4 = False

# Racks
RACK_ELEVATION_DEFAULT_UNIT_HEIGHT = 22
RACK_ELEVATION_DEFAULT_UNIT_WIDTH = 220

# Remote auth
REMOTE_AUTH_AUTO_CREATE_USER = False
REMOTE_AUTH_DEFAULT_GROUPS = []
REMOTE_AUTH_DEFAULT_PERMISSIONS = {}
REMOTE_AUTH_ENABLED = True  # FIXME(jathan): Deprecated in Grimlock
REMOTE_AUTH_HEADER = 'HTTP_REMOTE_USER'

# Releases
RELEASE_CHECK_URL = None
RELEASE_CHECK_TIMEOUT = 24 * 3600

# Reports
REPORTS_ROOT = os.path.join(BASE_DIR, 'reports').rstrip('/')

# RQ
RQ_DEFAULT_TIMEOUT = 300

# Scripts
SCRIPTS_ROOT = os.path.join(BASE_DIR, 'scripts').rstrip('/')

# Secrets
SECRETS_MIN_PUBKEY_SIZE = 2048

# Storage
STORAGE_BACKEND = None
STORAGE_CONFIG = {}


#
# Django cryptography
#

# CRYPTOGRAPHY_BACKEND = cryptography.hazmat.backends.default_backend()
# CRYPTOGRAPHY_DIGEST = cryptography.hazmat.primitives.hashes.SHA256
CRYPTOGRAPHY_KEY = None  # Defaults to SECRET_KEY if unset
CRYPTOGRAPHY_SALT = 'netbox-cryptography'


#
# Django Prometheus
#

PROMETHEUS_EXPORT_MIGRATIONS = False


#
# Django filters
#

FILTERS_NULL_CHOICE_LABEL = 'None'
FILTERS_NULL_CHOICE_VALUE = 'null'


#
# Django REST framework (API)
#

REST_FRAMEWORK_VERSION = VERSION.rsplit('.', 1)[0]  # Use major.minor as API version
REST_FRAMEWORK = {
    'ALLOWED_VERSIONS': [REST_FRAMEWORK_VERSION],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'netbox.api.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_METADATA_CLASS': 'netbox.api.metadata.BulkOperationMetadata',
    'DEFAULT_PAGINATION_CLASS': 'netbox.api.pagination.OptionalLimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'netbox.api.authentication.TokenPermissions',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'netbox.api.renderers.FormlessBrowsableAPIRenderer',
    ),
    'DEFAULT_VERSION': REST_FRAMEWORK_VERSION,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'PAGE_SIZE': PAGINATE_COUNT,
    'SCHEMA_COERCE_METHOD_NAMES': {
        # Default mappings
        'retrieve': 'read',
        'destroy': 'delete',
        # Custom operations
        'bulk_destroy': 'bulk_delete',
    },
    'VIEW_NAME_FUNCTION': 'utilities.api.get_view_name',
}


#
# drf_yasg (OpenAPI/Swagger)
#

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utilities.custom_inspectors.NetBoxSwaggerAutoSchema',
    'DEFAULT_FIELD_INSPECTORS': [
        'utilities.custom_inspectors.CustomFieldsDataFieldInspector',
        'utilities.custom_inspectors.JSONFieldInspector',
        'utilities.custom_inspectors.NullableBooleanFieldInspector',
        'utilities.custom_inspectors.ChoiceFieldInspector',
        'utilities.custom_inspectors.SerializedPKRelatedFieldInspector',
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SerializerMethodFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'DEFAULT_FILTER_INSPECTORS': [
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'DEFAULT_INFO': 'netbox.urls.openapi_info',
    'DEFAULT_MODEL_DEPTH': 1,
    'DEFAULT_PAGINATOR_INSPECTORS': [
        'utilities.custom_inspectors.NullablePaginatorInspector',
        'drf_yasg.inspectors.DjangoRestResponsePagination',
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'VALIDATOR_URL': None,
}


##############################################
# DJANGO - Core settings required for Django #
##############################################

# Default overrides
ALLOWED_HOSTS = []
DATETIME_FORMAT = 'N j, Y g:i a'
INTERNAL_IPS = ('127.0.0.1', '::1')
LOGGING = {}
MEDIA_ROOT = os.path.join(BASE_DIR, 'media').rstrip('/')
SESSION_FILE_PATH = None
SHORT_DATE_FORMAT = 'Y-m-d'
SHORT_DATETIME_FORMAT = 'Y-m-d H:i'
TIME_FORMAT = 'g:i a'
TIME_ZONE = 'UTC'

# Installed apps and Django plugins. NetBox plugins will be appended here later.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'cacheops',
    'corsheaders',
    'debug_toolbar',
    'django_filters',
    'django_tables2',
    'django_prometheus',
    'mptt',
    'rest_framework',
    'taggit',
    'timezone_field',
    'circuits',
    'dcim',
    'ipam',
    'extras',
    'secrets',
    'tenancy',
    'users',
    'utilities',
    'virtualization',
    'django_rq',  # Must come after extras to allow overriding management commands
    'drf_yasg',
    'graphene_django'
]

# Middleware
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'netbox.middleware.ExceptionHandlingMiddleware',
    'netbox.middleware.RemoteUserMiddleware',
    'netbox.middleware.APIVersionMiddleware',
    'netbox.middleware.ObjectChangeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'netbox.urls'

TEMPLATES_DIR = BASE_DIR + '/templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'netbox.context_processors.settings_and_registry',
            ],
        },
    },
]

# Set up authentication backends
AUTHENTICATION_BACKENDS = [
    # Always check object permissions
    'netbox.authentication.ObjectPermissionBackend',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# WSGI
WSGI_APPLICATION = 'netbox.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + '/static'
STATIC_URL = '/{}static/'.format(BASE_PATH)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "project-static"),
)

# Media
MEDIA_URL = '/{}media/'.format(BASE_PATH)

# Disable default limit of 1000 fields per request. Needed for bulk deletion of objects. (Added in Django 1.10.)
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Authentication URLs
LOGIN_URL = '/{}login/'.format(BASE_PATH)

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

#
# From django-cors-headers
#
CORS_ORIGIN_ALLOW_ALL = False  # FIXME(jathan): Renamed to CORS_ALLOW_ALL_ORIGINS in django-cors-headers==3.5.0
CORS_ORIGIN_REGEX_WHITELIST = []  # FIXME(jathan): Renamed to CORS_ALLOWED_ORIGIN_REGEXES in django-cors-headers==3.5.0
CORS_ORIGIN_WHITELIST = []  # FIXME(jathan): Renamed to CORS_ALLOWED_ORIGINS in django-cors-headers==3.5.0

#
# GraphQL
#
GRAPHENE = {
    'SCHEMA': 'netbox.graphql.schema_init.schema',
    'DJANGO_CHOICE_FIELD_ENUM_V3_NAMING': True,  # any field with a name of type will break in Graphene otherwise.
}
GRAPHQL_CUSTOM_FIELD_PREFIX = "cf"

#################################################################
# CONFIGURATION.PY - Configuration import from configuration.py #
#################################################################

# Import site-specific configuration parameters and overlay them
try:
    from netbox import configuration
except ModuleNotFoundError as err:
    if getattr(err, 'name') == 'configuration':
        raise ImproperlyConfigured(
            "Configuration file is not present. Please define netbox/netbox/configuration.py per the documentation."
        )
    raise

# Enforce required configuration parameters
for parameter in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY', 'REDIS']:
    if not hasattr(configuration, parameter):
        raise ImproperlyConfigured(
            "Required parameter {} is missing from configuration.py.".format(parameter)
        )

# Now that we've asserted that configuration works, import everything into local
# scope to support overloading.
from netbox.configuration import *  # noqa


#
# Email
#

# FIXME(jathan): Consider ripping this out entirely. Each of these are Django
# core settings that are being wrapped in this custom `EMAIL` setting. For now,
# if `EMAIL` is set, then this will be processed, otherwise these EMAIL_*
# variables will just pass through from `configuration.py` untouched (per Django
# settings)
if EMAIL:
    EMAIL_HOST = EMAIL.get('SERVER')
    EMAIL_HOST_USER = EMAIL.get('USERNAME')
    EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
    EMAIL_PORT = EMAIL.get('PORT', 25)
    EMAIL_SSL_CERTFILE = EMAIL.get('SSL_CERTFILE')
    EMAIL_SSL_KEYFILE = EMAIL.get('SSL_KEYFILE')
    EMAIL_SUBJECT_PREFIX = '[NetBox] '
    EMAIL_USE_SSL = EMAIL.get('USE_SSL', False)
    EMAIL_USE_TLS = EMAIL.get('USE_TLS', False)
    EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
    SERVER_EMAIL = EMAIL.get('FROM_EMAIL')


##############
# VALIDATION #
##############

#
# Authentication
#
# FIXME(jathan): This is just here as an interim validation check, to be
# replaced in a future update when all other validations hard-coded here in
# settings are moved to use the Django system check framework.
if 'netbox.authentication.ObjectPermissionBackend' not in AUTHENTICATION_BACKENDS:
    raise ImproperlyConfigured(
        "netbox.authentication.ObjectPermissionBackend must be defined in "
        "'AUTHENTICATION_BACKENDS'"
    )

#
# Releases
#

# Validate update repo URL and timeout
if RELEASE_CHECK_URL:
    try:
        URLValidator(RELEASE_CHECK_URL)
    except ValidationError:
        raise ImproperlyConfigured(
            "RELEASE_CHECK_URL must be a valid API URL. Example: "
            "https://api.github.com/repos/networktocode-llc/grimlock"
        )

# FIXME(jathan): Why is this enforced here? This would be better enforced in the core.
# Enforce a minimum cache timeout for update checks
if RELEASE_CHECK_TIMEOUT < 3600:
    raise ImproperlyConfigured("RELEASE_CHECK_TIMEOUT has to be at least 3600 seconds (1 hour)")


#
# Database
#

# Only PostgreSQL is supported
if METRICS_ENABLED:
    DATABASE.update({
        'ENGINE': 'django_prometheus.db.backends.postgresql'
    })
else:
    DATABASE.update({
        'ENGINE': 'django.db.backends.postgresql'
    })

DATABASES = {
    'default': DATABASE,
}


#
# Media storage
#

if STORAGE_BACKEND is not None:
    DEFAULT_FILE_STORAGE = STORAGE_BACKEND

    # django-storages
    if STORAGE_BACKEND.startswith('storages.'):

        try:
            import storages.utils
        except ModuleNotFoundError as e:
            if getattr(e, 'name') == 'storages':
                raise ImproperlyConfigured(
                    f"STORAGE_BACKEND is set to {STORAGE_BACKEND} but django-storages is not present. It can be "
                    f"installed by running 'pip install django-storages'."
                )
            raise e

        # Monkey-patch django-storages to fetch settings from STORAGE_CONFIG
        def _setting(name, default=None):
            if name in STORAGE_CONFIG:
                return STORAGE_CONFIG[name]
            return globals().get(name, default)
        storages.utils.setting = _setting

if STORAGE_CONFIG and STORAGE_BACKEND is None:
    warnings.warn(
        "STORAGE_CONFIG has been set in configuration.py but STORAGE_BACKEND is not defined. STORAGE_CONFIG will be "
        "ignored."
    )


#
# Redis
#

# Background task queuing
if 'tasks' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing the 'tasks' subsection."
    )
TASKS_REDIS = REDIS['tasks']
TASKS_REDIS_HOST = TASKS_REDIS.get('HOST', 'localhost')
TASKS_REDIS_PORT = TASKS_REDIS.get('PORT', 6379)
TASKS_REDIS_SENTINELS = TASKS_REDIS.get('SENTINELS', [])
TASKS_REDIS_USING_SENTINEL = all([
    isinstance(TASKS_REDIS_SENTINELS, (list, tuple)),
    len(TASKS_REDIS_SENTINELS) > 0
])
TASKS_REDIS_SENTINEL_SERVICE = TASKS_REDIS.get('SENTINEL_SERVICE', 'default')
TASKS_REDIS_SENTINEL_TIMEOUT = TASKS_REDIS.get('SENTINEL_TIMEOUT', 10)
TASKS_REDIS_PASSWORD = TASKS_REDIS.get('PASSWORD', '')
TASKS_REDIS_DATABASE = TASKS_REDIS.get('DATABASE', 0)
TASKS_REDIS_SSL = TASKS_REDIS.get('SSL', False)

# Caching
if 'caching' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing caching subsection."
    )
CACHING_REDIS = REDIS['caching']
CACHING_REDIS_HOST = CACHING_REDIS.get('HOST', 'localhost')
CACHING_REDIS_PORT = CACHING_REDIS.get('PORT', 6379)
CACHING_REDIS_SENTINELS = CACHING_REDIS.get('SENTINELS', [])
CACHING_REDIS_USING_SENTINEL = all([
    isinstance(CACHING_REDIS_SENTINELS, (list, tuple)),
    len(CACHING_REDIS_SENTINELS) > 0
])
CACHING_REDIS_SENTINEL_SERVICE = CACHING_REDIS.get('SENTINEL_SERVICE', 'default')
CACHING_REDIS_PASSWORD = CACHING_REDIS.get('PASSWORD', '')
CACHING_REDIS_DATABASE = CACHING_REDIS.get('DATABASE', 0)
CACHING_REDIS_SSL = CACHING_REDIS.get('SSL', False)


#
# Sessions
#

if LOGIN_TIMEOUT is not None:
    # Django default is 1209600 seconds (14 days)
    SESSION_COOKIE_AGE = LOGIN_TIMEOUT
if SESSION_FILE_PATH is not None:
    SESSION_ENGINE = 'django.contrib.sessions.backends.file'


#
# Caching
#
if CACHING_REDIS_USING_SENTINEL:
    CACHEOPS_SENTINEL = {
        'locations': CACHING_REDIS_SENTINELS,
        'service_name': CACHING_REDIS_SENTINEL_SERVICE,
        'db': CACHING_REDIS_DATABASE,
    }
else:
    if CACHING_REDIS_SSL:
        REDIS_CACHE_CON_STRING = 'rediss://'
    else:
        REDIS_CACHE_CON_STRING = 'redis://'

    if CACHING_REDIS_PASSWORD:
        REDIS_CACHE_CON_STRING = '{}:{}@'.format(REDIS_CACHE_CON_STRING, CACHING_REDIS_PASSWORD)

    REDIS_CACHE_CON_STRING = '{}{}:{}/{}'.format(
        REDIS_CACHE_CON_STRING,
        CACHING_REDIS_HOST,
        CACHING_REDIS_PORT,
        CACHING_REDIS_DATABASE
    )
    CACHEOPS_REDIS = REDIS_CACHE_CON_STRING

if not CACHE_TIMEOUT:
    CACHEOPS_ENABLED = False
else:
    CACHEOPS_ENABLED = True


CACHEOPS_DEFAULTS = {
    'timeout': CACHE_TIMEOUT
}
CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},
    'auth.*': {'ops': ('fetch', 'get')},
    'auth.permission': {'ops': 'all'},
    'circuits.*': {'ops': 'all'},
    'dcim.inventoryitem': None,  # MPTT models are exempt due to raw SQL
    'dcim.region': None,  # MPTT models are exempt due to raw SQL
    'dcim.rackgroup': None,  # MPTT models are exempt due to raw SQL
    'dcim.*': {'ops': 'all'},
    'ipam.*': {'ops': 'all'},
    'extras.*': {'ops': 'all'},
    'secrets.*': {'ops': 'all'},
    'users.*': {'ops': 'all'},
    'tenancy.tenantgroup': None,  # MPTT models are exempt due to raw SQL
    'tenancy.*': {'ops': 'all'},
    'virtualization.*': {'ops': 'all'},
}
CACHEOPS_DEGRADE_ON_FAILURE = True


#
# Django RQ (Webhooks backend)
#

if TASKS_REDIS_USING_SENTINEL:
    RQ_PARAMS = {
        'SENTINELS': TASKS_REDIS_SENTINELS,
        'MASTER_NAME': TASKS_REDIS_SENTINEL_SERVICE,
        'DB': TASKS_REDIS_DATABASE,
        'PASSWORD': TASKS_REDIS_PASSWORD,
        'SOCKET_TIMEOUT': None,
        'CONNECTION_KWARGS': {
            'socket_connect_timeout': TASKS_REDIS_SENTINEL_TIMEOUT
        },
    }
else:
    RQ_PARAMS = {
        'HOST': TASKS_REDIS_HOST,
        'PORT': TASKS_REDIS_PORT,
        'DB': TASKS_REDIS_DATABASE,
        'PASSWORD': TASKS_REDIS_PASSWORD,
        'SSL': TASKS_REDIS_SSL,
        'DEFAULT_TIMEOUT': RQ_DEFAULT_TIMEOUT,
    }

RQ_QUEUES = {
    'default': RQ_PARAMS,  # Webhooks
    'check_releases': RQ_PARAMS,
}


#
# Plugins
#

# Process the plugins and manipulate the specified config settings that are passed in.
load_plugins(PLUGINS, INSTALLED_APPS, PLUGINS_CONFIG, VERSION, MIDDLEWARE, CACHEOPS)
