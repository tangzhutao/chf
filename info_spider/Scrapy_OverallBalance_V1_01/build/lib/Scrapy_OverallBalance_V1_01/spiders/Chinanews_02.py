import scrapy
import json
import time
from Scrapy_OverallBalance_V1_01.items import InfoItem
from scrapy.utils import request


class Chinanews01Spider(scrapy.Spider):
    name = 'Chinanews_02'
    base_url = 'http://www.chinanews.com/'
    url_name = '中国新闻网'

    def start_requests(self):
        # http://channel.chinanews.com/cns/cjs/gn.shtml?pager=1&pagenum=10&t=2_45  15
        for j in range(15):
            url = f'http://channel.chinanews.com/cns/cjs/gn.shtml?pager={j + 1}&pagenum=10&t=2_45'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        # print(response.text[16:-29])
        config_info = json.loads(response.text[16:-29])['docs']

        for info in config_info:
            url = info['url']
            title = info['title']
            source = info['channel']
            issue_time = time.strftime("%Y-%m-%d", time.strptime(info['pubtime'], "%Y-%m-%d %H:%M:%S"))
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True,
                                 meta={'title': title, 'issue_time': issue_time, 'source': source})
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
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
        if item['content']:
            # print(item)
            yield item
            self.logger.info('title: {}, issue_time: {}'.format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Chinanews_02'])
