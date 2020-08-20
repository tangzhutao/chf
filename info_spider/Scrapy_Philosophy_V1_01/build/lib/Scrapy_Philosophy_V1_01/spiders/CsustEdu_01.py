# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Philosophy_V1_01.items import ChinawuliuG58ZxItem
from urllib3 import encode_multipart_formdata
from Scrapy_Philosophy_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'CsustEdu_01'
    base_url = 'https://www.csust.edu.cn/'
    url_name = '马克思主义学院'
    image_path = r'E:\Philosophy\哲学\马克思主义学院\images'

    def start_requests(self):
        for i in range(2):
            if i == 0:
                url = 'https://www.csust.edu.cn/mksxy/zxzx.htm'
            else:
                url = f'https://www.csust.edu.cn/mksxy/zxzx/{17 - i}.htm'
            req = scrapy.Request(url=url, callback=self.parse)
            yield req

    def parse(self, response):
        get_info = response.xpath('//ul[@id="content_news_list"]/li/a/@href').extract()
        for info in get_info:
            if 'mp.weixin.qq.com' not in info:
                url = 'https://www.csust.edu.cn/mksxy/' + info.replace('../', '')
                req = scrapy.Request(url=url, callback=self.detail_parse)
                news_id = request.request_fingerprint(req)
                req.meta.update({'news_id': news_id})
                yield req

    def detail_parse(self, response):
        headers = {}

        title = response.xpath('//span[@class="c124589_title"]/text()').extract_first()
        issue_time = response.xpath('//span[@class="c124589_date"]/text()').extract_first().strip()
        content = response.xpath('//div[@id="vsb_content"]').extract_first()
        item = ChinawuliuG58ZxItem()
        item['images'] = None
        item['category'] = '哲学'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '马克思主义学院'
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
        item['source'] = None
        # print(item)
        if item['content']:
            yield item
            self.logger.info({'title': item['title'], 'issue_time': item['issue_time'],'images': item['images']})

    def download_img(self, url):
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
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

    cmdline.execute(['scrapy', 'crawl', 'CsustEdu_01'])
