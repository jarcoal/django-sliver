#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for sliver."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import six

from django.urls import reverse
from django.test import TestCase


class SimpleTest(TestCase):
    def test_dummy(self):
        """Just see if the import works as expected."""
        import sliver

    def test_collection(self):
        from _slivertestproject.app.models import Person
        person = Person.objects.create(name='Juan')
        r = self.client.get(
            reverse('api-people-collection')
        )

        self.assertEqual(
            json.loads(r.content),
            [{'name': 'Juan', 'id': 1}]
        )

    def test_model(self):
        from _slivertestproject.app.models import Person
        person = Person.objects.create(name='Juan')
        r = self.client.get(
            reverse('api-people-model', kwargs={'pk': person.pk})
        )

        self.assertEqual(
            json.loads(r.content),
            {'name': 'Juan', 'id': 1}
        )
