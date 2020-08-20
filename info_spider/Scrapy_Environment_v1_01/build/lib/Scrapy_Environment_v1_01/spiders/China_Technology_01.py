import scrapy
import time
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class ChinaEcology01Spider(scrapy.Spider):
    name = 'China_Technology_01'

    base_url = 'http://www.miit.gov.cn/'
    url_name = '中华人民共和国工业和信息化部'

    def start_requests(self):
        for i in range(2):
            if i == 0:
                url = 'http://www.miit.gov.cn/n1146295/n1652858/index.html'
            else:
                url = f'http://www.miit.gov.cn/n1146295/n1652858/index_1274678_{181 - i}.html?&tsrcnkcwyad'

            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        links = response.xpath('//div[@class="clist_con"]/ul/li/a/@href').extract()
        for li in links:
            url = self.base_url + li.replace('../', '').replace('./', '')
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        title = response.xpath('//div[@class="ctitle"]/h1/text()').extract_first()
        source = response.xpath('//div[@class="long_gray wryh12black30"]/div[@class="short_l"]/text()').extract_first()[5:]
        issue_time = response.xpath('//div[@class="long_none wryh12black30"]/div[@class="short_r"]/text()').extract_first()[5:]
        content = response.xpath('//div[@class="ccontent center"]').extract_first()
        images = response.xpath('//div[@class="ccontent center"]//img/@src').extract()

        images_url = []
        if images:
            for url in images:
                url = url.replace('../', '').replace('./', '')
                if ('http' not in url) and ('https' not in url):
                    url = self.base_url + url
                images_url.append(url)

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = '中华人民共和国工业和信息化部'
        item['source'] = source if source else None
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
        if content:
            # print(item)
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'China_Technology_01'])
