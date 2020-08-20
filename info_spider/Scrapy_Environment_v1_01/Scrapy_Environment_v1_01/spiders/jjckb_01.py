import scrapy
import time
import json
import re
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class Jjckb01Spider(scrapy.Spider):
    name = 'jjckb_01'
    base_url = 'http://jjckb.xinhuanet.com/'
    url_name = '经济参考网'

    def start_requests(self):
        for i in range(1):
            url = f'http://qc.wa.news.cn/nodeart/list?nid=11100316&pgnum={i + 1}&cnt=50&attr=&tp=1&orderby=1&callback=jQuery17109016733155994541_1597310628591&_=1597310631410'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        config_info = json.loads(response.text[41:-1])['data']['list']
        for info in config_info:
            url = info['LinkUrl']
            title = info['Title']
            Author = info['Author']
            PubTime = info['PubTime']
            issue_time = time.strftime("%Y-%m-%d", time.strptime(PubTime, "%Y-%m-%d %H:%M:%S"))
            SourceName = info['SourceName']
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True,
                                 meta={'title': title, 'issue_time': issue_time, 'author': Author,
                                       'source': SourceName})
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.meta['title']
        issue_time = response.meta['issue_time']
        author = response.meta['author']
        source = response.meta['source']
        content = response.xpath('//div[@id="content"]').extract_first()

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = self.url_name
        item['source'] = source if source else None
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
        item['images_url'] = None
        if content:
            # print(item)
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'jjckb_01'])
