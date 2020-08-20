# -*- coding: utf-8 -*-
import scrapy, time, re, json
from scrapy.utils import request
import requests
from Scrapy_InternationalEconomic_info_V1_01.items import InfoItem
from urllib3 import encode_multipart_formdata
from Scrapy_InternationalEconomic_info_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'Yicai_01'
    base_url = 'https://www.yicai.com'
    url_name = '第一财经网'

    def start_requests(self):
        for i in range(1):
            link = f'https://www.yicai.com/api/ajax/getlistbycid?cid=52&page={i + 1}&pagesize=50'
            req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
            yield req
            
    def parse(self, response):
        get_info = json.loads(response.text)
        for info in get_info:
            url = self.base_url + info['url']
            title = info['NewsTitle']
            title_images = info['originPic']
            issue_time = info['CreateDate']
            source = info['NewsSource']
            author = info['NewsAuthor']
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id, 'title': title, 'title_images': title_images, 'issue_time': issue_time,
                             'source': source, 'content_url': url, 'author': author})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        # 2020-08-19T11:09:33
        issue_time = time.strftime('%Y-%m-%d', time.strptime(response.meta['issue_time'], '%Y-%m-%dT%H:%M:%S'))
        content = response.xpath('//div[@class="m-txt"]').extract_first()
        images_url = response.xpath('//div[@class="m-txt"]//img/@src').extract()
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
        item['title'] = response.meta['title']
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '第一财经'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        author = response.meta['author']
        item['author'] = author if author else None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = response.meta['source']
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

    cmdline.execute(['scrapy', 'crawl', 'Yicai_01'])
