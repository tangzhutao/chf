# -*- coding: utf-8 -*-
import scrapy, time, re, json
from scrapy.utils import request
import requests
from Scrapy_InternationalEconomic_info_V1_01.items import InfoItem
from urllib3 import encode_multipart_formdata
from Scrapy_InternationalEconomic_info_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Gs500001Spider(scrapy.Spider):
    name = 'Hexun_01'
    base_url = 'http://news.hexun.com'
    url_name = '和讯网'

    def start_requests(self):
        # 数据共69页
        for i in range(1):
            link = f'https://opentool.hexun.com/MongodbNewsService/newsListPageByJson.jsp?id=108511065&s=100&cp={i + 1}&priority=0&callback=hx_json41591064954437'
            req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = json.loads(response.text.replace('hx_json41591064954437( ', '').replace(')', ''))
        for info in get_info['result']:
            url = info['entityurl']
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="layout mg articleName"]/h1/text()').extract_first()
        source = response.xpath('//div[@class="tip fl"]/a/text()').extract_first()
        # source2 = response.xpath('//div[@class="source data-source"]/text()').extract()[1]
        try:
            issue_time = re.findall(r'\d+-\d+-\d+ \d+:\d+:\d+',
                                    response.text)[0]
            issue_time = time.strftime('%Y-%m-%d', time.strptime(issue_time, '%Y-%m-%d %H:%M:%S'))
        except IndexError:
            issue_time = None
        content = response.xpath('//div[@class="art_context"]').extract_first()
        images_url = response.xpath('//div[@class="art_context"]//img/@src').extract()

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
        item['information_source'] = '和讯新闻'
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
        item['source'] = source
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

    cmdline.execute(['scrapy', 'crawl', 'Hexun_01'])
