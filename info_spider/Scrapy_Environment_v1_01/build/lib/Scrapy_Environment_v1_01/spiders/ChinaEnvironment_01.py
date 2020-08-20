import scrapy
import time
import json
import re
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class Chinaenvironment01Spider(scrapy.Spider):
    name = 'ChinaEnvironment_01'
    base_url = 'http://www.chinaenvironment.com'
    url_name = '环保网'

    urls = {
        'http://www.chinaenvironment.com/ajax/ajax.aspx?type=loaddata&pagesize=0&nodeid=54': 2,
        'http://www.chinaenvironment.com/ajax/ajax.aspx?type=loaddata&pagesize=0&nodeid=55': 2,
    }

    def start_requests(self):
        for k, v in self.urls.items():
            for i in range(v):
                url = k.replace('pagesize=0', f'pagesize={i}')
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        config_info = response.xpath('//a[@class="title"]/@href').extract()
        for url in config_info:
            if 'http' not in url:
                url = self.base_url + url
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        title = response.xpath('//div[@class="articleTit"]/text()').get()
        publishtime = response.xpath('//span[@class="ibox time"]/text()').get()
        issue_time = time.strftime("%Y-%m-%d", time.strptime(publishtime, "时间：%Y.%m.%d"))
        source = response.xpath('//span[@class="ibox from"]/text()').get()[3:]
        author = response.xpath('//span[@class="ibox author"]/text()').get()[3:]
        content = response.xpath('//div[@class="edits"]').extract_first()
        images = response.xpath('//div[@class="edits"]//img/@src').extract_first()

        images_url = []
        if images:
            for url in images_url:
                if 'http' not in url:
                    url = self.base_url + url
                images_url.append(url)

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = self.url_name
        item['source'] = source if source else self.url_name
        item['author'] = author if author else None
        item['content'] = content
        item['images'] = None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['headers'] = headers
        item['images_url'] = images_url
        if item['content']:
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(item['title'], issue_time))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'ChinaEnvironment_01'])
