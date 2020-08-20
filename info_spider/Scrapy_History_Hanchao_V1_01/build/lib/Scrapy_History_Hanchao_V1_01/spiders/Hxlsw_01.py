# -*- coding: utf-8 -*-
import scrapy, time, re
from scrapy.utils import request
from Scrapy_History_Hanchao_V1_01.items import InfoItem
import requests
from urllib3 import encode_multipart_formdata
from Scrapy_History_Hanchao_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Gs500001Spider(scrapy.Spider):
    name = 'Hxlsw_01'
    base_url = 'http://www.hxlsw.com/'
    url_name = '中国古代历史网'


    urls = {
        'http://www.hxlsw.com/history/xihan/hanmr/list_1054_': '汉朝名人-3',
        'http://www.hxlsw.com/history/xihan/gs/list_132_': '历史概述-3',
        'http://www.hxlsw.com/history/xihan/xhjs/list_363_': '西汉事件-3',
    }

    def start_requests(self):
        for url, cate in self.urls.items():
            page = int(cate.split('-')[1])
            for i in range(page):
                link = url + f'{i + 1}.html'
                req = scrapy.Request(url=link, callback=self.parse)
                yield req

    def parse(self, response):
        get_info = response.xpath('//ul[@id="news_list"]//h3/a/@href').extract()
        for info in get_info:
            req = scrapy.Request(url=info, callback=self.detail_parse)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="title"]/h1/text()').extract_first()
        issue_time = response.xpath('//span[@class="date"]/text()').extract_first().split(' ')[1]
        content = response.xpath('//div[@id="m-news-detail"]').extract_first()
        # images_url = response.xpath('//div[@id="m-news-detail"]//img/@src').extract()
        item = InfoItem()

        item['images'] = None

        item['category'] = '汉朝'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '中华历史网'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        item['author'] = None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = '中华历史网'
        # print(item)
        if content:
            yield item
            self.logger.info({'title': title, 'issue_time': issue_time})

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

    cmdline.execute(['scrapy', 'crawl', 'Hxlsw_01'])
