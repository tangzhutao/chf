# -*- coding: utf-8 -*-
import scrapy
from Scrapy_D44_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class PowerofweekV1Spider(scrapy.Spider):
    name = 'powerOfweek_v1'
    allowed_domains = ['power.ofweek.com']
    # start_urls = ['http://power.ofweek.com/']
    urls = {
        'https://power.ofweek.com/CAT-35004-8100-News': '4411-行业资讯-1',  # 火电
        'https://power.ofweek.com/CAT-35003-8100-News': '4413-行业资讯-1',  # 水电
        'https://power.ofweek.com/CAT-35023-8100-News': '4416-行业资讯-1',  # 光伏
        'https://power.ofweek.com/CAT-35006-8100-News': '4414-行业资讯-1',  # 核电
        'https://power.ofweek.com/CAT-35020-8100-News': '4415-行业资讯-1',  # 风电
        'https://power.ofweek.com/CAT-35008-8100-News': '4419-行业资讯-1',  # 可再生资源
    }
    base_url = 'http://power.ofweek.com/'
    url_name = '电力网'

    def start_requests(self):
        for u, c in self.urls.items():
            cs = c.split('-')
            for i in range(int(cs[2])):
                url = u + f'-{i + 1}.html'
                req = scrapy.Request(url=url, callback=self.parse, meta={'cate': cs[1], 'in_S': cs[0]}, dont_filter=True)
                req.headers['Referer'] = u + '.html'
                yield req

    def parse(self, response):
        cate = response.meta['cate']
        new_urls = response.xpath('//div[@class="main_left"]/div')
        a = 0
        for new_url in new_urls:
            if a != 0 and a != 21:
                item = InfoItem()
                item['content_url'] = new_url.xpath('.//h3/a/@href').extract_first()
                item['tags'] = new_url.xpath('.//div[@class="tag"]/span[1]/a/text()').extract_first().strip()
                item['title_images'] = None
                item['industry_categories'] = 'D'
                item['industry_Lcategories'] = '44'
                item['industry_Mcategories'] = '441'
                item['industry_Scategories'] = response.meta['in_S']
                item['information_categories'] = cate
                req = scrapy.Request(url=item['content_url'], callback=self.parse2, meta={'item': item}, dont_filter=True)
                item["id"] = request.request_fingerprint(req)
                yield req
            a += 1

    def parse2(self, response):
        item = response.meta['item']
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['information_source'] = '电力网'
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        item['title'] = response.xpath('//div[@class="artical"]/p/text()').extract_first()
        item['content'] = response.xpath('//div[@class="artical-content"]').extract_first()
        item['issue_time'] = response.xpath('//div[@class="time fl"]/text()').extract_first().strip()[:10]

        source1 = response.xpath('//div[@class="source-name"]/text()').extract_first()
        source2 = response.xpath('//div[@class="artical-relative clearfix"]/a/span[2]/text()').extract_first()
        if source1:
            item['source'] = source1
        elif source2:
            item['source'] = source2
        else:
            item['source'] = None

        item['author'] = None
        images = ';'.join(response.xpath('//div[@class="artical-content"]//img/@src').extract())
        item['images'] = images if images else None

        if item['content']:
            yield item
            self.logger.info("title:{},issue_time:{}".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'powerOfweek_v1'])
