# -*- coding: utf-8 -*-
import scrapy
from Scrapy_D44_info_V1_01.items import InfoItem
import time
from scrapy.utils import request
# from Scrapy_D44_info_V1_01.start_urls import urls
from datetime import datetime


class PowerinV2Spider(scrapy.Spider):
    name = 'timer'

    urls = {
        # 国际电力网
        'https://power.in-en.com/news/intl/list82-1.html': '国际动态-2',  # «上一页 1 2 ... 3 4 5 6 7 … 1534 1535 下一页»
        'https://power.in-en.com/news/china/list83-2.html': '国内动态-2',  # «上一页 1 2 ... 3 4 5 6 7 … 3241 3242 下一页»
        'https://power.in-en.com/news/focus/list320-2.html': '新闻资讯-2',  # «上一页 1 2 ... 3 4 5 6 7 … 856 857 下一页»
        'https://power.in-en.com/finance/news/list101-2.html': '金融市场-1',
        'https://power.in-en.com/finance/stock/list69-2.html': '金融市场-1',
        'https://power.in-en.com/finance/direction/list102-2.html': '金融市场-1',
        'https://power.in-en.com/tech/news/list327-2.html': '科技资讯-1',
        'https://power.in-en.com/visit/news/list801-2.html': '风云人物-1',
    }
    base_url = 'https://power.in-en.com/'
    url_name = '国际电力网'

    def start_requests(self):

        for url, cate in self.urls.items():
            cates = cate.split('-')
            for num in range(int(cates[1])):
                next_link = url[:-6] + f'{num + 1}.html'
                yield scrapy.Request(url=next_link, callback=self.parse, meta={'cate': cates[0]}, dont_filter=True)

    def parse(self, response):
        cate = response.meta['cate']

        new_urls = response.xpath('//div[@class="slideTxtBox fl"]/ul/li')
        for new_url in new_urls:

            item = InfoItem()

            try:
                title_images = new_url.xpath('./div[@class="imgBox"]/a/img/@src').extract_first()
                item['title_images'] = title_images if title_images else None
            except:
                item['title_images'] = None

            issue_time = new_url.xpath('.//div[@class="prompt"]/i/text()').extract_first()
            if '天前' in issue_time:
                day = (int(issue_time[0])) * 24 * 60 * 60
                new_day = int(time.time()) - day
                issue_time = time.strftime('%Y-%m-%d', time.localtime(new_day))
                # print(issue_time)
            elif '小时' in issue_time:
                issue_time = datetime.now().date().strftime('%Y-%m-%d')
            else:
                pass

            source = new_url.xpath('.//div[@class="prompt"]/span[1]/text()').extract_first()[3:]
            tags = new_url.xpath('.//div[@class="prompt"]/span[2]/em/a/text()').extract()
            tags = '; '.join(tags)
            item['content_url'] = new_url.xpath('.//h5/a/@href').extract_first()
            item['industry_categories'] = 'D'
            item['industry_Lcategories'] = '44'
            item['industry_Mcategories'] = None
            item['industry_Scategories'] = None
            item['information_categories'] = cate
            item['update_time'] = str(int(time.time() * 1000))
            item['issue_time'] = issue_time
            item['source'] = source
            item['tags'] = tags

            req = scrapy.Request(url=item['content_url'], callback=self.parse2, meta={'item': item}, dont_filter=True)
            item["id"] = request.request_fingerprint(req)
            yield req

    def parse2(self, response):
        item = response.meta['item']

        item['sign'] = '19'
        item['information_source'] = '国际电力网'
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        item['content'] = response.xpath('//div[@id="article"]').extract_first()
        item['author'] = None

        title1 = response.xpath('//div[@class="leftBox fl"]/h1/text()').extract_first()
        title2 = response.xpath('//div[@class="c_content"]/h1/text()').extract_first()
        if title1:
            item['title'] = title1
        elif title2:
            item['title'] = title2
        else:
            item['title'] = None

        images = response.xpath('//div[@id="article"]//img/@src').extract()
        if images:
            images_urls = '; '.join(images)
            item['images'] = images_urls if images_urls else None
        else:
            item['images'] = None

        if item['content']:
            yield item
            self.logger.info("title:{},issue_time:{}".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'timer'])
