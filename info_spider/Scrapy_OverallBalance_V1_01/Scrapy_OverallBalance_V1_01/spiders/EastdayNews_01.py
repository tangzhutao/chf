import scrapy
import json
import time
from Scrapy_OverallBalance_V1_01.items import InfoItem
from scrapy.utils import request


class Eastdaynews01Spider(scrapy.Spider):
    name = 'EastdayNews_01'
    base_url = 'http://news.eastday.com/'
    url_name = '东方网'

    def start_requests(self):
        url = 'http://news.eastday.com/gd2008/shzw/index.html?t=true'
        req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
        req.headers['Host'] = 'news.eastday.com'
        yield req

    def parse(self, response):
        config_info = response.xpath('//div[@id="left"]/ul/li/a/@href').extract()
        for url in config_info:
            url = url.replace('news', 'pnews')
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            req.headers['Cookie'] = 'wdcid=7a2fb2e6c6216a4b; Hm_lvt_d82057e884263d9012a42f2d11c81647=1597651387; __asc=331f7039173fb719f6a160738a8; __auc=331f7039173fb719f6a160738a8; eastdaywdcid=2e4bac70e3093716; Hm_lpvt_d82057e884263d9012a42f2d11c81647=1597657517; eastdaywdlast=1597657519; wdlast=1597657519'
            yield req

    def parse_detail(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        title = response.xpath('//div[@class="article"]/h1/text()').extract_first()
        issue_time = response.xpath('//div[@class="subInfo"]/span[@class="date"]/text()').extract_first()
        author = response.xpath('//div[@class="subInfo"]/span[@class="author"]/text()').extract_first()
        source = response.xpath('//div[@class="subInfo"]/span[@class="source"]/a/text()').extract_first()
        content = response.xpath('//div[@class="detail"]').extract_first()
        images = response.xpath('//div[@class="detail"]//img/@src').extract()

        images_url = []
        if images:
            for url in images:
                url = url.split('?')[0]
                if 'http' not in url:
                    url = self.base_url + url
                images_url.append(url)

        # print(title, issue_time, author, source, images_url)
        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '综合平衡'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time.split(' ')[0] if issue_time else None
        item['information_source'] = self.url_name
        item['source'] = source if source else self.url_name
        item['author'] = author[3:] if author else None
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
            self.logger.info('title: {}, issue_time: {}'.format(item['title'], item['issue_time']))


if __name__ == '__main__':

    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'EastdayNews_01'])
