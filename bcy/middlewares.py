# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import base64
import json
from multiprocessing import Process
from scrapy import signals
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from bcy.login import web_driver_login


class BcyDownMiddleware(RetryMiddleware):

    def process_request(self, request, spider):
        if not request.url.endswith('.jpg'):
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                cookie = json.loads(f.read())
            request.cookies = cookie

    def process_response(self, request, response, spider):
        # 判断cookie是否有效
        if not request.url.endswith('.jpg'):
            status = response.xpath("./*//i[@class='i-notification mt9 mb9']").extract_first(default=None)
            if status == None:
                print('更换Cookie')
                p = Process(target=web_driver_login)
                p.start()
                p.join()
                print('更换成功')
                reason = response_status_message(response.status)
                return self._retry(request, reason, spider) or response  # 重试
            return response
        return response


class ProxyMiddleware(object):
    '''随机选择代理'''

    proxyServer = "http://proxy.abuyun.com:9020"
    # 代理隧道验证信息
    proxyUser = "H0LJ44DO4I9NG48D"
    proxyPass = "03DDA970549AD599"
    proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")

    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxyServer
        request.headers["Proxy-Authorization"] = self.proxyAuth



















class BcySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
