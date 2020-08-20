import scrapy
import time
import json
import re
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class Oubaohuanjing01Spider(scrapy.Spider):
    name = 'Oubaohuanjing_01'
    base_url = 'http://www.hehuzhili.com'
    url_name = '欧保环境网'

    def start_requests(self):
        # 90
        for i in range(2):
            url = f'http://www.hehuzhili.com/xydt-{i + 1}.shtml'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        config_info = response.xpath('//div[@class="news_con"]/dl[@class="news_dl"]/dt')
        for info in config_info:
            url = info.xpath('./a/@href').get()
            title = info.xpath('./a/@title').get()
            publishtime = info.xpath('./span/text()').get()
            issue_time = time.strftime("%Y-%m-%d", time.strptime(publishtime[1:-1], "%Y年%m月%d日%H:%M"))
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True, meta={'title': title, 'issue_time': issue_time})
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        content = response.xpath('//div[@id="cntrBody"]').extract_first()
        issue_time = response.meta['issue_time']
        images = response.xpath('//div[@id="cntrBody"]//img/@src').extract()
        images_url = []
        if images:
            for url in images:
                if 'http' not in url:
                    url = self.base_url + url
                images_url.append(url)

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = response.meta['title']
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = self.url_name
        item['source'] = self.url_name
        item['author'] = None
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
            # print(item['title'], item['images_url'], item['issue_time'])
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(item['title'], issue_time))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'Oubaohuanjing_01'])
