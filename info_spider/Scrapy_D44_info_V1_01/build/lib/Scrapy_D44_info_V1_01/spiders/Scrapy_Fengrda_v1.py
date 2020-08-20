# -*- coding: utf-8 -*-
import scrapy
from Scrapy_D44_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class ScrapyFengrdaV1Spider(scrapy.Spider):
    name = 'Scrapy_Fengrda_v1'
    allowed_domains = ['fengrda.com']
    base_url = 'http://www.fengrda.com/'
    url_name = '南极资讯网'


    def start_requests(self):
        # http://www.fengrda.com/huodian/huodianchanye/list161.html
        for num in range(5):
            next_link = f'http://www.fengrda.com/huodian/list15{num + 1}.html'
            cate = '行业资讯'
            yield scrapy.Request(url=next_link, callback=self.parse, meta={'cate': cate}, dont_filter=True)

    def parse(self, response):
        cate = response.meta['cate']
        new_urls = response.xpath('//div[@class="news1_txt"]/h3/a/@href').extract()
        for new_url in new_urls:
            item = InfoItem()
            item['content_url'] = f'http://www.fengrda.com{new_url}'
            item['title_images'] = None
            item['industry_categories'] = 'D'
            item['industry_Lcategories'] = '44'
            item['industry_Mcategories'] = '441'
            item['industry_Scategories'] = '4411'
            item['information_categories'] = cate
            req = scrapy.Request(url=item['content_url'], callback=self.parse2, meta={'item': item}, dont_filter=True)
            item["id"] = request.request_fingerprint(req)
            yield req

    def parse2(self, response):
        item = response.meta['item']
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['information_source'] = '南极资讯网'
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        item['title'] = response.xpath('//div[@id="printContent"]/h2/font/text()').extract_first()
        item['content'] = response.xpath('//div[@class="mainL12"]').extract_first()
        item['issue_time'] = response.xpath('//div[@id="printContent"]/h6/span[1]/text()').extract_first()[:10]
        item['source'] = response.xpath('//div[@id="printContent"]/h6/span[2]/text()').extract_first()[3:]
        item['author'] = None
        item['tags'] = None
        images = response.xpath('//div[@class="mainL12"]//img/@src').extract()
        image_urls = []
        for image in images:
            if 'http' in image:
                image_urls.append(image)
            else:
                image_url = f'http://www.fengrda.com{image}'
                image_urls.append(image_url)

        images_url = ';'.join(image_urls)
        item['images'] = images_url if images_url else None

        if item['content']:
            yield item
            self.logger.info("title:{},issue_time:{}".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Scrapy_Fengrda_v1'])
