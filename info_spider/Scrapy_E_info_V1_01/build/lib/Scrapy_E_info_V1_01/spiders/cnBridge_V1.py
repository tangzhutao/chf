# -*- coding: utf-8 -*-
import scrapy
import re
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class CnbridgeV1Spider(scrapy.Spider):
    name = 'cnBridge_V1'
    allowed_domains = ['www.cnbridge.cn']
    base_url = 'http://www.cnbridge.cn'
    url_name = '国际路桥网'
    # start_urls = ['http://www.cnbridge.cn/']

    def start_requests(self):
        yield scrapy.Request(url='http://www.cnbridge.cn/html/news/index.html', callback=self.parse, dont_filter=True)

        for i in range(1, 5):
            url = f'http://www.cnbridge.cn/html/news/{i + 1}.html'
            req = scrapy.Request(url=url, callback=self.parse)

            yield req

    def parse(self, response):
        config_list = response.xpath('//div[@class="show2 left"]/div')
        num = [0, 1, 12]
        for i in range(len(config_list)):

            if i not in num:
                item = InfoItem()
                title = config_list[i].xpath('.//div[@class="list5"]/a/text()').extract_first()
                link = self.base_url + config_list[i].xpath('.//div[@class="list5"]/a/@href').extract_first()
                title_images = config_list[i].xpath('.//img/@src').extract_first()
                req = scrapy.Request(url=link, callback=self.parse_detail, meta={'item': item}, dont_filter=True)
                item['id'] = request.request_fingerprint(req)
                item['title'] = title
                item['title_images'] = title_images
                item['content_url'] = link
                item['industry_categories'] = 'E'
                item['industry_Lcategories'] = '48'
                item['industry_Mcategories'] = '481'
                item['industry_Scategories'] = None
                item['information_categories'] = '行业资讯'
                yield req

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="show10"]').extract_first()
        info = response.xpath('//div[@class="show7"]/text()').extract_first()
        issue_time = None
        source = None
        if info:
            issue_time = re.findall(r'(\d+)', info.strip())
            source = re.search(r'来源：([^\x00-\xff]+)', info.strip())

        images = response.xpath('//div[@class="show10"]//img/@src').extract()
        if images:
            images_url = []
            for img in images:
                if 'http' in img:
                    images_url.append(img)
                else:
                    image = f'{self.base_url}{img}'
                    images_url.append(image)
            images_urls = '; '.join(images_url)
            item['images'] = images_urls if images_urls else None
        else:
            item['images'] = None

        item['issue_time'] = '-'.join(issue_time) if issue_time else None
        item['source'] = source.group(1) if source else '中国桥梁网'
        item['author'] = None
        item['information_source'] = '中国桥梁网'
        item['content'] = content
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        if content:
            yield item
            self.logger.info("title({}), issue_time({})".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'cnBridge_V1'])
