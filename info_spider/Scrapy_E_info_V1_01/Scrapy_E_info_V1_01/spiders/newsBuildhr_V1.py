# -*- coding: utf-8 -*-
import scrapy
import re
import time
from Scrapy_E_info_V1_01.items import InfoItem
from scrapy.utils import request


class NewsbuildhrV1Spider(scrapy.Spider):
    name = 'newsBuildhr_V1'
    allowed_domains = ['news.buildhr.com']
    base_url = 'http://news.buildhr.com/'
    url_name = '英才网'

    def start_requests(self):
        for i in range(2):
            url = f'http://news.buildhr.com/more.php?type=144&page={i + 1}'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        config_list = response.xpath('//div[@class="morenews"]/ul/li')
        for con in config_list:
            item = InfoItem()
            title = con.xpath('./h1/a/text()').extract_first()
            link = 'http:' + con.xpath('./h1/a/@href').extract_first()
            source = con.xpath('./h1/span/address/text()').extract_first()
            issue_time = con.xpath('./h1/span/b/text()').extract_first().replace('年', '-').replace('月', '-').replace(
                '日', '')
            req = scrapy.Request(url=link, callback=self.parse_detail, dont_filter=True, meta={'item': item})
            item['id'] = request.request_fingerprint(req)
            item['title'] = title
            item['title_images'] = None
            item['content_url'] = link
            item['issue_time'] = issue_time
            item['source'] = source[3:] if source else '建筑英才网'
            yield req

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="newsContent"]').extract_first()
        newsDate = response.xpath('//p[@class="newsDate"]/text()').extract_first()
        try:
            author = re.search(r'作者：(.+)　来源：', newsDate).group(1)
        except:
            author = None

        item['author'] = author
        item['industry_categories'] = 'E'
        item['industry_Lcategories'] = '49'
        item['industry_Mcategories'] = None
        item['industry_Scategories'] = None
        item['information_categories'] = '新闻资讯'
        item['information_source'] = '建筑英才网'
        item['content'] = content
        item['images'] = None
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

    cmdline.execute(['scrapy', 'crawl', 'newsBuildhr_V1'])
