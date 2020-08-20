import scrapy, time, re
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class ChinaEcology01Spider(scrapy.Spider):
    name = 'China_Natural_01'
    base_url = 'http://f.mnr.gov.cn/'
    url_name = '中华人民共和国自然资源部'

    def start_requests(self):
        for i in range(2):
            if i == 0:
                url = self.base_url + 'index_3553.html'
            else:
                url = self.base_url + f'index_3553_{i}.html'

            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        links = response.xpath('//ul[@id="ul"]/li')
        for li in links:
            url = self.base_url + li.xpath('./div[@class="ffbox"]/a[2]/@href').extract_first()[2:]
            info = li.xpath('./a/text()').extract_first()
            date = re.findall(r'\d+年\d+月\d+日', info)[0]
            issue_time = time.strftime("%Y-%m-%d", time.strptime(date, "%Y年%m月%d日"))

            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id, "issue_time": issue_time})
            yield req

    def detail_parse(self, response):
        title = response.xpath('//div[@id="country"]/div[@class="dtl-top"]/em/text()').extract_first()
        source = response.xpath('//div[@id="country"]/div[@class="dtl-middle"]/div[@class="mid-2"]/span[2]/text()').extract_first()
        content = response.xpath('//div[@id="content"]').extract_first()
        # print(title, issue_time, source, tags)

        item = InfoItem()

        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = response.meta['issue_time']
        item['information_source'] = '中华人民共和国自然资源部'
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

        item['headers'] = None
        item['images_url'] = None
        if content:
            # print(item)
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(title, response.meta['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'China_Natural_01'])
