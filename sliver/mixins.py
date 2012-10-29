import json, csv
from StringIO import StringIO
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse


class FiltersMixin(object):
	"""
	Enable simple filtering of querysets
	"""

	filters = []

	def get_queryset(self):
		"""
		Override get_queryset and apply filters.
		"""
		return super(FiltersMixin, self).get_queryset().filter(**self.get_filters())

	def get_filters(self):
		"""
		Provides a dictionary of filters to apply to the queryset.
		"""

		filters = {}

		for key, value in self.request.GET.items():
			if key not in self.filters:
				continue

			filters[key] = value

		return filters


class URIMixin(object):
	"""
	Enable display of URIs in responses
	"""

	model_resource_name = None
	uri_attribute_name = '_uri'


	def get_model_resource_name(self, relationship=None):
		"""
		Hook for returning the url name for the model.
		This is the parameter that you would pass into "reverse()".

		Defaults to "model_resource_name" of main model or related model.
		"""

		if relationship:
			return self.relationships[relationship].get('model_resource_name')

		return self.model_resource_name


	def get_resource_url_kwargs(self, model, relationship=None):
		"""
		Returns the kwargs for the call to "reverse()".
		Should be related to your pk or slug.
		"""

		return { 'pk': model.pk }


	def get_model_resource_url(self, model, relationship=None):
		"""
		Return a resource url for a given model
		"""

		resource_name = self.get_model_resource_name(relationship)

		if resource_name is None:
			raise ImproperlyConfigured('URIMixin requires either a definition of "model_resource_name" or an implementation of "get_model_resource_name()" or "get_model_resource_url()"')

		return reverse(resource_name, kwargs=self.get_resource_url_kwargs(model, relationship))


	def hydrate(self, *a, **k):
		"""
		Remove the URI parameter from incoming requests.
		"""

		data = super(URIMixin, self).hydrate(*a, **k)

		try:
			del data[self.uri_attribute_name]
		except:
			pass

		return data


	def dehydrate(self, model, fields=None, exclude=None, relationship_prefix=None):
		"""
		Insert the URI parameter into the data.
		"""

		data = super(URIMixin, self).dehydrate(model, fields, exclude, relationship_prefix)

		try:
			data[self.uri_attribute_name] = self.get_model_resource_url(model, relationship=relationship_prefix)
		except ImproperlyConfigured:
			#we only pass this exception up if this is the root model.
			if relationship_prefix is None:
				raise

		return data





class JSONMixin(object):
	""" Mixin for working with JSON encoded data """

	def parse(self, data):
		return json.loads(data)

	def render(self, context):
		return json.dumps(context, indent=4)


class FlatFileMixin(object):
	def parse(self, data):
		input = StringIO(data)
		reader = csv.DictReader(input, delimiter=self.get_delimiter())

		data = list(reader)

		return data if len(data) > 1 else data[0]


	def render(self, context):
		output = StringIO()
		writer = csv.DictWriter(output, context.keys(), extrasaction='ignore', delimiter=self.get_delimiter())

		writer.writeheader()
		writer.writerows(context)

		return output.getvalue()


	def get_delimiter(self):
		return self.delimiter


class TSVMixin(FlatFileMixin):
	""" Mixin with your resource to IO in TSV """
	delimiter = '\t'

class CSVMixin(FlatFileMixin):
	""" Mixin with your resource to IO in CSV """
	delimiter = ','

