# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import Scrapy_GlobalCompetitiveness_V1_01.proxy as Proxy
import logging

logger = logging.getLogger(__name__)


class ProxyMiddleWare(object):
    '''
    设置Proxy
    '''

    def __init__(self):
        self.invalid_proxy = set()
        self.proxy = Proxy.get_proxy()

    def process_request(self, request, spider):
        # 对 request 加上 proxy
        # proxy = get_proxy()
        request.meta['proxy'] = self.proxy['https']
        start_num = Proxy.get_status()
        # logger.info('invalid proxy number is %s,\n proxy total number is %s' % (len(self.invalid_proxy), start_num))

    def process_response(self, request, response, spider):
        # 如果返回的 response 状态不是 200 ，重新声称当前的 request 对象
        try:
            if str(response.status).startswith('4') or str(response.status).startswith('5'):
                print('状态码异常:', response.status)
                num = Proxy.get_status()
                # 当失效集合超过代理池ip数就清空集合
                if len(self.invalid_proxy) >= num:
                    self.invalid_proxy.clear()

                # 将失效代理ip添加到失效集合里
                self.invalid_proxy.add(request.meta['proxy'])
                # 重新获取代理ip
                self.proxy = Proxy.get_proxy()
                while True:
                    # 判断获取的代理ip是不是重复获取或者是失效代理集合里的
                    if self.proxy['https'] in self.invalid_proxy:
                        self.proxy = Proxy.get_proxy()
                        continue
                    else:
                        request.meta['proxy'] = self.proxy['https']
                        # logging.debug('is the invalid ip, replace ip:' + self.proxy['https'])
                        # 对当前request 加上代理
                        break
                return request
        except:
            request.meta['proxy'] = self.proxy['https']
            # logging.info('this is response ip:' + self.proxy['https'])
            # 对当前 request 加上代理
            return request

        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutError):
            self.invalid_proxy.add(request.meta['proxy'])
            self.proxy = Proxy.get_proxy()
            return request

        self.invalid_proxy.add(request.meta['proxy'])
        self.proxy = Proxy.get_proxy()
        num = Proxy.get_status()
        # 当失效集合超过代理池ip数就清空集合
        if len(self.invalid_proxy) >= num:
            self.invalid_proxy.clear()
        while True:
            # 判断获取的代理ip是不是重复获取或者是失效代理集合里的
            if self.proxy['https'] in self.invalid_proxy:
                self.proxy = Proxy.get_proxy()
                continue
            else:
                request.meta['proxy'] = self.proxy['https']
                # logging.debug('there is an error, replace ip:' + self.proxy['https'])
                # 对当前request 加上代理
                break
        return request
