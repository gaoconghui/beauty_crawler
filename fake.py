# -*- coding: utf-8 -*-
"""
模拟发送任务
"""
import json

import redis


def load_fake_seed_task():
    task = {
        "_id": "mt.91.com___meinv/xiangchemeinv/list_29",
        "domain": "mt.91.com",
        "extends" : {
            "tags" : ["香车美女"]
        }
    }
    return task


if __name__ == '__main__':
    r = redis.Redis()
    r.delete("beauty")
    r.delete("beautyqueue")
    r.lpush("beauty", json.dumps(load_fake_seed_task()))
