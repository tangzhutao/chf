# -*- coding: utf-8 -*-
import scrapy, time, re, json
from scrapy.utils import request
import requests
from Scrapy_InternationalEconomic_info_V1_01.items import InfoItem
from urllib3 import encode_multipart_formdata
from Scrapy_InternationalEconomic_info_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'ForexXinhua_01'
    base_url = 'http://forex.xinhua08.com'
    url_name = '新华外汇'

    def start_requests(self):
        for i in range(1):
            url = f'http://forex.xinhua08.com/waihui/{i + 1}.shtml'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="newsinfo"]/a/@href').extract()
        for info in get_info:
            req = scrapy.Request(url=info, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="mainContent pt0"]/h1/text()').extract_first()
        source = response.xpath('//div[@class="pull-left hidden-xs"]/span[1]/text()').extract_first()
        try:
            issue_time = re.findall(r'\d+年\d+月\d+日\d+:\d+',
                                    response.text)[0]
            issue_time = time.strftime('%Y-%m-%d', time.strptime(issue_time, '%Y年%m月%d日%H:%M'))
        except IndexError:
            issue_time = None
        content = response.xpath('//div[@id="ctrlfscont"]').extract_first()
        images_url = response.xpath('//div[@id="ctrlfscont"]//img/@src').extract()

        # print(images_url)
        images = []
        if images_url:
            for url in images_url:
                if ('http' not in url) and ('https' not in url):
                    url = self.base_url + url
                # print(url)
                res = self.download_img(url, headers)
                if res['success']:
                    self.logger.info({'图片下载完成': url})
                    images.append(res['data']['url'])
                else:
                    self.logger.info({'图片下载失败': url})

        item = InfoItem()
        item['images'] = ','.join(images) if images else None
        item['category'] = '国际经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '新华财经'
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
        item['source'] = source if source else None
        if item['content']:

            yield item
            self.logger.info({'title': item['title'], 'issue_time': item['issue_time']})

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

    cmdline.execute(['scrapy', 'crawl', 'ForexXinhua_01'])
