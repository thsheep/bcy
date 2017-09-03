#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: 哎哟卧槽
@license: Apache Licence 
@file: run.py
@time: 2017/9/3 12:31
"""
from scrapy.cmdline import execute


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'bcy'])