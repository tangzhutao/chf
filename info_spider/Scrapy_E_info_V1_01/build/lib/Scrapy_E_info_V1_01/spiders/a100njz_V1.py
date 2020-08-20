# -*- coding: utf-8 -*-
import scrapy, re
import time
from scrapy.utils import request
from Scrapy_E_info_V1_01.items import InfoItem


class A100njzV1Spider(scrapy.Spider):
    name = '100njz_V1'
    allowed_domains = ['www.100njz.com']
    # start_urls = ['https://123/']
    base_url = 'https://www.100njz.com'
    url_name = '百年建筑'

    # 布置定时任务
    urls = {
        'https://www.100njz.com/article/p-5072-------------1.html': '行业资讯2',  # 每页30条
        'https://www.100njz.com/article/p-5076-------------1.html': '国内动态2',
        'https://www.100njz.com/article/p-5073-------------1.html': '市场行情2',
        'https://www.100njz.com/article/p-5075----1001---------1.html': '行业资讯2',
        'https://www.100njz.com/article/p-5079-------------1.html': '风云人物2',
        'https://www.100njz.com/article/p-5078-------------1.html': '企业新闻2',
        'https://www.100njz.com/article/p-5077-------------1.html': '新闻资讯2',
    }

    def start_requests(self):

        for url, cate in self.urls.items():

            page = cate[4:]
            for i in range(1, int(page)):
                link = url.replace(url[-6:-4], f'{i}.')
                i += 1

                yield scrapy.Request(url=link, callback=self.parse, meta={'cate': cate[:4]}, dont_filter=True)

    def parse(self, response):

        cate = response.meta['cate']

        config_list = response.xpath('//ul[@id="list"]/li')

        for config in config_list:
            link = config.xpath('./h3/a/@href').extract_first()
            # print(link)
            if 'http' in link or ('https' in link):
                item = InfoItem()
                title = config.xpath('./h3/a/text()').extract_first()
                item['title'] = title
                # item['issue_time'] = issue_time
                item['content_url'] = link
                item['information_categories'] = cate
                item['title_images'] = None
                req = scrapy.Request(url=link, callback=self.parse2,
                                     meta={'item': item},
                                     dont_filter=True)
                item['id'] = request.request_fingerprint(req)

                yield req

    def parse2(self, response):

        item = response.meta['item']
        content = response.xpath('//div[@id="text"]').extract_first()

        images = response.xpath('//div[@id="text"]//img/@original').extract()
        if images:
            images_url = []
            for img in images:
                if ('http' in img) or ('https' in img):
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
        item['information_source'] = '百年建筑'
        source1 = response.xpath('//div[@class="article-infor"]/span[@class="source"]/a/text()').extract_first()
        try:
            source2 = response.xpath('//div[@class="article-infor"]/span[@class="source"]/text()').extract_first()[
                      3:].strip()
        except:
            source2 = None

        if source1:
            item['source'] = source1
        elif source2:
            item['source'] = source2
        else:
            item['source'] = None
        issue_time = response.xpath('//div[@class="article-infor"]/span[@class="upDate"]/text()').extract_first()[:10]
        item['issue_time'] = issue_time
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        item['author'] = None
        item['content'] = content
        if content:
            yield item
            self.logger.info(
                "title({}), issue_time({}), url({})".format(item['title'], item['issue_time'], item['content_url']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', '100njz_V1'])
