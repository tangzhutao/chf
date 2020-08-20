# -*- coding: utf-8 -*-
import scrapy
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class ChinahighwayV1Spider(scrapy.Spider):
    name = 'chinaHighway_V1'

    base_url = 'http://www.chinahighway.com'
    url_name='中国公路网'

    def start_requests(self):
        for i in range(2):
            url = f'http://www.chinahighway.com/focus?page={i + 1}&per-page=8'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        config_list = response.xpath('//ul[@id="ulitems"]/li')
        for con in config_list:
            item = InfoItem()
            title = con.xpath('./div/a/text()').extract_first()
            link = con.xpath('./div/a/@href').extract_first()
            issue_time = con.xpath('./div/span/text()').extract_first()
            if link:
                link = self.base_url + link
                # print(title, link, issue_time)

                req = scrapy.Request(url=link, callback=self.parse_detail, meta={'item': item}, dont_filter=True)

                item['id'] = request.request_fingerprint(req)
                item['title'] = title
                item['title_images'] = None
                item['tags'] = None
                item['author'] = None
                item['industry_categories'] = 'E'
                item['industry_Lcategories'] = '48'
                item['industry_Mcategories'] = '481'
                item['industry_Scategories'] = None
                item['information_categories'] = '行业资讯'
                item['content_url'] = link
                item['issue_time'] = issue_time[3:] if issue_time else None

                yield req

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="ttxq_con"]').extract_first()
        images = response.xpath('//div[@class="ttxq_con"]//img/@src').extract()
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

        source = response.xpath('//div[@class="ttxq_top"]/dl/dd/span[1]/text()').extract_first()

        item['source'] = source[3:] if source else '中国公路网'
        item['information_source'] = '中国公路网'
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
    cmdline.execute(['scrapy', 'crawl', 'chinaHighway_V1'])
