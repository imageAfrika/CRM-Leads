MIDDLEWARE = [
    # ... other middleware
    'authentication.middleware.ProfileAuthenticationMiddleware',
]

# Set DEBUG to True for development
DEBUG = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'registration' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'authentication.context_processors.profile_context',
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'expenses' / 'static',
    BASE_DIR / 'purchases' / 'static',
    BASE_DIR / 'banking' / 'static',
    BASE_DIR / 'banking' / 'static' / 'banking',
    BASE_DIR / 'reports' / 'static',
    BASE_DIR / 'registration' / 'static',
    BASE_DIR / 'access_control' / 'static',
    BASE_DIR / 'people' / 'static',
    BASE_DIR / 'project_management' / 'static',
]

# The absolute path to the directory where collectstatic will collect static files for deployment
STATIC_ROOT = BASE_DIR / 'staticfiles'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'clients.apps.ClientsConfig',
    'sales',
    'documents',
    'dashboard',
    'django_extensions',
    'authentication',
    'expenses.apps.ExpensesConfig',
    'purchases.apps.PurchasesConfig',
    'banking.apps.BankingConfig',
    'reports.apps.ReportsConfig',
    'access_control.apps.AccessControlConfig',
    'registration.apps.RegistrationConfig',
    'people.apps.PeopleConfig',
    'project_management.apps.ProjectManagementConfig',
]