import scrapy
import json
import time
from Scrapy_OverallBalance_V1_01.items import InfoItem
from scrapy.utils import request


class Qianlong01Spider(scrapy.Spider):
    name = 'Qianlong_01'
    base_url = 'http://www.qianlong.com/'
    url_name = '千龙网'

    def start_requests(self):
        for i in range(6):
            url = f'http://www.qianlong.com/finance/{i + 1}'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        config_info = response.xpath(
            '//div[@class="s_pc_rdjx row"]/div[@class="s_pc_rdjx_box clearfix"]/div[@class="s_pc_rdjx_box_wutu"]/a/@href').extract()
        for url in config_info:
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def parse_detail(self, response):
        # proxy = response.meta['proxy']
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()

        title = response.xpath('//div[@class="row cont"]/h1[@class="title"]/text()').extract_first()
        content = response.xpath(
            '//div[@class="z_cen"]/div[@class="col-xs-12 col-sm-12 col-md-12 col-lg-8"]/div[@class="row"]/div[@class="z_cen_box f_size_2 article-content"]').extract_first()
        source = response.xpath(
            '//div[@class="s_laiz clearfix"]/div[@class="s_laiz_box1 col-xs-12 col-sm-12 col-md-12 col-lg-4"]/div[@class="row"]/a/text()').extract_first()
        issue_time = response.xpath(
            '//div[@class="s_laiz clearfix"]/div[@class="s_laiz_box1 col-xs-12 col-sm-12 col-md-12 col-lg-4"]/div[@class="row"]/span/text()').extract_first()
        images_url = response.xpath('//div[@class="z_cen"]/div[@class="col-xs-12 col-sm-12 col-md-12 col-lg-8"]/div[@class="row"]/div[@class="z_cen_box f_size_2 article-content"]//img/@src').extract()

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '综合平衡'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = time.strftime("%Y-%m-%d", time.strptime(issue_time, "%Y-%m-%d %H:%M"))
        item['information_source'] = self.url_name
        item['source'] = source if source else self.url_name
        item['author'] = None
        item['content'] = content
        item['images'] = None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['headers'] = headers
        item['images_url'] = images_url
        # item['proxy'] = proxy
        if item['content']:
            # print(item)
            yield item
            self.logger.info('title: {}, issue_time: {}'.format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Qianlong_01'])
