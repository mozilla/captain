from factory import DjangoModelFactory, Sequence

from captain.projects import models


class ProjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.Project

    name = Sequence(lambda n: 'test{0}'.format(n))
    homepage = Sequence(lambda n: 'http://example.com/{0}'.format(n))
