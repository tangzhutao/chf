# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Literature_V1_01.items import InfoItem
from urllib3 import encode_multipart_formdata
from Scrapy_Literature_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class InternationalEconomicSpider(scrapy.Spider):
    name = 'HuanqiuCul_01'
    base_url = 'https://cul.huanqiu.com/'
    url_name = '环球网'
    # image_path = r'E:\Literature\文艺\环球网\images'
    # if not os.path.exists(image_path):
    #     os.makedirs(image_path)

    def start_requests(self):
        urls = ['https://cul.huanqiu.com/api/list2?node=/e3pn677q4/e7n7nshou-560', 'https://cul.huanqiu.com/api/list2?node=/e3pn677q4/e7n7qip93-120']
        for url in urls:
            for i in range(1):
                offset = 20 * i
                if offset < int(url.split('-')[-1]):
                    link = url.split('-')[0] + f'&offset={offset}&limit=20'
                    req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
                    yield req

    def parse(self, response):
        base_url = 'https://cul.huanqiu.com/article/'
        get_info = json.loads(response.text)
        for info in get_info['list']:
            if info:
                aid = info['aid']
                url = base_url + aid
                req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
                news_id = request.request_fingerprint(req)
                req.meta.update({'news_id': news_id})
                yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="t-container-title"]/h3/text()').extract_first()
        source = response.xpath('//span[@class="source"]//text()').extract()[1]
        source = [x.strip() for x in source if x.strip()]
        author = response.xpath('//span[@class="author"]//text()').extract()[0][3:]
        issue_time = response.xpath('//p[@class="time"]/text()').extract_first()
        content = response.xpath('//article').extract_first()
        images_url = response.xpath('//article//img/@src').extract()
        item = InfoItem()

        try:
            images = []
            if images_url:
                for url in images_url:
                    if ('http' not in url) and ('https' not in url):
                        url = self.base_url + url
                    res = self.download_img(url, headers)
                    if res['success']:
                        self.logger.info({'图片下载完成': url})
                        images.append(res['data']['url'])
                    else:
                        self.logger.info({'图片下载失败': url})
            item['images'] = ','.join(images) if images else None
        except IndexError:
            item['images'] = None

        item['category'] = '文艺'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = time.strftime("%Y-%m-%d", time.strptime(issue_time, "%Y-%m-%d %H:%M")) if issue_time else None
        item['information_source'] = '环球网'
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

    cmdline.execute(['scrapy', 'crawl', 'HuanqiuCul_01'])
