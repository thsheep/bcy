# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# adbapi 不用commit整个池子关闭后自动commit
import re
import six
import pymysql
from twisted.enterprise import adbapi
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from bcy.items import UItem, DetailItem


class InfoPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def form_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            # cursorclass=pymysql.connect,
            charset='utf8',
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool=dbpool)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.form_settings(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, UItem):
            table_name = item.pop('table_name')
            col_str = ''
            row_str = ''
            for key in item.keys():
                col_str = col_str + " " + key + ","
                row_str = "{}'{}',".format(row_str,
                                           item[key] if "'" not in item[key] else item[key].replace("'", "\\'"))
                sql = "insert INTO {} ({}) VALUES ({}) ON DUPLICATE KEY UPDATE ".format(table_name, col_str[1:-1],
                                                                                        row_str[:-1])
            for (key, value) in six.iteritems(item):
                sql += "{} = '{}', ".format(key, value if "'" not in value else value.replace("'", "\\'"))
            sql = sql[:-2]
            self.dbpool_execute(sql).addCallback(self.printresult)
            return item
        if isinstance(item, DetailItem):
            table_name = item.pop('table_name')
            col_str = ''
            row_str = ''
            for key in item.keys():
                col_str = col_str + " " + key + ","
                row_str = "{}'{}',".format(row_str,
                                           item[key] if "'" not in item[key] else item[key].replace("'", "\\'"))
                sql = "insert INTO {} ({}) VALUES ({}) ON DUPLICATE KEY UPDATE ".format(table_name, col_str[1:-1],
                                                                                        row_str[:-1])
            for (key, value) in six.iteritems(item):
                sql += "{} = '{}', ".format(key, value if "'" not in value else value.replace("'", "\\'"))
            sql = sql[:-2]
            self.dbpool_execute(sql).addCallback(self.printresult)
            return item

    def execute(self, txn, sql):
        result = txn.execute(sql)
        return result
    def dbpool_execute(self, sql):
        return self.dbpool.runInteraction(self.execute, sql)

    def printresult(self, age):

        pass


class BcyPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        """
        :param request: 每一个图片下载管道请求
        :param response:
        :param info:
        :param strip :清洗Windows系统的文件夹非法字符，避免无法创建目录
        :return: 每套图的分类目录
        """
        item = request.meta['item']
        folder = item['name']
        folder_strip = strip(folder)
        image_guid = request.url.split('/')[-1]
        filename = u'full/{0}/{1}'.format(folder_strip, image_guid)
        return filename

    def get_media_requests(self, item, info):
        """
        :param item: spider.py中返回的item
        :param info:
        :return:
        """
        yield from [Request(img_url, meta={'item': item}) for img_url in item['image_urls']]

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item

    # def process_item(self, item, spider):
    #     return item

def strip(path):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    path = re.sub(r'[？\\*|“<>:/]', '', str(path))
    return path