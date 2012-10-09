#django-sliver
###Lightweight REST API for Django built on top of generic views

----

###Why django-sliver?

Sliver was designed for sites that just need a simple API for their front-end ([backbone](https://github.com/documentcloud/backbone), etc), without all the bells and whistles (and headaches :) of a solution like [django-tastypie](https://github.com/toastdriven/django-tastypie).

Some things to note:

* It's built on top of Django's generic views, so a lot of the methods you are used to overriding are here.
* It only works with Django's ORM, and there are no plans to expand on that.
* It provides no authentication/authorization systems, instead relying on whatever auth backend you have to do the heavy lifting.
* Like the generic views, it relies heavily on mixins to provide additional functionality.

----

###Requirements

There are no dependencies beyond having django >= 1.3

----

###Installation

```pip install -e git+git@github.com:jarcoal/django-sliver.git#egg=django-sliver```

----

###Getting started

There are two main views that will be important to you.  Remember, they both inherit from Django's [View](https://github.com/django/django/blob/master/django/views/generic/base.py) class, so you can override `dispatch()`, `get()`, `post()`, etc, whenever you want.

####sliver.views.ModelResource

ModelResource is designed to handle requests relating to a single model object.  It's mixed with Django's [SingleObjectMixin](https://github.com/django/django/blob/master/django/views/generic/detail.py), so methods like `get_object()` and `get_querset()` can easily be overrided.

####sliver.views.CollectionResource

CollectionResource is designed to handle requests relating to a collection of model objects.  Similar to ModelResource, it mixes with Django's [MultipleObjectMixin](https://github.com/django/django/blob/master/django/views/generic/list.py), so those methods are available.