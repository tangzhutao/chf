# -*- coding: utf-8 -*-
import scrapy
from Scrapy_D44_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class ScrapyFenglifadianV1Spider(scrapy.Spider):
    name = 'Scrapy_Fenglifadian_v1'
    allowed_domains = ['fd.bjx.com.cn', 'news.bjx.com.cn']

    urls = {
        'http://fd.bjx.com.cn/fdcy/': '新闻资讯',
        'http://fd.bjx.com.cn/fdjs/': '新闻资讯',
        'http://fd.bjx.com.cn/fdyw/': '新闻资讯',
        'http://fd.bjx.com.cn/fdsbycl/': '新闻资讯',
        'http://fd.bjx.com.cn/hsfd/': '新闻资讯',
        'http://fd.bjx.com.cn/fssfd/': '新闻资讯',
        'http://fd.bjx.com.cn/gjfd/': '国际动态',
    }

    base_url = 'http://fd.bjx.com.cn/'
    url_name = '北极星风力发电网'


    def start_requests(self):
        for url, cate in self.urls.items():
            for i in range(3):
                link = url + f'?page={i + 1}'
                yield scrapy.Request(url=link, callback=self.parse2, meta={'cate': cate, 'url': url}, dont_filter=True)

    def parse2(self, response):
        cate = response.meta['cate']
        node_list = response.xpath('//div[@class="list_left"]/ul/li')
        for node in node_list:
            link_list = node.xpath('./a/@href').extract_first()
            if link_list:
                item = InfoItem()
                item['content_url'] = link_list
                item['issue_time'] = node.xpath('./span/text()').extract_first()
                req = scrapy.Request(url=link_list, callback=self.parse3, meta={'item': item, 'cate': cate}, dont_filter=True)
                item["id"] = request.request_fingerprint(req)
                yield req

    def parse3(self, response):
        cate = response.meta['cate']
        item = response.meta['item']

        item['title'] = response.xpath('//div[@class="list_detail"]/h1/text()').extract_first()
        item['source'] = None
        source = ''.join(response.xpath(
            '//div[@class="list_detail"]/div[@class="tempa list_copy btemp"]/b[1]//text()').extract())
        item['source'] = source[3:] if source else None
        # print(source)
        item['information_source'] = '北极星风力发电网'

        tags = response.xpath(
            '//div[@class="list_detail"]/div[@class="tempa list_key btemp"]/a/text()').extract()
        item['tags'] = ';'.join(tags)
        content = response.xpath('//div[@class="list_detail"]/div[@class="btemp"]').extract_first()
        item['content'] = content if content else None

        item['industry_categories'] = 'D'
        item['industry_Lcategories'] = '44'
        item['industry_Mcategories'] = '441'
        item['industry_Scategories'] = '4415'
        item['information_categories'] = cate
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        image_url = ';'.join(
            response.xpath('//div[@class="list_detail"]/div[@class="btemp"]//img/@data-echo').extract())
        item["images"] = image_url if image_url else None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['title_images'] = None
        # 部分没有作者，解决报错
        try:
            author = response.xpath('//div[@class="list_copy"]/text()').extract()
            author = author[1].strip()
            item['author'] = author[3:] if author else None
        except:
            item['author'] = None

        if item['content']:
            yield item
            self.logger.info("title:{},issue_time:{}".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Scrapy_Fenglifadian_v1'])
