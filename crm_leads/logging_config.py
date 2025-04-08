LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'crm_leads.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'expenses': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'purchases': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'documents': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
