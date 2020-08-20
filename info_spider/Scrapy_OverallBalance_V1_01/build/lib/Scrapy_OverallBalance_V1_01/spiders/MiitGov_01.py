import scrapy
import json
import time
from Scrapy_OverallBalance_V1_01.items import InfoItem
from scrapy.utils import request


class Miitgov01Spider(scrapy.Spider):
    name = 'MiitGov_01'
    base_url = 'http://www.miit.gov.cn/'
    url_name = '中国工业和信息化部'

    def start_requests(self):
        # 369 234 566 256
        urls = {
            'http://www.miit.gov.cn/n1146290/n1146402/n7039597/index.html?&tsrcdwtdqfc': 369,
            'http://www.miit.gov.cn/n1146290/n1146402/n1146440/index.html?&tsrcdwtdqfc': 234,
            'http://www.miit.gov.cn/n1146290/n1146402/n1146450/index.html?&tsrcdwtdqfc': 566,
            'http://www.miit.gov.cn/n1146290/n1146402/n1146445/index.html?&tsrcdwtdqfc': 256
        }

        for k, v in urls.items():
            cookie = {
                'maxPageNum1274883': str(v),
                'Hm_lvt_af6f1f256bb28e610b1fc64e6b1a7613': '1595230727,1595474493,1597302442,1597651978',
                'Hm_lpvt_af6f1f256bb28e610b1fc64e6b1a7613': str(int(time.time()))
            }
            for i in range(2):
            # for i in range(v):
                if i == 0:
                    url = k
                else:
                    last = f'index_1274883_{v - i}.html?&tsrcdwtdqfc'
                    base = k.split('/')[:-1]
                    base.append(last)
                    url = '/'.join(base)
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'cookie': cookie})
                req.headers['Host'] = 'www.miit.gov.cn'
                req.headers[
                    'Cookie'] = cookie
                yield req

    def parse(self, response):
        config_info = response.xpath('//div[@class="clist_con"]/ul/li/a/@href').extract()
        for info in config_info:
            url = self.base_url + info.replace('../', '')
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({"news_id": news_id})
            req.headers['Host'] = 'www.miit.gov.cn'
            req.headers[
                'Cookie'] = response.meta['cookie']
            yield req

    def parse_detail(self, response):
        # proxy = response.meta['proxy']
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        title = response.xpath('//h1[@id="con_title"]/text()').extract_first()
        issue_time = response.xpath('//span[@id="con_time"]/text()').extract_first()[5:]
        source = response.xpath('//div[@class="cinfo center"]/span[2]/text()').extract_first()
        content = response.xpath('//div[@id="con_con"]').extract_first()
        images = response.xpath('//div[@id="con_con"]//img/@src').extract()

        images_url = []
        if images:
            for url in images:
                if 'http' not in url:
                    url = self.base_url + url.replace('../', '')
                images_url.append(url)
        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '综合平衡'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = self.url_name
        item['source'] = source[3:] if source else self.url_name
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

    cmdline.execute(['scrapy', 'crawl', 'MiitGov_01'])
