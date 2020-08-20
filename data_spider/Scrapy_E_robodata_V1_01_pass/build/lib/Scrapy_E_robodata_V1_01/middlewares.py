from scrapy import signals
import requests
import time
import logging
from scrapy.exceptions import IgnoreRequest


class ProxyMiddleWare(object):

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.proxy = None

    def get_proxy(self):
        if self.proxy == None:
            while True:
                p = requests.get("http://192.168.0.11:5010/get/").json()
                if p.get("code") == 0:
                    self.logger.warning(p.get("src"))
                    time.sleep(60)
                else:
                    proxy_ = p.get('proxy')
                    proxy = 'https://%s' % proxy_
                    break
            self.proxy = proxy
            # self.logger.info("*** GET PROXY : %s ***" % proxy)
            return proxy
        else:
            return self.proxy

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        proxy = self.get_proxy()
        # spider.logger.info("*** proxy: %s ***" % proxy)
        if 'https:' in request.url:
            proxy = proxy.replace('http:', 'https:')
        elif 'http:' in request.url:
            proxy = proxy.replace('https:', 'http:')
        request.meta['proxy'] = proxy
        request.meta['download_timeout'] = 30  # 超时前等待的时间
        request_count = request.meta.get('request_count', 0)
        if request_count >= 6:
            # spider.logger.info("放弃请求：%s" % request.url)
            raise IgnoreRequest

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status == 404:  # 状态码：404
            return response
        elif response.status != 200:  # 状态码：非200
            # spider.logger.debug('*** Bad proxy: %s ***' % request.meta['proxy'])
            # 重置proxy
            self.proxy = None
            return request
        else:  # 状态码：200
            self.proxy = request.meta['proxy']
            return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, IgnoreRequest):
            return None
        # spider.logger.debug(exception)
        # 重置proxy
        if request.meta['proxy'] == self.proxy:
            self.proxy = None
        request_count = request.meta.get('request_count', 1)
        # 重复请求次数不能超过5次
        # self.logger.info("第%s次重复请求：%s" % (request_count, request.url))
        request.meta['request_count'] = request_count + 1
        return request
