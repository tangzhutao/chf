import scrapy
import time
import json
import re
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class Huanbaojs01Spider(scrapy.Spider):
    name = 'Huanbaojs_01'
    base_url = 'http://www.huanbaojs.com/'
    url_name = '环保网'
    urls = {
        'http://www.huanbaojs.com/xinwen/hbjj/': 3,
        'http://www.huanbaojs.com/xinwen/hbxw/': 2,
    }

    def start_requests(self):
        for k, v in self.urls.items():
            for i in range(v):
                if i == 0:
                    url = k + 'index.html'
                else:
                    url = k + f'index_{i + 1}.html'
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        config_info = response.xpath('//div[@class="listl list2"]/ul/li')
        for info in config_info:
            link = info.xpath('./h3/a/@href').get()
            title = info.xpath('./h3/a/@title').get()
            issue_time = info.xpath('./span/text()').get()
            req = scrapy.Request(url=link, callback=self.parse_detail, dont_filter=True,
                                 meta={'title': title, 'issue_time': issue_time})
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        issue_time = response.meta['issue_time']
        content = response.xpath(
            '//div[@class="inner"]/div[@class="article-content fontSizeSmall BSHARE_POP"]').extract_first()
        images = response.xpath(
            '//div[@class="inner"]/div[@class="article-content fontSizeSmall BSHARE_POP"]//img/@src').extract()

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

    cmdline.execute(['scrapy', 'crawl', 'Huanbaojs_01'])
