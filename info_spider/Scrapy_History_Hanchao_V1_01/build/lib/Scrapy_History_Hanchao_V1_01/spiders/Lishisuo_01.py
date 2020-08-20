# -*- coding: utf-8 -*-
import scrapy, time, re, requests
from scrapy.utils import request
from Scrapy_History_Hanchao_V1_01.items import InfoItem
from urllib3 import encode_multipart_formdata
from Scrapy_History_Hanchao_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Lishisuo01Spider(scrapy.Spider):
    name = 'Lishisuo_01'
    base_url = 'http://lishisuo.cssn.cn/xsyj/qhs/'
    url_name = '历史所网'


    def start_requests(self):
        for i in range(3):
            if i == 0:
                url = self.base_url + 'index.shtml'
            else:
                url = self.base_url + f'index_{i}.shtml'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = response.xpath('//div[@class="main_r_m"]/ul/li')
        for info in get_info:
            item = InfoItem()
            date = info.xpath('./span/text()').extract_first()
            link = info.xpath('./a/@href').extract_first()
            title = info.xpath('./a/text()').extract_first()
            url = self.base_url + link.replace('./', '')
            item['category'] = '汉朝'
            item['content_url'] = url
            item['title'] = title
            item['issue_time'] = date
            item['information_source'] = '中国历史研究院'
            item['sign'] = '19'
            # print(int(time))
            item['update_time'] = str(int(time.time()*1000))
            req = scrapy.Request(url=url, callback=self.parse2, dont_filter=True, meta={'item': item})
            item['news_id'] = request.request_fingerprint(req)
            yield req

    def parse2(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        item = response.meta['item']
        get_info = response.xpath('//div[@class="main_m"]')
        content = get_info.xpath('.//div[@id="changefont"]/div').extract_first()
        source = get_info.xpath('.//div[@class="riqi"]/text()').extract_first()
        source = re.search('原文刊于：(.+)', source)
        if source:
            item['source'] = source.group(1).strip()
        else:
            item['source'] = None

        images_url = get_info.xpath('.//img/@src').extract()

        images = []
        if images_url:
            for image_url in images_url:
                if 'http' in image_url:
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

        item['content'] = content
        item['author'] = None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        # print(item)
        if content:
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
    cmdline.execute(['scrapy', 'crawl', 'Lishisuo_01'])
