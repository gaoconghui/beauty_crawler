# -*- coding: utf-8 -*-
"""
id 生成器
"""

def gen_gallery_id(task,_id):
    seed_id = task.get("_id")
    return seed_id + "___" + _id