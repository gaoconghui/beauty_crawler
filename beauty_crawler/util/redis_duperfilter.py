# -*- coding: utf-8 -*-
"""
    基于redis的简单去重服务

    从settings中读取配置:
    'REDIS_URL': 'url',
    'REDIS_HOST': 'host',
    'REDIS_PORT': 'port',
    dp = RedisDuperfilter.from_settings(settings, "DEDUP_DOUBAN_MOVIE")
    dp.is_new("value")

    or

    params = {
        # "REDIS_HOST" : "10.111.0.33"
    }
    dp = RedisDuperfilter.from_params(params)
    print dp.dedup_list(['aa','bb','aaa','bbb'])

    默认值为本地

"""
import logging

import redis
import six
from scrapy.utils.misc import load_object

__author__ = "gch"

DEFAULT_REDIS_CLS = redis.StrictRedis
# Sane connection defaults.
DEFAULT_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
}

# Shortcut maps 'setting name' -> 'parmater name'.
SETTINGS_PARAMS_MAP = {
    'REDIS_URL': 'url',
    'REDIS_HOST': 'host',
    'REDIS_PORT': 'port',
}


def get_redis_from_settings(settings):
    params = DEFAULT_PARAMS.copy()
    params.update(settings.getdict('REDIS_PARAMS'))
    for source, dest in SETTINGS_PARAMS_MAP.items():
        val = settings.get(source)
        if val:
            params[dest] = val

    # Allow ``redis_cls`` to be a path to a class.
    if isinstance(params.get('redis_cls'), six.string_types):
        params['redis_cls'] = load_object(params['redis_cls'])

    return get_redis(**params)


def get_redis_from_params(user_params):
    params = DEFAULT_PARAMS.copy()
    params.update(user_params)
    for source, dest in SETTINGS_PARAMS_MAP.items():
        val = settings.get(source)
        if val:
            params.pop(source)
            params[dest] = val

    # Allow ``redis_cls`` to be a path to a class.
    if isinstance(params.get('redis_cls'), six.string_types):
        params['redis_cls'] = load_object(params['redis_cls'])

    return get_redis(**params)


# Backwards compatible alias.
from_settings = get_redis_from_settings


def get_redis(**kwargs):
    """Returns a redis client instance.

    Parameters
    ----------
    redis_cls : class, optional
        Defaults to ``redis.StrictRedis``.
    url : str, optional
        If given, ``redis_cls.from_url`` is used to instantiate the class.
    **kwargs
        Extra parameters to be passed to the ``redis_cls`` class.

    Returns
    -------
    server
        Redis client instance.

    """
    redis_cls = kwargs.pop('redis_cls', DEFAULT_REDIS_CLS)
    url = kwargs.pop('url', None)
    if url:
        return redis_cls.from_url(url, **kwargs)
    else:
        return redis_cls(**kwargs)


logger = logging.getLogger(__name__)
DEFAULT_KEY = "REDIS_DEDUPFILTER_DETAULT"


class RedisDuperfilter(object):
    logger = logger

    def __init__(self, server, key=None):
        self.server = server
        if not key:
            self.key = DEFAULT_KEY
        else:
            self.key = key

    @classmethod
    def from_settings(cls, settings, key=None):
        server = get_redis_from_settings(settings)
        return cls(server, key=key)

    @classmethod
    def from_params(cls, user_params, key=None):
        server = get_redis_from_params(user_params)
        return cls(server, key=key)

    def is_new(self, value):
        if self.server.sadd(self.key, value):
            return True
        else:
            return False

    def dedup_list(self, values):
        dedup_list = []
        for item in values:
            if self.is_new(item):
                dedup_list.append(item)
        return dedup_list


if __name__ == '__main__':
    params = {
        # "REDIS_HOST" : "10.111.0.33"
    }
    settings = {"REDIS_PARAMS": params}
    dp = RedisDuperfilter.from_params(params)
    print dp.dedup_list(['aa', 'bb', 'aaa', 'bbb'])
