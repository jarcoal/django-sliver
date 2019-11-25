#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 by Łukasz Langa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from unittest.loader import defaultTestLoader

from django.conf import settings
from django.test import TestCase

try:
    # Added in Django 1.6
    from django.test.runner import DiscoverRunner
    class DiscoveryDjangoTestSuiteRunner(DiscoverRunner):
        """Unfortunately the new DiscoverRunner doesn't handle custom top level
        correctly."""
        def __init__(
            self, pattern=None, top_level=None, verbosity=1, interactive=True,
            failfast=False, **kwargs
        ):
            self.test_label_default = settings.TEST_DISCOVERY_ROOT
            if not top_level:
                top_level = self.test_label_default
            super(DiscoveryDjangoTestSuiteRunner, self).__init__(
                pattern=pattern, top_level=top_level, verbosity=verbosity,
                interactive=interactive, failfast=failfast, **kwargs
            )

        def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
            if not test_labels:
                test_labels = [self.test_label_default]
            return super(DiscoveryDjangoTestSuiteRunner, self).build_suite(
                test_labels=test_labels, extra_tests=extra_tests, **kwargs
            )

except ImportError:
    # Django < 1.6 compatibility
    from django.utils.importlib import import_module
    from django.test.simple import DjangoTestSuiteRunner
    class DiscoveryDjangoTestSuiteRunner(DjangoTestSuiteRunner):
        """A test suite runner that uses unittest2 test discovery.
        Courtesy of @carljm."""

        def build_suite(self, test_labels, extra_tests=None, **kwargs):
            suite = None
            discovery_root = settings.TEST_DISCOVERY_ROOT

            if test_labels:
                suite = defaultTestLoader.loadTestsFromNames(test_labels)
                # if single named module has no tests, do discovery within it
                if not suite.countTestCases() and len(test_labels) == 1:
                    suite = None
                    discovery_root = import_module(test_labels[0]).__path__[0]

            if suite is None:
                suite = defaultTestLoader.discover(
                    discovery_root,
                    top_level_dir=settings.BASE_PATH,
                )

            if extra_tests:
                for test in extra_tests:
                    suite.addTest(test)

            from django.test.simple import reorder_suite  # Django 1.5 and lower
            return reorder_suite(suite, (TestCase,))
