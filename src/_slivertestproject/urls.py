from django.conf.urls import url

from app.views import PersonCollectionResource, PersonResource

urlpatterns = [
	url(r'^people/$', PersonCollectionResource.as_view(), name='api-people-collection'),
	url(r'^people/(?P<pk>\d+)/$', PersonResource.as_view(), name='api-people-model'),
]
