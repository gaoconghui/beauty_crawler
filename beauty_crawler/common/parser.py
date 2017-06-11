# -*- coding: utf-8 -*-
"""
解析器
"""
import logging
import re

from beauty_crawler.common.normalizer import DateNormalizor, ListNormalizor
from beauty_crawler.common.regex_cache import RegexCache
from beauty_crawler.util.date_util import norm_date

logger = logging.getLogger(__name__)


class RuleParser:
    def __init__(self, rule):
        self.rule = rule

    def parse(self, response):
        pass


class ListParser(RuleParser):
    def __init__(self, rule):
        RuleParser.__init__(self, rule)
        self.block = ExtractField(name="block", rule=rule.get("gallery_block"), result_type=ExtractRuleType.NODES)
        self.gallery_id = ExtractField(name="gallery_id", rule=rule.get("gallery_id"), result_type=ExtractRuleType.STR)
        self.all_page = ExtractField(name="all_page", rule=rule.get("all_page"), result_type=ExtractRuleType.STR)

    def parse(self, response):
        """
        从list页面解析出需要的字段
        :param response:
        :return:
        """
        items = []
        blocks = self.block.extract(response)
        for block in blocks:
            item = {"_id": self.gallery_id.extract(block)}
            items.append(item)
        all_page = self.all_page.extract(response)
        return items, all_page


class GalleryParser(RuleParser):
    def __init__(self, rule):
        RuleParser.__init__(self, rule)
        self.title = ExtractField(name="title", rule=rule.get("title"), result_type=ExtractRuleType.STR)
        self.publish_time = ExtractField(name="publish_time", essential=False, rule=rule.get("publish_time", ),
                                         result_type=ExtractRuleType.STR, normalizor=DateNormalizor())
        self.all_page = ExtractField(name="all_page", rule=rule.get("all_page"), result_type=ExtractRuleType.STR)
        self.image_url = ExtractField(name="image_url", rule=rule.get("image_url"), result_type=ExtractRuleType.STR)
        self.desc = ExtractField(name="desc", rule=rule.get("desc"), essential=False, result_type=ExtractRuleType.STR)
        self.tags = ExtractField(name="tags", rule=rule.get("tags"), essential=False, result_type=ExtractRuleType.STR,
                                 normalizor=ListNormalizor())
        self.image_block = ExtractField(name="image_block", rule=rule.get("image_block"),
                                        result_type=ExtractRuleType.NODES)

    def parse(self, response):
        """
        从list页面解析出需要的字段
        :param response:
        :return:
        """

        def extract_singal(selector):
            item = {
                "title": self.title.extract(selector),
                "publish_time": self.publish_time.extract(selector),
                "all_page": self.all_page.extract(selector),
                "image_url": self.image_url.extract(selector),
                "desc": self.desc.extract(selector),
                "tags": self.tags.extract(selector)
            }
            return item

        items = []
        if self.image_block.rule is not None:
            blocks = self.image_block.extract(response)
            for block in blocks:
                items.append(extract_singal(block))
        else:
            items.append(extract_singal(response))
        return items


class ExtractRuleType(object):
    STR = 0x01
    NODES = 0x02
    STRS = 0x03
    JSONITEM = 0x04


class EmptyFieldException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ExtractField(object):
    name = None
    rule = None

    def __init__(self, name, rule, result_type=ExtractRuleType.STR, essential=True, normalizor=None, validator=None):
        self.name = name
        self.rule = rule
        self.essential = essential
        self.normalizor = normalizor
        self.extract_rule = ExtractRule(rule, result_type)
        self.validator = validator

    def extract(self, selector):
        logger.debug("---------1----------start extract {name}".format(name=self.name))
        if not self.rule:
            return None
        logger.debug("---------2-----------using rule {rule}".format(rule=self.rule))
        result = self.extract_rule.extract(selector)
        if result and self.normalizor:
            result = self.normalizor.normalize(result)
        if not result and isinstance(self.rule, dict) and 'default' in self.rule:
            return self.rule.get('default')
        if not result and self.essential:
            raise EmptyFieldException(self.name)
        if self.validator and not self.validator.isvalid(result):
            raise EmptyFieldException(self.name)
        return result


