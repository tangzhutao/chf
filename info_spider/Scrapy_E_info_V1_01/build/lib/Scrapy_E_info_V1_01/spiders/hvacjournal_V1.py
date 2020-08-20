# -*- coding: utf-8 -*-
import scrapy
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class HvacjournalV1Spider(scrapy.Spider):
    name = 'hvacjournal_V1'
    base_url = 'http://www.hvacjournal.cn'
    url_name= '暖通空调'

    def start_requests(self):
        for i in range(1):
                url = f'http://www.hvacjournal.cn/Category_25/Index_{i + 1}.aspx'
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        config_list = response.xpath('//div[@class="listBox"]/li')
        # print(len(config_list))
        num = [5, 11, 17, 23]
        if config_list:
            for n in range(len(config_list)):
                if n not in num:
                    item = InfoItem()
                    title = config_list[n].xpath('./a/text()').extract_first()
                    link = self.base_url + config_list[n].xpath('./a/@href').extract_first()
                    issue_time = config_list[n].xpath('./span/text()').extract_first()
                    req = scrapy.Request(url=link, callback=self.parse_detail, meta={'item': item}, dont_filter=True)
                    item['id'] = request.request_fingerprint(req)
                    item['title'] = title
                    item['title_images'] = None
                    item['tags'] = None
                    item['industry_categories'] = 'E'
                    item['industry_Lcategories'] = '49'
                    item['industry_Mcategories'] = '492'
                    item['industry_Scategories'] = None
                    item['information_categories'] = '行业资讯'
                    item['content_url'] = link
                    item['issue_time'] = issue_time
                    yield req

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@id="fontzoom"]').extract_first()
        images = response.xpath('//div[@id="fontzoom"]//img/@src').extract()
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

        source = response.xpath('//div[@class="property"]/span[1]/text()').extract_first()
        author = response.xpath('//div[@class="property"]/span[2]/text()').extract_first()

        item['author'] = author[5:] if author[5:] else None
        item['source'] = source[5:] if source[5:] else '暖通空调'
        item['information_source'] = '暖通空调'
        item['content'] = content
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        if content:
            yield item
            self.logger.info("title({}), issue_time({})".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'hvacjournal_V1'])
