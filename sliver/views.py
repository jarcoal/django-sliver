from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from django.db.models import ForeignKey, OneToOneField
from django.db.models.fields.related import RelatedField

import datetime

from types import NoneType
from decimal import Decimal

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import responses

class Resource(View):
	"""
	Root resource object
	"""

	fields = None
	exclude = []
	relationships = {}

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		"""
		Make sure the request meets any global requirements and is exempt from csrf.
		"""

		#if a response exception is raised, grab it and return it to django
		try:
			return super(Resource, self).dispatch(request, *args, **kwargs)
		except responses.SliverResponse, r:
			return r.response()

	def get_model_class(self):
		return self.model if hasattr(self, 'model') and self.model else self.get_queryset().model

	def hydrate(self):
		"""
		Prepares the incoming data for the database.
		"""

		data = self.parse(self.request.body)
		cleaned_data = {}

		model_class = self.get_model_class()

		for key, val in data.items():
			#make sure it's allowed
			if (self.fields and key not in self.fields) or key in self.exclude:
				continue

			#get the field with that name
			field = model_class._meta.get_field_by_name(key)[0]

			#hydrate it
			cleaned_data[key] = self.hydrate_value(field, val)

		return cleaned_data


	def hydrate_value(self, field, val):
		"""
		Prepares a single model attribute for the database.
		"""
		try:
			val = field.get_prep_value(val)
		except:
			raise responses.HttpResponseBadRequest

		#this is a foreign key, we need to manually hydrate it
		if val and isinstance(field, RelatedField):
			fk = {}
			fk[field.rel.field_name] = val

			val = field.rel.to.objects.get(**fk)

		return val


	def dehydrate_value(self, model, field):
		"""
		Prepares a single model attribute for the tubes.
		"""

		val = field.value_from_object(model)

		#if it's something from the datetime lib, convert to iso
		if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
			val = val.isoformat()

		#decimal fields
		elif isinstance(val, Decimal):
			val = float(val)

		#if it's something we don't know about, just convert to string
		elif not isinstance(val, (int, str, bool, NoneType)):
			val = unicode(val)		

		return val


	def dehydrate_relationship(self, model, relationship_name, relationship_prefix=None):
		"""
		Prepares a relationship for the tubes.
		"""

		full_relationship_name = '__'.join([relationship_prefix, relationship_name]) if relationship_prefix else relationship_name

		related_object = getattr(model, relationship_name)
		relationship_data = self.relationships[full_relationship_name]

		dehydrate_params = {
			'fields': relationship_data.get('fields'),
			'exclude': relationship_data.get('exclude'),
			'relationship_prefix': full_relationship_name,
		}

		#this is a to-many relationship
		if related_object.__class__.__name__ in ('RelatedManager', 'ManyRelatedManager'):
			return [self.dehydrate(related_model, **dehydrate_params) for related_model in related_object.all()]

		#this is a to-one relationship
		return self.dehydrate(related_object, **dehydrate_params)
		

	def dehydrate(self, model, fields=None, exclude=None, relationship_prefix=None):
		"""
		Prepares the full resource for the tubes.
		"""

		field_values = {}
		exclude = exclude or []

		#if the relationship is optional, this will show up as None sometimes, so we just return it.
		if model is None:
			return None

		#loop through the fields and scoop up the data
		for field in model._meta.fields:
			if fields and not field.name in fields:
				continue

			if field.name in exclude:
				continue

			full_relationship_name = '__'.join([relationship_prefix, field.name]) if relationship_prefix else field.name

			#if this is a relationship they want expanded on
			if isinstance(field, RelatedField) and full_relationship_name in self.relationships:
				field_values[field.name] = self.dehydrate_relationship(model, field.name, relationship_prefix=relationship_prefix)

			#normal field, get the value
			else:
				field_values[field.name] = self.dehydrate_value(model, field)

		#loop through reverse relationships
		for reverse_relationship in model._meta.get_all_related_objects():
			relationship_name = reverse_relationship.get_accessor_name()
			full_relationship_name = '__'.join([relationship_prefix, relationship_name]) if relationship_prefix else relationship_name

			if full_relationship_name in self.relationships:
				field_values[relationship_name] = self.dehydrate_relationship(model, relationship_name, relationship_prefix=relationship_prefix)

		#loop through m2m relationships
		for m2m_relationship in model._meta.many_to_many:
			relationship_name = m2m_relationship.name
			full_relationship_name = '__'.join([relationship_prefix, relationship_name]) if relationship_prefix else relationship_name

			if full_relationship_name in self.relationships:
				field_values[relationship_name] = self.dehydrate_relationship(model, relationship_name, relationship_prefix=relationship_prefix)			

		return field_values


	def render_to_response(self, context, status=200):
		"""
		Out to the tubes...
		"""
		return HttpResponse(self.render(context), status=status)




class ModelResource(SingleObjectMixin, Resource):
	"""
	Resource for a single model
	"""

	def get(self, request, *args, **kwargs):
		"""
		GET requests - fetch object
		"""

		self.object = self.get_object()
		return self.render_to_response(self.get_context_data())


	def put(self, request, *args, **kwargs):
		"""
		PUT requests - update object
		"""

		self.object = self.get_object()

		for key, val in self.hydrate().items():
			setattr(self.object, key, val)

		self.object.save()

		return self.render_to_response(self.get_context_data())


	def delete(self, request, *args, **kwargs):
		"""
		DELETE requests - delete object
		"""

		self.object = self.get_object()
		self.object.delete()
		return self.render_to_response({}, status=204)


	def get_context_data(self):
		"""
		Prepares data for response
		"""
		return self.dehydrate(self.object, self.fields, self.exclude)




class CollectionResource(MultipleObjectMixin, Resource):
	"""
	Resource for a collection of models
	"""

	def post(self, request, *args, **kwargs):
		"""
		POST requests - add object
		"""

		model_class = self.get_model_class()
		self.object = model_class.objects.create(**self.hydrate())

		return self.render_to_response(self.dehydrate(self.object), status=201)


	def get(self, request, *args, **kwargs):
		"""
		GET requests - fetch objects
		"""

		self.object_list = self.get_queryset()
		return self.render_to_response(self.get_context_data())


	def get_context_data(self):
		"""
		Loop through the models in the queryset and dehydrate them.
		"""
		return [self.dehydrate(model, self.fields, self.exclude) for model in self.object_list]

