# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Philosophy_V1_01.items import ChinawuliuG58ZxItem
from urllib3 import encode_multipart_formdata
from Scrapy_Philosophy_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'HttpCn_01'
    base_url = 'http://zhexue.httpcn.com/'
    url_name = '汉程网'
    urls = ['http://zhexue.httpcn.com/list/PWPWCQ/2', 'http://zhexue.httpcn.com/list/PWPWPW/2',
            'http://zhexue.httpcn.com/list/PWPWKO/2', 'http://zhexue.httpcn.com/list/PWPWIL/2']
    image_path = r'E:\Philosophy\哲学\汉程网\images'

    def start_requests(self):
        for url in self.urls:
            for i in range(int(url[-1:])):
                link = url[:-1] + f'?page={i + 1}'
                req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="info-content"]/h3/a/@href').extract()
        for info in get_info:
            url = 'http:' + info
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="readNove_top newNove_top"]/h1/text()').extract_first()
        source = response.xpath('//div[@class="readBook_meas clear"]/span[2]/text()').extract_first()
        try:
            issue_time = re.findall(r'\d+-\d+-\d+ \d:\d+:\d+',
                                    response.text)[0].split(' ')[0]
            issue_time = time.strftime('%Y-%m-%d', time.strptime(issue_time, '%Y-%m-%d'))
        except IndexError:
            issue_time = None
        content = response.xpath('//div[@class="contentBox"]').extract_first()
        images_url = response.xpath('//div[@class="contentBox"]//img/@src').extract()

        images = []
        if images_url:
            for url in images_url:
                if 'http://' not in url:
                    url = 'http:' + url
                res = self.download_img(url, headers)
                if res['success']:
                    self.logger.info({'图片下载成功': url})
                    images.append(res['data']['url'])
                else:
                    self.logger.info({'图片下载失败': url})
        item = ChinawuliuG58ZxItem()
        item['images'] = ','.join(images) if images else None
        item['category'] = '哲学'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '汉程网'
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
        item['source'] = source[3:] if source else None
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

    cmdline.execute(['scrapy', 'crawl', 'HttpCn_01'])
