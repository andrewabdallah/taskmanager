import factory
import factory.fuzzy
from faker import Faker

from tasks.models import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("sentence", nb_words=6)
    description = factory.Faker("paragraph", nb_sentences=3)
    priority = factory.fuzzy.FuzzyInteger(1, 5)
    due_date = factory.LazyFunction(
        lambda: Faker().date_between(start_date="+1d", end_date="+30d")
    )
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in Task.STATUS_CHOICES])
    owner = factory.SubFactory("core.factories.user_factory.UserFactory")
