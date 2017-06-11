# -*- coding: utf-8 -*-

rules = [
    {
        "domain": "mt.91.com",
        # list页面是入口，用于获取gallery
        "list": {
            "list_first_url": "http://mt.91.com/{listid}_1.html",
            "list_url": "http://mt.91.com/{listid}_{page}.html",
            "gallery_block": "//div[@class='yb_d top10 clearfix']/ul/li",
            "gallery_id": {
                "xpath": ".//a/@href",
                "regex": ".*91.*?(\d+).*"
            },
            "all_page": {
                "xpath": "//span[@class='pageinfo']/strong/text()",
                "regex": ".*?(\d+).*"
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
            "all_page": {
                "xpath": "//ul[@class='pagelist']/li/a/text()",
                "regex": ".*?(\d+).*"
            },
        }
    },

    {
        "domain": "www.7y7.com",

        # list页面是入口，用于获取gallery
        "list": {
            "list_url": "http://www.7y7.com/pic/{listid}/index_{page}.html",
            "all_page": {
                "xpath": "//a[@class='end']/text()",
                "regex": ".*?(\d+).*"
            },
            "gallery_block": "//ul[@id='piclist']/li",
            "gallery_id": {
                "xpath": ".//a/@href",
                "regex": ".*pic/(\d+.*?\d+).*"
            },
        },
        # 具体解析gallery页面，这是一页一张图的例子
        "gallery": {
            "gallery_url": "http://www.7y7.com/pic/{galleryid}_{page}.html",
            "image_block": "//ul[@class='pic-ul']/li",
            "image_url": ".//a/img/@src",
            "title": "//div[@class='pic-title']/h1/text()",
            "desc": ".//a/img/@alt",
            "need_flip": False,
        }
    },
    {
        "domain": "www.meizitu.com",
        "list": {
            "list_url": "http://www.meizitu.com/a/{listid}_{page}.html",
            "all_page": {
                "xpath": "//div[@id='wp_page_numbers']/ul/li[last()]/a/@href",
                "regex": ".*?(\d+).*"
            },
            "gallery_block": "//li[@class='wp-item']",
            "gallery_id": {
                "xpath": ".//h3[@class='tit']/a/@href",
                "regex": ".*?(\d+).*"
            },
        },
        "gallery": {
            "gallery_url": "http://www.meizitu.com/a/{galleryid}.html",
            "image_block": "//div[@id='picture']//img",
            "image_url": "./@src",
            "title": "//div[@class='metaRight']/h2/a/text()",
            "desc": "./@alt",
            "need_flip": False,
            "tags": "//div[@class='metaRight']/p/text()"
        }
    },

    {
        "domain": "pic.yesky.com",
        # list页面是入口，用于获取gallery
        "list": {
            "list_url": "http://pic.yesky.com/c/{listid}_{page}.shtml",
            "gallery_block": "//div[@class='lb_box']/dl",
            "gallery_id": {
                "xpath": ".//a/@href",
                "regex": ".*?(\d+/\d+).*"
            },
            "all_page": {
                "default" : 100 #需要增加无线翻页设置
            }
        },
        # 具体解析gallery页面，这是一页一张图的例子
        "gallery": {
            "gallery_first_url": "http://pic.yesky.com/{galleryid}.shtml",
            "gallery_url": "http://pic.yesky.com/{galleryid}_{page}.shtml",
            "image_url": "//div[@class='l_effect_img_mid']/a/img/@src",
            "title": "//div[@class='ll_img']/h2/a/text()",
            "publish_time": {
                "xpath": "//div[@class='l_con_title_right0']/span[1]/text()",
                "regex": ".*?(\d+-\d+-\d+ \d+:\d+).*",
            },
            "all_page": {
                "xpath": "//div[@class='viewport']/ul/li/a/span[@class='num']/text()",
                "regex": ".*?/(\d+).*"
            },
        }
    },
]
