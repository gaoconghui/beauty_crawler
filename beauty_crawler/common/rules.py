# -*- coding: utf-8 -*-

rules = [
{
    "domain": "mt.91.com",

    # list页面是入口，用于获取gallery
    "list": {
        "list_first_url" : "http://mt.91.com/{listid}_1.html",
        "list_url": "http://mt.91.com/{listid}_{page}.html",
        "pages": {
            "default": 20,
        },
        "gallery_block": "//div[@class='yb_d top10 clearfix']/ul/li",
        "gallery_id": {
            "xpath": ".//a/@href",
            "regex": ".*91.*?(\d+).*"
        },
        "all_page" : {
            "xpath" : "//span[@class='pageinfo']/strong/text()",
            "regex" : ".*?(\d+).*"
        }
    },
    # 具体解析gallery页面，这是一页一张图的例子
    "gallery": {
        "gallery_first_url": "http://mt.91.com/meinv/xiangchemeinv/{galleryid}.html",
        "gallery_url": "http://mt.91.com/meinv/xiangchemeinv/{galleryid}_{page}.html",
        "image_url": "//img[@id='bigimg']/@src",
        "title": ".//div[@class='tb_005']/h2/text()",
        "publish_time": {
            "xpath": "//div[@class='tb_005']/p/text()",
            "regex": ".*?(\d+-\d+-\d+ \d+:\d+).*",
        },
        "all_page" : {
            "xpath" : "//ul[@class='pagelist']/li/a/text()",
            "regex" : ".*?(\d+).*"
        },
    }

}
]
