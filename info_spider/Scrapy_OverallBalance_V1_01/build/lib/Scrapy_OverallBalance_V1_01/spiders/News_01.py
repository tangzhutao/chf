import scrapy
import json
import time
from Scrapy_OverallBalance_V1_01.items import InfoItem
from scrapy.utils import request


class News01Spider(scrapy.Spider):
    name = 'News_01'
    base_url = 'http://www.news.cn/politics/index.htm'
    url_name = '新华时政'

    def start_requests(self):
        for i in range(1):
            url = f'http://qc.wa.news.cn/nodeart/list?nid=113352&pgnum={i + 1}' \
                f'&cnt=50&tp=1&orderby=1?callback=jQuery112404689362246619351_1597392357708&_=1597392357710'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            req.headers['Referer'] = 'http://www.news.cn/politics/index.htm'
            yield req

    def parse(self, response):
        a = 'jQuery112404689362246619351_1597392357708'
        b = len(a) + 1
        config_info = json.loads(response.text[b:-1])['data']['list']
        for info in config_info:
            LinkUrl = info['LinkUrl']
            title = info['Title']
            author = info['Author']
            issue_time = time.strftime("%Y-%m-%d", time.strptime(info['PubTime'], "%Y-%m-%d %H:%M:%S"))
            req = scrapy.Request(url=LinkUrl, callback=self.parse_detail, dont_filter=True,
                                 meta={'title': title, 'issue_time': issue_time, 'author': author})
            news_id = request.request_fingerprint(req)
            req.meta.update({"news_id": news_id})
            req.headers['Referer'] = 'http://www.news.cn/politics/index.htm'
            yield req

    def parse_detail(self, response):
        base_url = response.url.split('/')[:-1]
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        content = response.xpath('//div[@id="p-detail"]').extract_first()
        source = response.xpath('//em[@id="source"]/text()').extract_first()
        images = response.xpath('//div[@id="p-detail"]//img/@src').extract()
        author = response.meta['author']
        # print(images)
        images_url = []
        if images:
            for uri in images:
                if '.gif' not in uri:
                    if 'http' not in uri or ('https' not in uri):
                        base_url.append(uri)
                        uri = '/'.join(base_url)
                    images_url.append(uri)
        # print(images_url)
        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '综合平衡'
        item['content_url'] = response.url
        item['title'] = response.meta['title']
        item['issue_time'] = response.meta['issue_time']
        item['information_source'] = self.url_name
        item['source'] = source if source else self.url_name
        item['author'] = author
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
        if item['content']:
            # print(item)
            yield item
            self.logger.info('title: {}, issue_time: {}'.format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'News_01'])
