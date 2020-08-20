# -*- coding: utf-8 -*-
import scrapy
import time
from Scrapy_E_info_V1_01.items import InfoItem
from scrapy.utils import request


class AbbaV1Spider(scrapy.Spider):
    name = 'Abbs_V1'
    # allowed_domains = ['www.abbs.com.cn']
    # start_urls = ['https://www.abbs.com.cn/news/index.php?cate=3&page=1&query=']
    base_url = 'http://www.abbs.com.cn/'
    url_name = '建筑论坛'

    def start_requests(self):
        for i in range(2):
            url = f'http://www.abbs.com.cn/news/index.php?cate=3&page={i + 1}&query='
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            req.headers['Host'] = 'www.abbs.com.cn'
            req.headers['Connection'] = 'keep-alive'
            req.headers['Upgrade-Insecure-Requests'] = '1'
            req.headers['Cookie'] = '__utma=257498843.200118608.1583747278.1583747278.1583747278.1; __utmc=257498843; __utmz=257498843.1583747278.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; Hm_lvt_4533002abe821deabeeda13d3e466540=1583740842,1583747278; __utmb=257498843.15.10.1583747278; Hm_lpvt_4533002abe821deabeeda13d3e466540=1583747800'
            yield req

    def parse(self, response):
        base_url = 'http://www.abbs.com.cn/news/'
        config_list1 = response.xpath('//td[@valign="top"]/a')
        config_list2 = response.xpath('//td[@valign="top"]/b')
        for i in range(len(config_list1)):
            item = InfoItem()
            link = base_url + config_list1[i].xpath('./@href').extract_first()
            title = config_list1[i].xpath('./text()').extract_first()
            issue_time = config_list2[i].xpath('./text()').extract_first()
            req = scrapy.Request(url=link, callback=self.parse_detail, dont_filter=True, meta={'item': item})
            item['id'] = request.request_fingerprint(req)
            item['title'] = title
            item['content_url'] = link
            item['title_images'] = None
            item['issue_time'] = issue_time
            yield req

    def parse_detail(self, response):
        content = response.xpath('//td[@class="s"]').extract_first()

        item = response.meta['item']

        images = response.xpath('//td[@class="s"]//img/@src').extract()
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

        item['content'] = content
        item['tags'] = None
        item['industry_categories'] = 'E'
        item['industry_Lcategories'] = '47'
        item['industry_Mcategories'] = None
        item['industry_Scategories'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['information_source'] = 'ABBS建筑论坛'
        item['source'] = 'ABBS建筑论坛'
        item['author'] = None
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        item['information_categories'] = '行业资讯'
        # print(item)
        if content:
            yield item
            self.logger.info("title({}), issue_time({})".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'Abbs_V1'])
