# -*- coding: utf-8 -*-
import scrapy
import re
import json
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class QianjiaV1Spider(scrapy.Spider):
    name = 'qianjia_V1'
    # allowed_domains = ['www.qianjia.com']
    # start_urls = ['http://www.qianjia.com/']
    base_url = 'https://www.qianjia.com/'
    url_name = '千家网'
    url1 = {
        # 50-市场行情-772   行业分类-资讯分类-页数
        '49-新闻资讯-2': 'https://api.qianjia.com:8444/api/news/GetQiajiaIndexNewsList?pageSize=30&classId=0&moduleSet=0_1&lableId=&pageIndex=',
        '49-新闻资讯-1': 'https://api.qianjia.com:8444/api/news/GetQiajiaIndexNewsList?pageSize=30&classId=1430&moduleSet=0_1&lableId=&pageIndex=',
        '49-行业技术-1': 'https://api.qianjia.com:8444/api/news/GetQiajiaIndexNewsList?pageSize=30&classId=1955&moduleSet=0_1&lableId=&pageIndex=',
        '49-行业资讯-1': 'https://api.qianjia.com:8444/api/news/GetQiajiaIndexNewsList?pageSize=30&classId=1409&moduleSet=0_1&lableId=&pageIndex=',
        '49-产品百科-1': 'https://api.qianjia.com:8444/api/news/GetQiajiaIndexNewsList?pageSize=30&classId=1408&moduleSet=0_1&lableId=&pageIndex=',
        '49-科普资讯-1': 'https://api.qianjia.com:8444/api/news/GetQiajiaIndexNewsList?pageSize=30&classId=1411&moduleSet=0_1&lableId=&pageIndex=',
    }

    def start_requests(self):
        for c, u in self.url1.items():
            cs = c.split('-')
            for i in range(int(cs[2])):
                url = f'{u}{i + 1}'
                req = scrapy.Request(url=url, callback=self.parse, meta={'industry_Lcategories': cs[0], 'information_categories': cs[1]}, dont_filter=True)
                yield req

    def parse(self, response):
        config_list = json.loads(response.text)
        Table = config_list['Data']['Table']
        for t in Table:
            item = InfoItem()
            title = t['Title']
            title_images = t['TitleImage']
            issue_time = t['DateAndTime']
            link = t['LinkUrl'].replace('http', 'https')
            tags = t['LabelName']
            source = t['Source']
            author = t['Author']
            if link:
                req = scrapy.Request(url=link, callback=self.parse_detail, meta={'item': item}, dont_filter=True)
                item['id'] = request.request_fingerprint(req)
                item['title'] = title
                item['title_images'] = title_images if title_images else None
                item['issue_time'] = issue_time[:10] if issue_time else None
                item['tags'] = tags if tags else None
                item['source'] = source if source else '千家智能照明网'
                item['author'] = author if author else None
                item['industry_categories'] = 'E'
                item['industry_Lcategories'] = response.meta['industry_Lcategories']
                item['industry_Mcategories'] = None
                item['industry_Scategories'] = None
                item['information_categories'] = response.meta['information_categories']
                item['content_url'] = link

                yield req

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="article-text"]/article').extract_first()
        images = response.xpath('//div[@class="article-text"]/article//img/@src').extract()
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

        item['information_source'] = '千家智能照明网'
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
    cmdline.execute(['scrapy', 'crawl', 'qianjia_V1'])
