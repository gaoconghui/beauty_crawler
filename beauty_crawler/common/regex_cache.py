import re
import logging

logger = logging.getLogger(__name__)

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class RegexCache(Singleton):

    cache = {}

    def get_pattern(self, regex):
        if regex in self.cache:
            return self.cache.get(regex)
        else:
            pattern = re.compile(regex, re.DOTALL)
            self.cache[regex] = pattern
            return pattern

