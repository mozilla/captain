from django.contrib.auth.models import User

from factory import DjangoModelFactory, Sequence


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = User

    username = Sequence(lambda n: 'test{0}'.format(n))
    email = Sequence(lambda n: 'test{0}@example.com'.format(n))
