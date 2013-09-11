DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'captain',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB',
            'charset': 'utf8',
            'use_unicode': True,
        },
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    }
}
DEBUG = TEMPLATE_DEBUG = True
DEV = True
SECRET_KEY = 'travis-ci'
SITE_URL = 'http://127.0.0.1'
NOSE_ARGS = ['--logging-clear-handlers', '--logging-filter=-django_browserid,-factory']
