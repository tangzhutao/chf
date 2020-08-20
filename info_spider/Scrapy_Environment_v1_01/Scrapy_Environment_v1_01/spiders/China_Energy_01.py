import scrapy, time
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class ChinaEcology01Spider(scrapy.Spider):
    name = 'China_Energy_01'

    base_url = 'http://www.nea.gov.cn/'
    url_name = '中华人民共和国能源局'
    urls = {
        '能源局通知-17': 'http://www.nea.gov.cn/policy/tz.htm',
        '能源局公告-10': 'http://www.nea.gov.cn/policy/gg.htm',
        '能源局项目核准-6': 'http://www.nea.gov.cn/policy/xmsp.htm',
    }

    def start_requests(self):
        for key, value in self.urls.items():
            # for i in range(int(key.split('-')[-1])):
            for i in range(2):
                if i == 0:
                    url = value
                else:
                    url = value[:-4] + f'_{i + 1}.htm'
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'base_url': value})
                yield req

    def parse(self, response):
        links = response.xpath('//div[@class="box01"]/ul/li/a/@href').extract()
        for li in links:
            if 'zfxxgk.nea.gov.cn' in li:
                req = scrapy.Request(url=li, callback=self.detail_parse, dont_filter=True)
                news_id = request.request_fingerprint(req)
                req.meta.update({'news_id': news_id})
                yield req
            elif 'www.nea.gov.cn' in li:
                req = scrapy.Request(url=li, callback=self.detail_parse1, dont_filter=True)
                news_id = request.request_fingerprint(req)
                req.meta.update({'news_id': news_id})
                yield req

    def detail_parse(self, response):
        title = response.xpath('//div[@class="article-content"]/table[2]/tbody/tr[1]/td[2]/text()').extract_first()
        issue_time = response.xpath('//div[@class="article-content"]/table[2]/tbody/tr[3]/td[2]/text()').extract_first()
        source = response.xpath('//div[@class="article-content"]/table[2]/tbody/tr[2]/td[last()]/text()').extract_first()
        content = response.xpath('//div[@class="article-content"]/table[4]').extract_first()

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = '中华人民共和国能源局'
        item['source'] = source
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
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))

    def detail_parse1(self, response):
        title = response.xpath('//div[@class="titles"]/text()').extract_first().strip()
        issue_time = response.xpath('//span[@class="times"]/text()').extract_first().strip()[5:]
        source = response.xpath('//span[@class="author"]/text()').extract_first().strip()[3:]
        content = response.xpath('//div[@class="article-content"]').extract_first()

        item = InfoItem()
        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = '中华人民共和国能源局'
        item['source'] = source
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
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'China_Energy_01'])
