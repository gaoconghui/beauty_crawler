# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BeautyCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class GalleryItem(scrapy.Item):
    title = scrapy.Field()
    domain = scrapy.Field()
    insert_time = scrapy.Field()
    gallery_id = scrapy.Field()
    all_page = scrapy.Field()
    tags = scrapy.Field()
    publish_time = scrapy.Field()
    from_id = scrapy.Field()


class ImageItem(scrapy.Item):
    image_url = scrapy.Field()
    title = scrapy.Field()
    desc = scrapy.Field()
    order = scrapy.Field()
    gallery_id = scrapy.Field()
