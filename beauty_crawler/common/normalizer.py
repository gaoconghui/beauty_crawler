# -*- coding: utf-8 -*-
import re
import HTMLParser
import logging
from urlparse import urljoin

import time

from beauty_crawler.util.date_util import norm_date

logger = logging.getLogger(__name__)

HTML_TAG_RE = re.compile(r'<[^>]+>')

INVALID_RE = [
    r'\s+',
    r'\r+',
    r'\n+',
]

INVALID_PATTERNS = []
for re_txt in INVALID_RE:
    INVALID_PATTERNS.append(re.compile(re_txt))

def decodehtml(text):
    h= HTMLParser.HTMLParser()
    return h.unescape(text)

def remove_tags(text):
    result = HTML_TAG_RE.sub('', text)
    return decodehtml(result)

def clean_html_tags(text):
    if not text:
        return text
    text = remove_tags(text)
    for pattern in INVALID_PATTERNS:
        text = pattern.sub('', text)
    return text

URL_REGEX_PATTERN = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def is_valid_url(url):
    return URL_REGEX_PATTERN.match(url)

class Normalizor(object):

    def __init__(self):
        pass

    def normalize(self, obj):
        raise NotImplementedError()


class DateNormalizor(Normalizor):
    def normalize(self, obj):
        if isinstance(obj,unicode):
            obj = norm_date(obj,None)
        ts = int(time.mktime(obj.timetuple()))
        if ts > int(time.time()):
            ts -= 365 * 86400
        return ts

class CleanHTMLNormalizor(Normalizor):

    def normalize(self, obj):
        return clean_html_tags(obj)

class FulfillUrlNormalizor(Normalizor):

    def __init__(self, host):
        self.host = host

    def normalize_url(self, url):
        if not url or url.startswith('http'):
            return url
        if not url.startswith('/'):
            url = '/' + url
        if url.startswith('//'):
            url = 'http:' + url
        else:
            url = 'http://' + self.host + url
        if is_valid_url(url):
            return url

    def normalize(self, obj):
        if isinstance(obj, basestring):
            return self.normalize_url(obj)
        elif isinstance(obj, list):
            res_list = []
            for url in obj:
                if isinstance(url, basestring):
                    res = self.normalize_url(url)
                    if res:
                        res_list.append(res)
                else:
                    logger.error('failed, invalid url : %s' % url)
            return res_list

class FulfillRelativeUrlNormalizor(Normalizor):

    def __init__(self, linkspre):
        self.linkspre = linkspre

    def normalize_url(self, url):
        if not url or url.startswith('http'):
            return url
        url = urljoin(self.linkspre, url)
        if is_valid_url(url):
            return url

    def normalize(self, obj):
        if isinstance(obj, basestring):
            return self.normalize_url(obj)
        elif isinstance(obj, list):
            res_list = []
            for url in obj:
                if isinstance(url, basestring):
                    res = self.normalize_url(url)
                    if res:
                        res_list.append(res)
                else:
                    logger.error('failed, invalid url : %s' % url)
            return res_list

class IntNormalizor(Normalizor):

    def normalize(self, obj):
        if isinstance(obj, int):
            return obj
        else:
            try:
                return int(obj)
            except Exception:
                return

