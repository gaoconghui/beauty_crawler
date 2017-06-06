# -*- coding: utf-8 -*-
"""
模拟发送任务
"""
import json
from optparse import OptionParser

import redis

from seed import seeds

r = redis.Redis()


def clean():
    r.delete("beauty")
    r.delete("beautyqueue")


def main(domain):
    clean()
    task = [s for s in seeds if s.get("domain") == domain]
    print task[0]
    r.lpush("beauty", json.dumps(task[0]))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--domain', dest='domain',
                      help='seed domain')
    (options, args) = parser.parse_args()
    main(options.domain)
