from factory import DjangoModelFactory, Sequence, SubFactory

from captain.projects import models
from captain.users.tests import UserFactory


class ProjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.Project

    name = Sequence(lambda n: 'test{0}'.format(n))
    homepage = Sequence(lambda n: 'http://example.com/{0}'.format(n))


class CommandLogFactory(DjangoModelFactory):
    FACTORY_FOR = models.CommandLog

    project = SubFactory(ProjectFactory)
    user = SubFactory(UserFactory)
    command = Sequence(lambda n: 'test{0}'.format(n))
