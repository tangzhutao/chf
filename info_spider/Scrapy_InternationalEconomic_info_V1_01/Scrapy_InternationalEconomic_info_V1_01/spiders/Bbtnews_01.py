# -*- coding: utf-8 -*-
import scrapy, time, re, json, requests
from scrapy.utils import request
from urllib3 import encode_multipart_formdata
from Scrapy_InternationalEconomic_info_V1_01.items import InfoItem
from Scrapy_InternationalEconomic_info_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'Bbtnews_01'
    base_url = 'http://www.bbtnews.com.cn'
    url_name = '北京商报网'

    def start_requests(self):
        for i in range(2):
            link = f'http://www.bbtnews.com.cn/chuizhipd/yaowenzx/guojipd/{i + 1}.shtml'
            req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = response.xpath('//ul[@class="clearfix"]/li/div/h4/a/@href').extract()
        for info in get_info:
            req = scrapy.Request(url=info, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id, 'url': info})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        content_url = response.meta['url']
        news_id = response.meta['news_id']
        title = response.xpath('//div[@class="article-hd"]/h3/text()').extract_first()
        source = response.xpath('//div[@class="info"]/span[1]/text()').extract_first()[3:]
        author = response.xpath('//div[@class="info"]/span[2]/text()').extract_first()[3:]
        issue_time = response.xpath('//div[@class="info"]/span[4]/text()').extract_first()
        content = response.xpath('//div[@id="pageContent"]').extract_first()
        images_url = response.xpath('//div[@id="pageContent"]//img/@src').extract()
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
        item['content_url'] = content_url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = self.url_name
        item['sign'] = '19'
        item['news_id'] = news_id
        item['content'] = content
        item['author'] = author if author else None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['update_time'] = str(int(time.time() * 1000))
        item['source'] = source if source else self.url_name
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

    cmdline.execute(['scrapy', 'crawl', 'Bbtnews_01'])
