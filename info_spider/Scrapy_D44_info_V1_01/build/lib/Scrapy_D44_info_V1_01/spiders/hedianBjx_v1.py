# -*- coding: utf-8 -*-
import scrapy
from Scrapy_D44_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class HedianbjxV1Spider(scrapy.Spider):
    name = 'hedianBjx_v1'
    allowed_domains = ['hedian.bjx.com.cn', 'news.bjx.com.cn']

    urls = {
        'http://hedian.bjx.com.cn/NewsList?': '新闻资讯',
        'http://hedian.bjx.com.cn/NewsList?id=82': '国际动态',
        'http://hedian.bjx.com.cn/NewsList?id=103': '国内动态',
        'http://hedian.bjx.com.cn/NewsList?id=88': '行业技术',
        'http://hedian.bjx.com.cn/NewsList?id=84': '风云人物',
        'http://hedian.bjx.com.cn/NewsList?id=76': '企业新闻',
        'http://hedian.bjx.com.cn/NewsList?id=89': '金融市场',
        'http://hedian.bjx.com.cn/NewsList?id=85': '金融市场',
    }
    base_url = 'http://hedian.bjx.com.cn/'
    url_name = '北极星核电网'


    # 初始网址
    def start_requests(self):
        for url, cate in self.urls.items():
            for i in range(3):
                link = url + f'&page={i + 1}'
                yield scrapy.Request(url=link, callback=self.parse, meta={'cate': cate, 'url': url}, dont_filter=True)

    def parse(self, response):
        cate = response.meta['cate']

        # 获取本页所有的新闻链接
        node_list = response.xpath('//div[@class="list_left"]/ul/li')
        for node in node_list:
            link_list = node.xpath('./a/@href').extract_first()
            if link_list:
                item = InfoItem()
                item['content_url'] = link_list
                item['issue_time'] = node.xpath('./span/text()').extract_first()
                req = scrapy.Request(url=link_list, callback=self.parse2, meta={'item': item, 'cate': cate}, dont_filter=True)
                item["id"] = request.request_fingerprint(req)
                yield req

    def parse2(self, response):
        cate = response.meta['cate']
        item = response.meta['item']

        item['title'] = response.xpath('//div[@class="list_detail"]/h1/text()').extract_first()

        source1 = ''.join(response.xpath(
            '//div[@class="list_detail"]/div[@class="list_copy"]/b[1]//text()').extract())
        source2 = ''.join(response.xpath(
            '//div[@class="list_detail"]/div[@class="tempa list_copy btemp"]/b[1]//text()').extract())
        if source1:
            item['source'] = source1[3:]
        elif source2:
            item['source'] = source2[3:]
        else:
            item['source'] = None

        item['information_source'] = '北极星核力发电网'

        tags1 = ';'.join(response.xpath(
            '//div[@class="list_detail"]/div[@class="list_key"]/a/text()').extract())
        tags2 = ';'.join(response.xpath(
            '//div[@class="list_detail"]/div[@class="tempa list_key btemp"]/a/text()').extract())
        if tags1:
            item['tags'] = None if tags1 == ';' else tags1
        elif tags2:
            item['tags'] = None if tags2 == ';' else tags2
        else:
            item['tags'] = None

        item['industry_categories'] = 'D'
        item['industry_Lcategories'] = '44'
        item['industry_Mcategories'] = '441'
        item['industry_Scategories'] = '4414'
        item['information_categories'] = cate
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        image_url = ';'.join(
            response.xpath('//div[@class="list_detail"]/div[@id="content"]//p//img/@data-echo').extract())
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

        content = response.xpath('//div[@class="list_detail"]/div[@id="content"]').extract_first()
        item['content'] = content if content else None

        # 如果内容有多页，则继续爬取content and images，没有就yield item
        next_page1 = response.xpath('//div[@class="page"]/a[@title="下一页"]/@href').extract_first()
        next_page2 = response.xpath('//div[@class="tempa page btemp"]/a[@title="下一页"]/@href').extract_first()
        if next_page1:
            content_url = item['content_url']
            next_content_url = content_url.replace(content_url[-6:], next_page1[-8:])
            yield scrapy.Request(url=next_content_url, callback=self.parse3, meta={'item': item}, dont_filter=True)
        elif next_page2:
            content_url = item['content_url']
            next_content_url = content_url.replace(content_url[-6:], next_page2[-8:])
            yield scrapy.Request(url=next_content_url, callback=self.parse3, meta={'item': item}, dont_filter=True)
        else:
            yield item
            self.logger.info("title:{},issue_time:{}".format(item['title'], item['issue_time']))

    def parse3(self, response):
        item = response.meta['item']

        # 把之前的内容和下一页的内容拼接起来
        old_content = item['content']
        content = response.xpath('//div[@id="content"]').extract_first()
        if content:
            item['content'] = ('' if old_content is None else old_content) + content
        else:
            item['content'] = old_content

        # 把之前的images和下一页的images拼接起来
        old_images = '' if item['images'] is None else item['images']
        image_url = ';'.join(
            response.xpath('//div[@class="list_detail"]/div[@id="content"]//p//img/@data-echo').extract())
        new_images = old_images + ';' + ('' if image_url is None else image_url)
        new_images = '' if new_images == ';' else new_images
        item['images'] = new_images if new_images else None

        # 如果还有更多的内容，则获取下一页内容链接，没有就yield item
        next_page1 = response.xpath('//div[@class="page"]/a[@title="下一页"]/@href').extract_first()
        next_page2 = response.xpath('//div[@class="tempa page btemp"]/a[@title="下一页"]/@href').extract_first()
        if next_page1:
            content_url = item['content_url']
            next_content_url = content_url.replace(content_url[-6:], next_page1[-8:])
            yield scrapy.Request(url=next_content_url, callback=self.parse3, meta={'item': item}, dont_filter=True)
        elif next_page2:
            content_url = item['content_url']
            next_content_url = content_url.replace(content_url[-6:], next_page2[-8:])
            yield scrapy.Request(url=next_content_url, callback=self.parse3, meta={'item': item}, dont_filter=True)
        else:
            yield item
            self.logger.info("title:{},issue_time:{}".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'hedianBjx_v1'])
