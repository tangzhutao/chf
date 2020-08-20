# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Philosophy_V1_01.items import ChinawuliuG58ZxItem
from urllib3 import encode_multipart_formdata
from Scrapy_Philosophy_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'TheoryPeople_01'
    base_url = 'http://theory.people.com.cn'
    url_name = '人民网'
    image_path = r'E:\Philosophy\哲学\人民网\images'

    def start_requests(self):
        for i in range(1):
            link = f'http://theory.people.com.cn/GB/49157/index{i + 1}.html'
            req = scrapy.Request(url=link, callback=self.parse)
            yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="fl"]/ul/li/a/@href').extract()
        # print(get_info)
        for info in get_info:
            url = self.base_url + info
            # print(url)
            req = scrapy.Request(url=url, callback=self.detail_parse)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="text_c"]/h1/text()').extract_first()
        author = response.xpath('//p[@class="sou1"]/text()').extract_first()
        source = response.xpath('//p[@class="sou"]/a/text()').extract_first()
        try:
            issue_time = re.findall(r'\d+年\d+月\d+日\d+:\d+',
                                    response.text)[0]
            issue_time = time.strftime('%Y-%m-%d', time.strptime(issue_time, '%Y年%m月%d日%H:%M'))
        except IndexError:
            issue_time = None
        content = response.xpath('//div[@class="show_text"]').extract_first()

        item = ChinawuliuG58ZxItem()
        item['images'] = None
        item['category'] = '哲学'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '人民网'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        item['author'] = author if author else author
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = source if source else None
        # print(item)
        if item['content']:
            yield item
            self.logger.info({'title': item['title'], 'issue_time': item['issue_time'], 'images': item['images']})

    def download_img(self, url, headers):
        resp = requests.get(url, headers=headers)
        file_name = url.split('/')[-1]
        file = {
            'file': (file_name, resp.content)
        }
        send_url = UPLOADURL + SPIDER_NAME
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        headers_from_data = {
            "Content-Type": encode_data[1]
        }
        response = requests.post(url=send_url, headers=headers_from_data, data=file_data).json()
        return response


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'TheoryPeople_01'])
