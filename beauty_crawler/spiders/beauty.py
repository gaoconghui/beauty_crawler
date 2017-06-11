# -*- coding: utf-8 -*-

import json
import logging
import time

from scrapy import Request
from scrapy.conf import settings
from scrapy_redis.spiders import RedisSpider

from beauty_crawler.common.rule_manager import RuleManager
from beauty_crawler.items import GalleryItem, ImageItem
from beauty_crawler.util.redis_duperfilter import RedisDuperfilter

logger = logging.getLogger(__name__)


class Beauty(RedisSpider):
    name = "beauty"
    redis_key = "beauty"

    def __init__(self, **kwargs):
        super(Beauty, self).__init__(**kwargs)
        self.rule_manager = RuleManager()
        self.dp = RedisDuperfilter.from_settings(settings, "DEDUP_BEAUTY")

    custom_settings = {
        'SCHEDULER': 'scrapy_redis.scheduler.Scheduler',
        'SCHEDULER_PERSIST': True,
        'SCHEDULER_QUEUE_KEY': 'beautyqueue',

        "ITEM_PIPELINES": {
            'beauty_crawler.pipelines.BeautyCrawlerPipeline': 300,
        }
    }

    def gen_request_from_url(self, url, meta=None):
        logger.debug("gen list url {url}".format(url=url))
        return Request(url, meta=meta, callback=self.parse_list, dont_filter=True)

    def next_request(self):
        """
        load seed
        :return:
        """
        task = self.server.rpop(self.redis_key)
        if not task:
            return None
        try:
            task = json.loads(task)
        except Exception:
            self.logger.error('invalid task : %s' % task)
            return
        else:
            self.logger.debug('got task : %s' % task)
            meta = {'task': task, 'domain': task['domain'], "page": 1}
            return self.gen_request_from_url(self.rule_manager.gen_list_url(task, page=1), meta)

    def parse_list(self, response):
        meta = response.meta.copy()
        task = meta.get("task")
        # list页面解析，获取直接能获取的字段
        list_items, all_page = self.rule_manager.parse_list(task, response)
        # 字段加工，增加额外的字段
        for item in list_items:
            item['insert_time'] = int(time.time())
            item['from_id'] = task.get("_id")
            item['domain'] = task.get("domain")
            # 继承seed中extend里的元素
            self.__append_extend(item, task.get("extends", {}))
            item['order'] = 1
            item['gallery_id'] = item['from_id'] + "___" + item['_id']
            url = self.rule_manager.gen_detail_url(item, page=1)
            yield Request(url, meta={"gallery": item}, callback=self.parse_gallery, dont_filter=True)
        now_page = meta.get("page")
        if now_page < all_page:
            meta['page'] = now_page + 1
            yield self.gen_request_from_url(self.rule_manager.gen_list_url(task, page=now_page + 1), meta)

    def parse_gallery(self, response):
        gallery = response.meta.copy().get("gallery")
        now_page = gallery.get("order")
        image_items = self.rule_manager.parse_detail(gallery, response)
        for index, item in enumerate(image_items):
            item["gallery_id"] = gallery.get("gallery_id")
            item['order'] = self.rule_manager.order_calculate(gallery, now_page, index)
            yield self.__gen_image_item(item)
        if len(image_items) >= 1:
            first_image = image_items[0]
            # 第一页需要抛出gallery
            if now_page == 1:
                yield self.__gen_gallery_item(gallery, first_image)
            # 是否需要翻页
            if self.rule_manager.need_flip(gallery):
                all_page = int(first_image.get("all_page"))
                if now_page < all_page:
                    url = self.rule_manager.gen_detail_url(gallery, page=now_page + 1)
                    gallery['order'] = now_page + 1
                    yield Request(url, meta={"gallery": gallery}, callback=self.parse_gallery, dont_filter=True)
                else:
                    logger.info("get all image for gallery {gallery}".format(gallery=gallery.get("gallery_id")))

    def __gen_gallery_item(self, gallery_item, first_image):
        gallery = GalleryItem()
        for k in gallery.fields.keys():
            if k in gallery_item and gallery_item[k] is not None:
                gallery[k] = gallery_item[k]
            elif k in first_image and first_image[k] is not None:
                gallery[k] = first_image[k]
        # 特殊处理tags
        if "tags" in first_image and first_image['tags'] is not None:
            tags = list(set(gallery_item.get("tags", []) + first_image.get("tags", [])))
            gallery['tags'] = tags
        return gallery

    def __gen_image_item(self, item):
        image = ImageItem()
        for k in image.fields.keys():
            if k in item and item[k] is not None:
                image[k] = item[k]
        return image

    def __append_extend(self, _to, _from):
        for k, v in _from.iteritems():
            if isinstance(v, basestring):
                if k not in _to:
                    _to[k] = v
            if isinstance(v, list):
                _to[k] = _to.get(k, []) + v
        return _to
