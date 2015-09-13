from __future__ import absolute_import

__all__ = ['cache_single_value']

import collections
import functools

import django.core.cache

CachedValue = collections.namedtuple('CachedValue', ['value', 'type'])

CacheConfig = collections.namedtuple(
    'CacheConfig',
    ['skip_cache', 'key', 'timeout', 'backoff']
)


def get_cached_value(config):
    x = django.core.cache.cache.get(config.key)
    if x is not None:
        assert isinstance(x, CachedValue)
        return None if x.type == 'wait' else x.value
    else:
        try:
            return load(config)
        except:
            initiate_backoff(config)


def load(config):
    value = config.skip_cache()
    timeout_seconds = config.timeout.total_seconds()
    if timeout_seconds > 0:
        x = CachedValue(value=value, type='value')
        django.core.cache.cache.set(config.key, x, timeout_seconds)
    return value


def initiate_backoff(config):
    if config.backoff is None:
        return
    backoff_seconds = config.backoff.total_seconds()
    if backoff_seconds > 0:
        x = CachedValue(value=None, type='wait')
        django.core.cache.cache.set(config.key, x, backoff_seconds)


def cache_single_value(key, min_timeout, max_timeout, backoff=None):
    """
    key (string)
        Prefix for keys used to store this value in the cache.

    min_timeout (datetime.timedelta)
        How long before a cached value may be replaced.

    max_timeout (datetime.timedelta)
        How long before a cached value must be evicted.

    backoff (datetime.timedelta)
        How long to wait before retrying after the function raises.
    """
    def decorate(f):
        config = CacheConfig(
            skip_cache=f, key=key, min_timeout=min_timeout,
            max_timeout=max_timeout, backoff=backoff)
        return functools.wraps(f)(lambda: get_cached_value(config))

    return decorate
