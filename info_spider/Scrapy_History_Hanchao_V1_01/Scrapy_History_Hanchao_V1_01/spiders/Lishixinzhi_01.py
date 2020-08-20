# -*- coding: utf-8 -*-
import scrapy, time, re
from scrapy.utils import request
from Scrapy_History_Hanchao_V1_01.items import InfoItem
import requests
from urllib3 import encode_multipart_formdata
from Scrapy_History_Hanchao_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Lishixinzhi01Spider(scrapy.Spider):
    name = 'Lishixinzhi_01'
    base_url = 'https://www.lishixinzhi.com'
    url_name = '历史新知网'


    def start_requests(self):
        for i in range(3):
            if i == 0:
                url = 'https://www.lishixinzhi.com/lishi/hanchaolishi.html'
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                yield req
            else:
                url = f'https://www.lishixinzhi.com/lishi/hanchaolishi_{i + 1}.html'
                req = scrapy.Request(url, callback=self.parse, dont_filter=True)
                yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="list"]/ul/li//h3/a/@href').extract()
        for info in get_info:
            req = scrapy.Request(url=info, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="t"]/h3/a/text()').extract_first()
        try:
            issue_time = re.findall(r'\d+/\d+/\d+ \d+:\d+', response.text)[0].split(' ')[0]
        except IndexError:
            issue_time = None
        tags = response.xpath('//div[@class="t"]/a/text()').extract()
        content = response.xpath('//div[@class="article_content"]').extract_first()
        images_url = response.xpath('//div[@class="article_content"]//img/@src').extract()
        item = InfoItem()
        images = []
        if images_url:
            for image_url in images_url:
                if 'https' in image_url:
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
        item['issue_time'] = issue_time.replace('/', '-') if issue_time else None
        item['information_source'] = '历史新知'
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

    cmdline.execute(['scrapy', 'crawl', 'Lishixinzhi_01'])
