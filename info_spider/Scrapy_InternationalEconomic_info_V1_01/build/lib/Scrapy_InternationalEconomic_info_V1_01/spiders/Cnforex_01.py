# -*- coding: utf-8 -*-
import scrapy, time, re, json, requests
from urllib3 import encode_multipart_formdata
from Scrapy_InternationalEconomic_info_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL
from scrapy.utils import request
from Scrapy_InternationalEconomic_info_V1_01.items import InfoItem


class InternationalEconomicSpider(scrapy.Spider):
    name = 'Cnforex_01'
    base_url = 'http://www.cnforex.com/news/'
    url_name = '环球外汇'

    def start_requests(self):
        link = f'http://www.cnforex.com/news/'
        req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
        yield req

    def parse(self, response):
        get_info = response.xpath('//figcaption/a/@href').extract()
        for info in get_info:
            url = self.base_url + info
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

        link = 'http://www.cnforex.com/news/home/getmore'
        mid = get_info[-1].split('/')[-1][:-5]

        data = {
            'md5': mid
        }
        form_req = scrapy.FormRequest(url=link, formdata=data, callback=self.parse2, dont_filter=True)
        yield form_req

    def parse2(self, response):
        base_url = 'http://www.cnforex.com/news/'
        get_info = json.loads(response.text)
        for info in get_info:
            url = base_url + info['HtmlUrl']
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

        link = 'http://www.cnforex.com/news/home/getmore'
        MD5 = get_info[-1]['MD5']
        data = {
            'md5': MD5
        }
        form_req = scrapy.FormRequest(url=link, formdata=data, callback=self.parse2, dont_filter=True)
        yield form_req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//section/h1/text()').extract_first()
        author = response.xpath('//section/h3/a/text()').extract_first()
        try:
            issue_time = re.findall(r'\d+-\d+-\d+ \d+:\d+',
                                    response.text)[0]
            issue_time = time.strftime('%Y-%m-%d', time.strptime(issue_time, '%Y-%m-%d %H:%M'))
        except IndexError:
            issue_time = None
        content = response.xpath('//article').extract_first()
        images_url = response.xpath('//article//img/@src').extract()

        images = []
        if images_url:
            for url in images_url:
                if 'http' not in url:
                    url = self.base_url + url
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
        item['information_source'] = '环球外汇'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        item['author'] = author if author else None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = '环球外汇'

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

    cmdline.execute(['scrapy', 'crawl', 'Cnforex_01'])
