# -*- coding: utf-8 -*-
import scrapy, time, re
from scrapy.utils import request
from Scrapy_History_Hanchao_V1_01.items import InfoItem
import requests
from urllib3 import encode_multipart_formdata
from Scrapy_History_Hanchao_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Shijielishi01Spider(scrapy.Spider):
    name = 'Shijielishi_01'
    base_url = 'http://shijielishi.com'
    url_name = '世界历史网'


    def start_requests(self):
        for i in range(4):
            url = f'http://www.shijielishi.com/han/lishi_{i + 1}.html'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="newList wordWrap"]/ul/li/h3/a/@href').extract()
        for info in get_info:
            # print(info)
            req = scrapy.Request(url=info, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="newDetail"]/h1/text()').extract_first()
        issue_time = response.xpath(
            '//div[@class="newDetail"]//div[@class="fl"]/span[1]/text()').extract_first().replace('时间：', '')
        source = response.xpath('//div[@class="newDetail"]//div[@class="fl"]/span[2]/text()').extract_first().replace(
            '文章来源：', '')
        content = response.xpath('//div[@id="newDetailCont"]').extract_first()
        images_url = response.xpath('//div[@id="newDetailCont"]//img/@src').extract()
        tags = response.xpath('//p[@class="newKeyword"]//a/text()').extract()

        images = []
        for url in images_url:
            if 'http' in url:
                link = url
            else:
                link = self.base_url + url
            res = self.download_img(link, headers)
            if res['success']:
                self.logger.info({'图片下载完成': link})
                images.append(res['data']['url'])
            else:
                self.logger.info({'图片下载失败': link})
        item = InfoItem()
        item['images'] = ','.join(images) if images else None
        item['category'] = '汉朝'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = '世界历史'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        item['author'] = None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = ','.join(tags) if tags else None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = source
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

    cmdline.execute(['scrapy', 'crawl', 'Shijielishi_01'])
