from factory import DjangoModelFactory, post_generation, Sequence, SubFactory

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

    @post_generation
    def sent(self, create, extracted, **kwargs):
        # Assign sent after the model is generated, since auto_now_add will overwrite it during
        # generation.
        if create and extracted:
            self.sent = extracted


class ScheduledCommandFactory(DjangoModelFactory):
    FACTORY_FOR = models.ScheduledCommand

    project = SubFactory(ProjectFactory)
    command = Sequence(lambda n: 'test{0}'.format(n))
    user = SubFactory(UserFactory)

