import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.conf import settings
settings.configure(**{
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    },
    'LOGGING_CONFIG': {},
})

import django.core.cache

import django.test

from datetime import timedelta
import time

from django_singlevalue_cache import *


class SingleValueCacheTest(django.test.TestCase):

    def setUp(self):
        django.core.cache.cache.clear()

    def test_timeout(self):

        i = [0]
        @cache_single_value(key='a',
                            timeout=timedelta(seconds=.2))
        def foo():
            i[0] += 1
            return i[0]

        self.assertEqual(foo(), 1)
        self.assertEqual(foo(), 1)
        time.sleep(.1)
        self.assertEqual(foo(), 1)
        time.sleep(.2)
        self.assertEqual(foo(), 2)
        self.assertEqual(foo(), 2)

    def test_backoff(self):

        i = [0]
        @cache_single_value(key='a',
                            timeout=timedelta(seconds=.2),
                            backoff=timedelta(seconds=.2))
        def foo():
            i[0] += 1
            if i[0] % 2 == 0:
                raise
            return i[0]

        self.assertEqual(foo(), 1)
        self.assertEqual(foo(), 1)
        time.sleep(.3)
        self.assertEqual(foo(), None)
        self.assertEqual(foo(), None)
        time.sleep(.2)
        self.assertEqual(foo(), 3)
        self.assertEqual(foo(), 3)
