from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed


class SliverResponse(Exception):
	pass

class HttpResponseBadRequest(SliverResponse):
	response = HttpResponseBadRequest


class HttpResponseUnauthorized(SliverResponse):
	response = HttpResponseNotAllowed