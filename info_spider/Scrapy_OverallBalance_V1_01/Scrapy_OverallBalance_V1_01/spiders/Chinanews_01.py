import scrapy
import re
import json
import time
from Scrapy_OverallBalance_V1_01.items import InfoItem
from scrapy.utils import request


class Chinanews01Spider(scrapy.Spider):
    name = 'Chinanews_01'
    base_url = 'http://www.chinanews.com/'
    url_name = '中国新闻网'

    def start_requests(self):
        # http://channel.chinanews.com/cns/cl/gn-zcdt.shtml?pager=0   100
        for i in range(2):
            url = f'http://channel.chinanews.com/cns/cl/gn-zcdt.shtml?pager={i}'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        # print(response.text)
        config_info = re.search(r'var docArr(.+)', response.text).group(1)[1:-2]
        info = json.loads(config_info)
        for i in info:
            url = i['url']
            title = i['title']
            issue_time = time.strftime("%Y-%m-%d", time.strptime(i['pubtime'], "%Y-%m-%d %H:%M:%S"))
            source = i['channel']
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True, meta={'title': title, 'issue_time': issue_time, 'source': source})
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        # proxy = response.meta['proxy']
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        source = response.meta['source']
        content = response.xpath('//div[@class="left_zw"]').extract_first()
        images_url = response.xpath('//div[@class="left_zw"]//img/@src').extract()

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '综合平衡'
        item['content_url'] = response.url
        item['title'] = response.meta['title']
        item['issue_time'] = response.meta['issue_time']
        item['information_source'] = self.url_name
        item['source'] = source if source else self.url_name
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
        # item['proxy'] = proxy
        if item['content']:
            # print(item)
            yield item
            self.logger.info('title: {}, issue_time: {}'.format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'Chinanews_01'])
