# -*- coding: utf-8 -*-
import scrapy, time, re
from scrapy.utils import request
from Scrapy_History_Hanchao_V1_01.items import InfoItem
import requests
from urllib3 import encode_multipart_formdata
from Scrapy_History_Hanchao_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Gs500001Spider(scrapy.Spider):
    name = 'Y5000_01'
    base_url = 'https://www.y5000.com'
    url_name = '中国历史网'

    def start_requests(self):
        for i in range(3):
            if i == 0:
                url = 'https://www.y5000.com/zgls/qh/'
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                yield req
            else:
                url = f'https://www.y5000.com/zgls/qh/p{i + 1}/'
                req = scrapy.Request(url, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="lzw_cont"]/h6/a/@href').extract()
        for info in get_info:
            req = scrapy.Request(url=info, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="lct_tit"]/h1/text()').extract_first()
        issue_time = response.xpath('/html/body/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/p/span[1]/em/text()').extract_first()
        author = response.xpath('//html/body/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/p/span[2]/em/text()').extract_first()
        content = response.xpath('//div[@class="lct_cont"]').extract_first()
        images_url = response.xpath('//div[@class="lct_cont"]//img/@src').extract()
        item = InfoItem()
        images = []
        if images_url:
            for image_url in images_url:
                if 'http' in image_url:
                    link = image_url
                else:
                    link = self.base_url + image_url
                res = self.download_img(link, headers)
                if res['success']:
                    self.logger.info({'图片下载完成': link})
                    images.append(res['data']['url'])
                else:
                    self.logger.info({'图片下载失败': link})

        item['images'] = ','.join(images) if images else None
        item['category'] = '汉朝'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '中国历史网'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        item['author'] = author
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = None
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

    cmdline.execute(['scrapy', 'crawl', 'Y5000_01'])

