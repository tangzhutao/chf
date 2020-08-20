# -*- coding: utf-8 -*-
import scrapy, time, re
from scrapy.utils import request
from Scrapy_History_Hanchao_V1_01.items import InfoItem
import requests
from urllib3 import encode_multipart_formdata
from Scrapy_History_Hanchao_V1_01.ApolloConfig import IMAGES_STORE, SPIDER_NAME, UPLOADURL


class Gs500001Spider(scrapy.Spider):
    name = 'Baiduzixun_01'
    base_url = 'https://www.baidu.com'
    url_name = '百度资讯'

    def start_requests(self):

        for i in range(3):
            link = f'https://www.baidu.com/s?ie=utf-8&cl=2&medium=2&rtt=4&bsst=1&rsv_dl=news_b_pn&tn=news&word=%E6%B1%89%E6%9C%9D&x_bfe_rqs=03E80&x_bfe_tjscore=0.531946&tngroupname=organic_news&newVideo=12&pn={i * 10}'
            req = scrapy.Request(url=link, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        get_info = response.xpath('//h3[@class="news-title_1YtI1"]')
        for info in get_info:
            link = info.xpath('./a/@href').extract_first()
            # author = info.xpath('./following-sibling::div[1]//p[@class="c-author"]/text()').extract()[1].strip().replace('\xa0', '').replace(' ', '').replace('\t', '').split('\n')[0]
            # issue_time = info.xpath('./following-sibling::div[1]//p[@class="c-author"]/text()').extract()[1].strip().replace('\xa0', '').replace(' ', '').replace('\t', '').split('\n')[1]
            # if '分钟前' in issue_time or '小时前' in issue_time:
            #     issue_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            # else:
            #     a = time.strptime(issue_time, '%Y年%m月%d日%H:%M')
            #     issue_time = time.strftime('%Y-%m-%d', a)
            req = scrapy.Request(url=link, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="article-title"]/h2/text()').extract_first()
        author = response.xpath('//p[@class="author-name"]/text()').extract_first()
        issue_time = str(time.localtime().tm_year) + response.xpath('//span[@class="date"]/text()').extract_first()[5:]
        content = response.xpath('//div[@class="article-content"]').extract_first()
        images_url = response.xpath('//div[@class="article-content"]//img/@src').extract()
        item = InfoItem()

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

        item['category'] = '汉朝'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time if issue_time else None
        item['information_source'] = '百家号'
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
        item['source'] = '百家号'
        if content:
            # print(item)
            yield item
            self.logger.info({'title': title, 'issue_time': issue_time})

    def download_img(self, url, headers):
        resp = requests.get(url, headers=headers)
        file_name = url.split('/')[-1].split('?')[0]
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

    cmdline.execute(['scrapy', 'crawl', 'Baiduzixun_01'])
