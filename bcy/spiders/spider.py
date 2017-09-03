#!/usr/bin/env python
# encoding: utf-8
"""
@version: ??
@author: 哎哟卧槽
@license: Apache Licence 
@file: spider.py
@time: 2017/9/2 23:32
"""
import re
import json
from datetime import datetime
from scrapy.spiders import Spider
from scrapy import Request
from scrapy.cmdline import execute
from bcy.config import *
from bcy.login import post

# 关注页面
follow_url = 'https://bcy.net{}/following'
# Cos作品集页面
works_url = 'https://bcy.net{}/post/cos'
# 基准URL
bash_url = 'https://bcy.net{}'


class Bcy_Spider(Spider):

    name = 'bcy'

    def start_requests(self):
        yield Request(start_user_url, callback=self.follow, dont_filter=True)

    def follow(self, response):
        """解析关注的人
        :param response:
        :return:
        """
        users = response.xpath("./*//i[@class='l-left i-new-sex-{}']/preceding-sibling::a/@href".format(sex)).extract()
        # 进入cos作品集
        yield from [Request(works_url.format(user), callback=self.works_cos, dont_filter=True) for user in users]
        # 继续追踪关注
        yield from [Request(follow_url.format(user), callback=self.follow, dont_filter=True) for user in users]

    def works_cos(self, response):
        """获取cos作品
        :param response:
        :return:
        """
        post_work_card__links = response.xpath("./*//a[@class='postWorkCard__link']/@href").extract()
        # 进入作品详细目录
        if len(post_work_card__links) > 0:
            next_page = response.xpath("./*//a[text()='>']/@href").extract_first(default=None)
            yield from [Request(bash_url.format(post_work_card__link), callback=self.detail)
                        for post_work_card__link in post_work_card__links]
            if next_page:
                # 翻页
                yield Request(bash_url.format(next_page), callback=self.works_cos, dont_filter=True)

    def detail(self, response):
        """作品详细目录
        :param response:
        :return:
        """
        cp_rp_ids = re.findall('detail/(.+)/(.+)', response.url)
        if len(cp_rp_ids) > 0:
            cp_rp_id = cp_rp_ids[0]
            cp_id = cp_rp_id[0]
            rp_id = cp_rp_id[1]
            # 传递参数发表回复
            print(response.url)
            post(cp_id, rp_id)
        item = {}
        title = response.xpath("./*//h1/text()").extract_first(default=str(datetime.now()))
        images = response.xpath("./*//img[@class='detail_std detail_clickable' and @src]/@src").extract()
        if len(images) > 0:
            images_list = [re.search(r'.+\.(jpg|png)', image).group() for image in images]
            item['name'] = title.strip()
            item['image_urls'] = images_list
            yield item
            images_list.clear()

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'bcy'])
    pass