class ExtractRule(object):
    """
    按照规则具体抽取内容
    """
    xpath = None
    regex = None
    ops = None

    def __init__(self, rules, result_type=ExtractRuleType.STR):
        if not rules:
            return
        self.result_type = result_type
        self.rules = rules
        self.regex_cache = RegexCache()
        if isinstance(rules, basestring):
            self.xpath = rules
        elif isinstance(rules, list):
            self.xpath = rules
        elif isinstance(rules, dict):
            self.xpath = rules.get('xpath', None)
            self.regex = rules.get('regex', None)
            self.ops = rules.get('ops', None)
        else:
            logger.error('invalid rules : %s' % rules)
        self.__compile_regex()

    def __compile_regex(self):
        if not self.regex:
            return
        regex_cache = RegexCache()
        if isinstance(self.regex, basestring):
            return regex_cache.get_pattern(self.regex)
        elif isinstance(self.regex, list):
            patterns = []
            for s in self.regex:
                pattern = regex_cache.get_pattern(s)
                patterns.append(pattern)
            return patterns

    def extract(self, selector):
        try:
            if self.result_type == ExtractRuleType.STR:
                return self.extract_str(selector)
            elif self.result_type == ExtractRuleType.NODES:
                return self.extract_nodes(selector)
            elif self.result_type == ExtractRuleType.STRS:
                return self.extract_strs(selector)
            else:
                raise RuntimeError()
        except Exception, e:
            logger.debug('exception : %s' % e)
            return

    def extract_strs(self, selector):
        res = None
        if isinstance(self.xpath, basestring):
            res = selector.xpath(self.xpath).extract()
        elif isinstance(self.xpath, list):
            for xpath in self.xpath:
                res = selector.xpath(xpath).extract()
                if res:
                    break
        if res:
            res = [self.__do_regex_and_ops(r) for r in res]
            return res

    def extract_str(self, selector):
        res = None

        def xpath_extract(xpath, selector):
            if xpath.endswith('node()'):
                res = selector.xpath(xpath).extract()
                if res:
                    return ''.join(res)
            else:
                return selector.xpath(xpath).extract_first()

        # xpath rule
        if isinstance(self.xpath, basestring):
            res = xpath_extract(self.xpath, selector)
        elif isinstance(self.xpath, list):
            for xpath in self.xpath:
                res = xpath_extract(xpath, selector)
                if res:
                    break
        if res:
            logger.debug("-------------3-------------  get " + res)
            return self.__do_regex_and_ops(res)

    def __do_regex_and_ops(self, res):
        # regex rule
        if isinstance(self.regex, basestring):
            if self.xpath and res:
                if 'rep' in self.rules:
                    res = re.sub(self.regex_cache.get_pattern(self.regex),
                                 self.rules.get('rep'),
                                 res)
                else:
                    match = re.match(self.regex_cache.get_pattern(self.regex), res)
                    if match:
                        res = ''.join(match.groups())
        elif isinstance(self.regex, list):
            for regex in self.regex:
                if self.xpath and res:
                    match = re.match(self.regex_cache.get_pattern(regex), res)
                    if match:
                        res = ''.join(match.groups())
                if res:
                    break

        # ops rule
        if not res:  # ensure res is ready
            return

        if isinstance(self.ops, dict):
            if 'divide' in self.ops:
                try:
                    res = int(res)
                except Exception:
                    return
                res = int(res / self.ops.get('divide'))
            if 'minus' in self.ops:
                try:
                    res = int(res)
                except Exception:
                    return
                res = int(res - self.ops.get('minus'))
            elif 'date' in self.ops:
                res = norm_date(res, self.ops.get('date'))
            elif 'pre' in self.ops:
                res = self.ops.get('pre') + res
        return res

    def extract_nodes(self, selector):
        if isinstance(self.xpath, basestring):
            return selector.xpath(self.xpath)
        elif isinstance(self.xpath, list):
            for xpath in self.xpath:
                res = selector.xpath(xpath)
                if res:
                    return res
