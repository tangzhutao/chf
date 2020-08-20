import scrapy
import time
import re
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class HuanbaoBjx01Spider(scrapy.Spider):
    name = 'Huanbao_Bjx_01'
    base_url = 'https://huanbao.bjx.com.cn/'
    url_name = '北极星环保网'

    urls = {
        'https://huanbao.bjx.com.cn/NewsList?page=': 2,
        'https://huanbao.bjx.com.cn/NewsList?id=100&page=': 2,
        'https://huanbao.bjx.com.cn/NewsList?id=89&page=': 2,
        'https://huanbao.bjx.com.cn/NewsList?id=76&page=': 2,
    }

    def start_requests(self):
        for k, v in self.urls.items():
            # for i in range(v):
            for i in range(2):
                url = k + f'{i + 1}'
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        config_info = response.xpath('//div[@class="list_left"]/ul[@class="list_left_ul"]/li/a/@href').extract()
        for info in config_info:
            req = scrapy.Request(url=info, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        title = response.xpath('//div[@class="list_detail"]/h1/text()').extract_first()
        source = response.xpath('//div[@class="list_detail"]/div[@class="list_copy"]/b[1]/text()').extract_first()[3:]
        issue_time = response.xpath('//div[@class="list_detail"]/div[@class="list_copy"]/b[2]/text()').extract_first()
        issue_time = time.strftime("%Y-%m-%d", time.strptime(issue_time, "%Y/%m/%d %H:%M:%S"))
        author = response.xpath('//div[@class="list_detail"]/div[@class="list_copy"]/text()').extract()
        author = ''.join(author).strip()[3:] if author else None
        content = response.xpath('//div[@class="list_detail"]').extract_first()
        images_url = response.xpath('//div[@class="list_detail"]//img/@data-echo').extract()
        # print(title, issue_time, author, images_url)

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = self.url_name
        item['source'] = source if source else None
        item['author'] = author
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
        if content:
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'Huanbao_Bjx_01'])
