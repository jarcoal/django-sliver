from sliver.views import ModelResource, CollectionResource
from sliver.mixins import JSONMixin

from .models import Person


class PersonCollectionResource(JSONMixin, CollectionResource):
	model = Person

class PersonResource(JSONMixin, ModelResource):
	model = Person
