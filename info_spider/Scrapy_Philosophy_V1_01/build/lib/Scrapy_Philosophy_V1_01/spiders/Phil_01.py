# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Philosophy_V1_01.items import ChinawuliuG58ZxItem
from urllib3 import encode_multipart_formdata
from Scrapy_Philosophy_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'Phil_01'
    base_url = 'http://phil.cssn.cn'
    url_name = '中国哲学网'
    image_path = r'E:\Philosophy\哲学\中国社会科学网\images'
    urls = ['http://phil.cssn.cn/zhx/zx_mkszyzx/', 'http://phil.cssn.cn/zhx/zx_zgzx/',
            'http://phil.cssn.cn/zhx/zx_wgzx/', 'http://phil.cssn.cn/zhx/zx_kxjszx/',
            'http://phil.cssn.cn/zhx/zx_txzl/']

    def start_requests(self):
        for url in self.urls:
            for i in range(3):
                if i == 0:
                    link = url + 'index.shtml'
                else:
                    link = url + f'index_{i}.shtml'
                req = scrapy.Request(url=link, callback=self.parse)
                yield req

    def parse(self, response):
        base_url = 'http://phil.cssn.cn/zhx/zx_mkszyzx'
        get_info = response.xpath('//div[@class="ImageListView"]/ol/li/a/@href').extract()
        for info in get_info:
            if 'http://' in info:
                url = info
            else:
                url = base_url + info[1:]
            req = scrapy.Request(url=url, callback=self.detail_parse)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//span[@class="TitleFont"]/text()').extract_first()
        TitleInfo = response.xpath('//div[@class="TitleFont2"]/text()').extract()[0].strip().split(' ')
        issue_time = time.strftime('%Y-%m-%d', time.strptime(TitleInfo[0], '%Y年%m月%d日')) if TitleInfo else None
        source = TitleInfo[2][3:] if TitleInfo else None
        author = TitleInfo[4][3:] if TitleInfo else None
        content = response.xpath('//div[@class="TRS_Editor"]').extract_first()
        item = ChinawuliuG58ZxItem()

        item['images'] = None
        item['category'] = '哲学'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '中国社会科学网'
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
        item['source'] = source if source else None
        # print(item)
        if item['content']:
            yield item
            self.logger.info({'title': item['title'], 'issue_time': item['issue_time'], 'images': item['images']})

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

    cmdline.execute(['scrapy', 'crawl', 'Phil_01'])
