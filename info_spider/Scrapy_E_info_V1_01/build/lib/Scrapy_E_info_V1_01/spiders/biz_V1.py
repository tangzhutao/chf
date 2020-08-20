# -*- coding: utf-8 -*-
import scrapy, re
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class BizV1Spider(scrapy.Spider):
    name = 'biz_V1'
    # allowed_domains = ['biz.co188.com']
    # start_urls = ['http://123/']
    base_url = 'http://biz.co188.com'
    url_name = '土木商易宝'
    urls = {
        'http://biz.co188.com/info_10303/p2.html': '行业资讯1',  # 每页10条
        'http://biz.co188.com/info_10304/p2.html': '行业资讯1',  # 每页10条
        'http://biz.co188.com/info_10344/p2.html': '行业资讯1',
        'http://biz.co188.com/info_10306/p2.html': '政策法规1',
        'http://biz.co188.com/info_10307/p2.html': '行业技术1',
        'http://biz.co188.com/info_10305/p2.html': '行业资讯1',
        'http://biz.co188.com/info_10308/p2.html': '行业资讯1',
        'http://biz.co188.com/info_10299/p2.html': '行业资讯1',
        'http://biz.co188.com/info_10300/p2.html': '行业资讯1',
        'http://biz.co188.com/info_10301/p2.html': '行业资讯1',
        'http://biz.co188.com/info_10302/p2.html': '行业资讯1',

    }

    def start_requests(self):

        for url, cate in self.urls.items():
            page = cate[4:]
            for i in range(int(page)):
                link = url.replace(url[-6:-4], f'{i + 1}.')
                i += 1
                yield scrapy.Request(url=link, callback=self.parse, meta={'cate': cate[:4]}, dont_filter=True)
                self.logger.info("cate({})".format(cate[:4]))

    def parse(self, response):

        cate = response.meta['cate']

        config_list = response.xpath('//div[@id="ui_main"]/div')
        a = 1
        for config in config_list:
            if a < 11:
                item = InfoItem()
                title_img = config.xpath('./div[@class="left"]/a/img/@src').extract_first()
                title = config.xpath('./div[@class="navs_head add_height"]/a/text()').extract_first()
                link = self.base_url + config.xpath('./div[@class="navs_head add_height"]/a/@href').extract_first()
                issue_time = config.xpath('./div[@class="navs_head add_height"]/span[@class="head_right"]/text()').extract_first().replace('年', '-').replace(
                    '月', '-').replace('日', '')
                # tags = config.xpath('./div[@class="right"]/ul/li/a/text()').extract()
                item['title'] = title
                item['issue_time'] = issue_time
                item['content_url'] = link
                item['information_categories'] = cate
                item['title_images'] = title_img if title_img else None
                req = scrapy.Request(url=link, callback=self.parse2,
                                     meta={'item': item},
                                     dont_filter=True)
                item['id'] = request.request_fingerprint(req)
                yield req
            a += 1

    def parse2(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="info_content"]').extract_first()
        images = response.xpath('//div[@class="info_content"]//img/@src').extract()
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

        item['tags'] = None
        item['industry_categories'] = 'E'
        item['industry_Lcategories'] = '48'
        item['industry_Mcategories'] = None
        item['industry_Scategories'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['information_source'] = '土木商易宝'
        try:
            source1 = response.xpath('//div[@class="info_title"]/span[2]/a/text()').extract_first().strip()
        except:
            source1 = None
        item['source'] = source1 if source1 else '土木商易宝'

        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        try:
            author = response.xpath('//div[@class="info_title"]/span[3]/text()').extract_first()[3:].strip()
        except:
            author = None
        item['author'] = author
        item['content'] = content

        if content:
            yield item
            self.logger.info("title({}), issue_time({})".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'biz_V1'])
