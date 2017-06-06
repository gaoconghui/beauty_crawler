# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from beauty_crawler.dao.mysql import Gallery, Image
from beauty_crawler.items import GalleryItem, ImageItem
from scrapy.exporters import BaseItemExporter


class BeautyCrawlerPipeline(object):
    def __init__(self):
        self.exporter = BaseItemExporter()

    def process_item(self, item, spider):
        if isinstance(item, GalleryItem):
            self.process_gallery(item)
        if isinstance(item, ImageItem):
            self.process_image(item)
        return item

    def process_gallery(self, item):
        json_item = dict(self.exporter._get_serialized_fields(item))
        Gallery(**json_item).save()

    def process_image(self, item):
        json_item = dict(self.exporter._get_serialized_fields(item))
        Image(**json_item).save()
