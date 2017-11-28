# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class UItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    table_name = Field()
    name = Field()
    user_id = Field()
    gouda = Field()
    fans = Field()
    follow = Field()
    city = Field()
    following_circle = Field()
    zan = Field()
    works_num = Field()
    achievement = Field()
    url = Field()
    sex = Field()


class DetailItem(Item):
    table_name = Field()
    user_id = Field()
    zan = Field()
    comment = Field()
    tag = Field()
    circle = Field()
    url = Field()
    pass
