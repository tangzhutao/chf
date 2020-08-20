# -*- coding: utf-8 -*-
import scrapy, time, re, json, os, requests
from scrapy.utils import request
from Scrapy_Literature_V1_01.items import InfoItem
from urllib3 import encode_multipart_formdata
from Scrapy_Literature_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL



class InternationalEconomicSpider(scrapy.Spider):
    name = 'ArtIfeng_01'
    base_url = 'http://art.ifeng.com'
    url_name = '凤凰艺术'
    # image_path = r'E:\Literature\文艺\凤凰艺术\images'
    # if not os.path.exists(image_path):
    #     os.makedirs(image_path)

    def start_requests(self):
        # 300
        for i in range(5):
            url = f'http://app.art.ifeng.com/?app=system&controller=fall&action=freelist_page&flid=1&jsoncallback=jsonp1591860636813&page={i + 1}&_=1591860722987'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = json.loads(response.text[19:-1])
        for info in get_info:
            url = info['url']
            tags = info['tags'].replace(' ', ',')
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id, 'tags': tags})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//h3[@class="h3"]/text()').extract_first()
        source_list = response.xpath('//p[@class="info"]//text()').extract()
        source_info = [x.strip() for x in source_list if x.strip() != '']
        if len(source_info) == 2:
            source = source_info[0]
            author = None
            issue_time = source_info[1].split(' ')[0]
        elif len(source_info) == 3:
            source = source_info[0]
            author = source_info[1]
            issue_time = source_info[2].split(' ')[0]
        else:
            source = None
            author = None
            issue_time = None
        content = response.xpath('//div[@id="cont_p"]').extract_first()
        images_url = response.xpath('//div[@id="cont_p"]//img/@src').extract()
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
        item['issue_time'] = issue_time
        item['information_source'] = '凤凰艺术'
        item['sign'] = '19'
        item['news_id'] = response.meta['news_id']
        item['content'] = content
        item['author'] = author
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        tags = response.meta['tags']
        item['tags'] = tags if tags else None
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

    cmdline.execute(['scrapy', 'crawl', 'ArtIfeng_01'])
