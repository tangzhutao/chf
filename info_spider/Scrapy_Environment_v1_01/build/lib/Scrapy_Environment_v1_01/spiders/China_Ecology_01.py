import scrapy, time
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class ChinaEcology01Spider(scrapy.Spider):
    name = 'China_Ecology_01'

    base_url = 'http://www.mee.gov.cn/'
    url_name = '中华人民共和国生态环境部'

    urls = {
        '中央有关文件-4': 'http://www.mee.gov.cn/zcwj/zyygwj/',
        '国务院有关文件-25': 'http://www.mee.gov.cn/zcwj/gwywj/',
    }

    def start_requests(self):
        for key, value in self.urls.items():
            # for i in range(int(key.split('-')[-1])):
            for i in range(2):
                if i == 0:
                    url = value + 'index.shtml'
                else:
                    url = value + f'index_{i}.shtml'

                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'base_url': value})
                yield req

    def parse(self, response):
        links = response.xpath('//ul[@id="div"]/li/a/@href').extract()
        for li in links:
            url = response.meta['base_url'] + li.replace('../', '').replace('./', '')
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        title = response.xpath('//div[@class="content_body"]/h1/text()').extract_first()
        issue_time = response.xpath('//div[@class="wjkFontBox"]/em[1]/text()').extract_first()[5:]
        # source = response.xpath('//div[@class="wjkFontBox"]/em[2]/text()').extract_first()[3:]
        content = response.xpath('//div[@class="content_body_box"]').extract_first()
        # print(title, issue_time, source)

        item = InfoItem()

        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = '中华人民共和国生态环境部'
        item['source'] = '中华人民共和国生态环境部'
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
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'China_Ecology_01'])
