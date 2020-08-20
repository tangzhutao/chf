# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Philosophy_V1_01.items import ChinawuliuG58ZxItem
from urllib3 import encode_multipart_formdata
from Scrapy_Philosophy_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    # 网站无法访问
    name = 'Chinareform_01'
    base_url = 'https://www.sinoss.net/'
    url_name = '中国改革论坛网'
    urls = ['https://www.sinoss.net/redian/zhexue/36', 'https://www.sinoss.net/redian/lilun/68']
    image_path = r'E:\Philosophy\哲学\中国改革论坛网\images'

    def start_requests(self):
        for i in range(5):
            if i == 0:
                url = 'https://www.chinareform.org.cn/explore/explore/index.htm'
            else:
                url = f'http://www.chinareform.org.cn/explore/explore/index_{i}.htm'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = response.xpath('//span[@class="title"]/a/@href').extract()
        for info in get_info:
            if 'http://' not in info:
                url = 'http://www.chinareform.org.cn/explore/explore/' + info
                req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
                news_id = request.request_fingerprint(req)
                req.meta.update({'news_id': news_id})
                yield req

    def detail_parse(self, response):
        title = response.xpath('//h1[@class="title"]/strong/text()').extract_first()
        info = response.xpath('//p[@class="info"]/text()').extract_first()
        author = re.findall(r'作者：(.+)时间：', info)[0].strip()
        issue_time = re.findall(r'时间：(.+)', info)[0].strip()
        # author = response.xpath('//div[@class="textHeader"]/p/span[2]/text()').extract_first()[3:]
        source = response.xpath('//p[@class="info1"]/text()').extract_first().strip()[3:]
        content = response.xpath('//div[@class="TRS_Editor"]').extract_first()
        images_url = response.xpath('//div[@class="TRS_Editor"]//img/@src').extract()

        images = []
        if images_url:
            for url in images_url:
                if ('http' not in url) and ('https' not in url):
                    url = self.base_url + url
                res = self.download_img(url)
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
        item['information_source'] = '中国改革论坛网'
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
        item['source'] = source if source else '中国改革论坛网'
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

    cmdline.execute(['scrapy', 'crawl', 'Chinareform_01'])
