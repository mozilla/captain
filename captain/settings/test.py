import os


GRAVATAR_URL = 'https://secure.gravatar.com'


# Configure test database for TravisCI.
if os.environ.get('TRAVIS'):
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
