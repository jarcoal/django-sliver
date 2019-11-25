[![Build Status](https://travis-ci.org/supervacuo/django-sliver.svg?branch=master)](https://travis-ci.org/supervacuo/django-sliver)

# django-sliver
### Lightweight REST API for Django built on top of generic views

----

### Why django-sliver?

Sliver was designed for sites that just need a simple API for their front-end ([backbone](https://github.com/documentcloud/backbone), etc), without all the bells and whistles (and headaches :) of a solution like [django-tastypie](https://github.com/toastdriven/django-tastypie).

Some things to note:

* It's built on top of Django's generic views, so a lot of the methods you are used to overriding are here.
* It only works with Django's ORM, and there are no plans to expand on that.
* It provides no authentication/authorization systems, instead relying on whatever auth backend you have to do the heavy lifting.
* Like the generic views, it relies heavily on mixins to provide additional functionality.

----

### Requirements

There are no dependencies beyond having django >= 1.3

----

### Installation

```pip install -e git+git@github.com:jarcoal/django-sliver.git#egg=django-sliver```

----

###What's it look like?

views.py
```python
# sliver objects
from sliver.views import ModelResource, CollectionResource
from sliver.mixins import JSONMixin

# your data
from products.models import Product


class ProductCollectionResource(JSONMixin, CollectionResource):
	model = Product

class ProductResource(JSONMixin, ModelResource):
	model = Product
```

urls.py
```python
from django.conf.urls import patterns, url
from views import ProductCollectionResource, ProductResource

urlpatterns = patterns('',
	url(r'^products/$', ProductCollectionResource.as_view(), name='api-products-collection'),
	url(r'^products/(?P<pk>\d+)/$', ProductResource.as_view(), name='api-products-model'),
)
```

That's all you need for a basic JSON API.

----

###Views

There are two main views that will be important to you.  Remember, they both inherit from Django's [View](https://github.com/django/django/blob/master/django/views/generic/base.py) class, so you can override `dispatch()`, `get()`, `post()`, etc, whenever you want.

####sliver.views.ModelResource

ModelResource is designed to handle requests relating to a single model object.  It's mixed with Django's [SingleObjectMixin](https://github.com/django/django/blob/master/django/views/generic/detail.py), so methods like `get_object()` and `get_queryset()` can easily be overrided.

####sliver.views.CollectionResource

CollectionResource is designed to handle requests relating to a collection of model objects.  Similar to ModelResource, it mixes with Django's [MultipleObjectMixin](https://github.com/django/django/blob/master/django/views/generic/list.py), so those methods are available.

----

###Limiting incoming/outgoing fields

Handling which fields are shown / updateable is just like using Django's form views.  Continuing our example:

```python
class ProductCollectionResource(JSONMixin, CollectionResource):
	#this will limit the output to these three fields.  it will restrict updates to just them as well.
	fields = ['id', 'name', 'description']

	#like form views, exclude also works
	exclude = ['secret_key']
```

----

###Serializing / Unserializing

Serializing is really up to you; the bare resources don't implement anything in particular. There is a JSONMixin provided that you can add to your resource that will aide in parsing/rendering your resource in JSON.

When a request comes in, the `parse()` method on your resource will be called with `request.body` passed to it.  Here is an example for JSON:

```python
def parse(self, raw_data):
	return json.loads(raw_data)
```

NOTE: If `request.body` isn't all you need to parse a request, remember this is just a generic view, the request object is available at `self.request`.

When a response is ready to go out, the `render()` method is called on your resource.  Again, a JSON example:

```python
def render(self, data):
	return json.dumps(data)
```

----

###Filtering

Filtering can easily be applied by overriding `get_queryset()` and applying your own logic.  However, if you need a simple solution, you can add the `FiltersMixin` to your resource (usually on collection).  Continuing our basic example from above:

```python
from sliver.mixins import FiltersMixin

class ProductCollectionResource(FiltersMixin, JSONMixin, CollectionResource):
	filters = ['name__contains', 'date_added__gt']
```

All filters must be specified in the `filters` attribute, otherwise they are ignored.

If you need more advanced filtering, you can override `get_filters()` which should return a dictionary of filters that will be applied to the queryset.  You can go one step further than that by overriding the `get_queryset()` method and doing exactly what you want with the queryset.

----

###Relationships

Relationships are always a trick in APIs, so I've tried to make them as simple as possible.  Both to-one and to-many relationships are possible.  Example:

```python
class ProductResource(JSONMixin, CollectionResource):
	model = Product

	relationships = {
		'vendor': {},			#to-one
		'feature_set': {}		#to-many
	}
```

If you need to exclude some fields from your related models, that can easily be done:

```python
relationships = {
	'vendor': {
		'exclude': ['private_notes']
	},
	'feature_set': {
		'fields': ['id', 'name']
	}
}
```

Deeper relationships are denoted by double underscores:

```python
relationships = {
	'vendor': {},
	'vendor__parent_company': {}
}
```

----

###URIs

By default, the resources will not insert any URIs into the responses.  For many, this is fine, but not all.  Sliver ships with a `URIMixin` that provides this functionality.  Example:

```python
class ProductCollectionResource(URIMixin, JSONMixin, CollectionResource):
	#this should be the 'name' parameter you used in your URL patterns
	model_resource_name = 'api-product-model'

	#this is the name of the attribute you want serialized into your responses
	uri_attribute_name = '_uri'
```

This is nice, but it won't insert URIs into related objects.  This will:

```python
relationships = {
	'vendor': {
		'model_resource_name': 'api-vendor-model'
	}
}
```
