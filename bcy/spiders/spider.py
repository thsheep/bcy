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
from datetime import datetime
from scrapy.spiders import Spider
from scrapy import Request
from bcy.items import UItem, DetailItem
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
        users = response.xpath("./*//i[@class='l-left i-new-sex-{}']/preceding-sibling::a/@href".format(sex)).extract()# 返回用户信息
        yield from [Request(bash_url.format(user), callback=self.user, meta={'user': user}) for user in users]
        # 进入cos作品集
        yield from [Request(works_url.format(user), callback=self.works_cos, meta={'user': user}) for user in users]
        # 继续追踪关注 必须降低优先级 不然就特么全请求follow了
        yield from [Request(follow_url.format(user), callback=self.follow, priority=-1) for user in users]

    def user(self, response):
        u_item = UItem()
        u_item['table_name'] = 'u_item'
        u_item['name'] = self.sub_strip(response.xpath("./*//div[@class='l-clearfix spaceProfileCard__line']/a/text()").extract_first(default=None))
        u_item['user_id'] = response.meta['user']
        u_item['gouda'] = self.sub_strip(response.xpath("./*//span[@class='gouda--tag fz12']/text()").extract_first(default=None))
        u_item['fans'] = self.sub_strip(response.xpath("./*//p[text()='粉丝']/preceding-sibling::p/text()").extract_first(default=None))
        u_item['follow'] = self.sub_strip(response.xpath("./*//p[text()='关注']/preceding-sibling::p/text()").extract_first(default=None))
        city = response.xpath("./*//span[@class='fz14']/text()").extract_first(default=None)
        u_item['city'] = city.strip()
        u_item['following_circle'] = '|'.join(response.xpath("./*//div[text()='关注的圈子']/following-sibling::div/a/@title").extract())
        u_item['zan'] = self.sub_strip(response.xpath("./*//span[@class='ml5 fz14 vam']/span[@class='red']/text()").extract())
        u_item['works_num'] = self.sub_strip(response.xpath("./*//span[@class='ml5 fz14 vam']/span[@class='red ml15']/text()").extract_first(default=None))
        u_item['achievement'] = self.sub_strip(response.xpath("count(./*//div[@id='space-chanliang']/ul/a)").extract_first(default='0'))
        u_item['url'] = response.url
        u_item['sex'] = sex
        yield u_item

    def works_cos(self, response):
        """获取cos作品
        :param response:
        :return:
        """
        post_work_card__links = response.xpath("./*//a[@class='postWorkCard__link']/@href").extract()
        # 进入作品详细目录
        if len(post_work_card__links) > 0:
            next_page = response.xpath("./*//a[text()='>']/@href").extract_first(default=None)
            yield from [Request(bash_url.format(post_work_card__link), callback=self.detail, meta={'user': response.meta['user']})
                        for post_work_card__link in post_work_card__links]
            if next_page:
                # 翻页
                yield Request(bash_url.format(next_page), callback=self.works_cos, dont_filter=True, meta={'user': response.meta['user']})

    def detail(self, response):
        """作品详细目录
        :param response:
        :return:
        """
        detail_item = DetailItem()
        detail_item['table_name'] = 'detail_item'
        detail_item['user_id'] = response.meta['user']
        zan = response.xpath("./*//div[text()='推荐']/following-sibling::div/div/text()").extract()
        zan = self.re_search(r'(\d+)', self.sub_strip(zan))
        detail_item['zan'] = zan
        detail_item['comment'] = self.sub_strip(response.xpath("./*//div[@class='text mb10']/span/text()").extract_first(default=None))
        detail_item['tag'] = self.sub_strip(response.xpath("./*//li[@class='tag']/a/div/text()").extract())
        detail_item['circle'] = '|'.join(response.xpath("./*//li[@class='tag js-delete-tag']/@data-tag-name").extract())
        detail_item['url'] = response.url
        yield detail_item
        # cp_rp_ids = re.findall('detail/(.+)/(.+)', response.url)
        # if len(cp_rp_ids) > 0:
        #     cp_rp_id = cp_rp_ids[0]
        #     cp_id = cp_rp_id[0]
        #     rp_id = cp_rp_id[1]
        #     # 传递参数发表回复
        #     post(cp_id, rp_id)
        # # item = {}
        # title = response.xpath("./*//h1/text()").extract_first(default=str(datetime.now()))
        # images = response.xpath("./*//img[@class='detail_std detail_clickable' and @src]/@src").extract()
        # if len(images) > 0:
        #     images_list = [re.search(r'.+\.(jpg|png)', image).group() for image in images]
        #     item['name'] = title.strip()
        #     item['image_urls'] = images_list
        #     yield item
        #     images_list.clear()

    @staticmethod
    def sub_strip(string):
        if string is not None:
            string = ''.join(string).strip()
            string = re.sub('\s', '', string)
            return string
        return '空'

    @staticmethod
    def re_search(pattern, string):
        string = ''.join(string).strip()
        string = re.sub('\s', '', string)
        result = re.search(pattern, string)
        if hasattr(result, 'group'):
            return result.group()
        return '空'

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'bcy'])
    pass