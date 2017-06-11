# -*- coding: utf-8 -*-
import rules
from beauty_crawler.common.parser import GalleryParser
from beauty_crawler.common.parser import ListParser


class RuleManager:
    def __init__(self):
        self.rules_map = {}
        self.list_parser_map = {}
        self.gallery_parser_map = {}
        self.__load_rules()

    def __load_rules(self):
        for rule in rules.rules:
            self.rules_map[rule.get("domain", "")] = rule
            self.list_parser_map[rule.get("domain")] = ListParser(rule.get("list"))
            self.gallery_parser_map[rule.get("domain")] = GalleryParser(rule.get("gallery"))

    def gen_list_url(self, task, page=1):
        """
        :param task:
        :return:
        """
        _id = task.get("_id")
        domain, _id = _id.split("___")
        rule = self.rules_map.get(domain, {}).get("list", {})
        if page == 1:
            url = rule.get("list_first_url", rule.get("list_url", "")).format(listid=_id, page=page)
        else:
            url = rule.get("list_url").format(listid=_id, page=page)
        return url

    def gen_detail_url(self, task, page=1):
        """
        {'_id': u'2013072321592409', 'insert_time': 1496670529, 'from_id': u'mt.91.com___meinv/xiangchemeinv/list_29'}
        :param task:
        :return:
        """
        from_id = task.get("from_id")
        domain, _ = from_id.split("___")
        rule = self.rules_map.get(domain, {}).get("gallery", {})
        if page == 1:
            url = rule.get("gallery_first_url", rule.get("gallery_url", "")).format(galleryid=task.get("_id"),
                                                                                    page=page)
        else:
            url = rule.get("gallery_url", "").format(galleryid=task.get("_id"), page=page)
        return url

    def parse_list(self, task, response):
        domain = task.get("domain")
        items, all_page = self.list_parser_map.get(domain).parse(response)
        return items, int(all_page)

    def parse_detail(self, task, response):
        domain, _id = task.get("from_id").split("___")
        items = self.gallery_parser_map.get(domain).parse(response)
        return items

    def need_flip(self, gallery):
        domain = gallery.get("domain")
        return self.rules_map.get(domain).get("gallery", {}).get("need_flip", True)

    def order_calculate(self, gallery, now_page, index):
        """
        计算图片的order值
        :param gallery: 图集属性
        :param now_page: 爬取到图片的页数
        :param index: 该页中的第几个图片，从0开始
        :return:
        """
        if not self.need_flip(gallery):
            return index + 1
        else:
            return (now_page - 1) * 100 + index + 1
