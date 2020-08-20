# -*- coding: utf-8 -*-
import scrapy, re
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class MysteelV1Spider(scrapy.Spider):
    name = 'mySteel_V1'
    allowed_domains = ['news.mysteel.com']
    base_url = 'https://news.mysteel.com'
    url_name = '我的钢铁网'
    urls = {
        # 50-市场行情-772   行业分类-资讯分类-页数
        'https://news.mysteel.com/article/p-4651-------------1.html': '50-市场行情-1',  # 每页30条
        'https://news.mysteel.com/article/p-4652-------------1.html': '50-行业资讯-1',
        'https://news.mysteel.com/article/p-286-------------1.html': '48-行业资讯-1',
        'https://news.mysteel.com/article/p-5438-------------1.html': '48-国内动态-2',
        'https://news.mysteel.com/article/p-5439-------------1.html': '48-国际动态-1',
        'https://news.mysteel.com/article/p-323-------------1.html': '48-政策法规-1',

    }

    def start_requests(self):
        for url, cate in self.urls.items():
            page = cate[8:]
            for i in range(int(page)):
                link = url.replace(url[-6:-4], f'{i + 1}.')
                i += 1
                yield scrapy.Request(url=link, callback=self.parse,
                                     meta={'cate': cate[3:7], 'industry_Lcategories': cate[:2]}, dont_filter=True)

    def parse(self, response):

        cate = response.meta['cate']
        industry_Lcategories = response.meta['industry_Lcategories']
        # print(cate)
        config_list = response.xpath('//ul[@id="news"]/li')

        for config in config_list:
            issue_time = config.xpath('.//p[@class="date"]/text()').extract_first()
            if '-' in issue_time:
                item = InfoItem()
                # title_img = config.xpath('./a/img/@src').extract_first()
                title = config.xpath('./h3/a/text()').extract_first()
                link = config.xpath('./h3/a/@href').extract_first()
                if 'http' in link:
                    link = link
                else:
                    link = f'https:' + config.xpath('./h3/a/@href').extract_first()
                item['title'] = title
                item['issue_time'] = issue_time[:10]
                item['content_url'] = link
                item['information_categories'] = cate
                item['title_images'] = None
                req = scrapy.Request(url=link, callback=self.parse2,
                                     meta={'item': item, 'industry_Lcategories': industry_Lcategories},
                                     dont_filter=True)
                item['id'] = request.request_fingerprint(req)

                yield req

    def parse2(self, response):
        industry_Lcategories = response.meta['industry_Lcategories']
        item = response.meta['item']
        content = response.xpath('//div[@id="text"]').extract_first()

        images = response.xpath('//div[@id="text"]//img/@original').extract()
        if images:
            images_url = []
            for img in images:
                if 'http' in img:
                    images_url.append(img)
                else:
                    image = f'https:{img}'
                    images_url.append(image)
            images_urls = '; '.join(images_url)
            item['images'] = images_urls if images_urls else None
        else:
            item['images'] = None
        item['tags'] = None
        item['industry_categories'] = 'E'
        item['industry_Lcategories'] = industry_Lcategories
        item['industry_Mcategories'] = None
        item['industry_Scategories'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['information_source'] = '我的钢铁网'

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
            item['source'] = '我的钢铁网'

        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        item['author'] = None
        item['content'] = content
        if content:
            yield item
            self.logger.info("title({}), issue_time({})".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'mySteel_V1'])
