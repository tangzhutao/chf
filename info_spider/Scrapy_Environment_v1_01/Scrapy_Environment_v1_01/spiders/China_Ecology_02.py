import scrapy, time
from scrapy.utils import request
from Scrapy_Environment_v1_01.items import InfoItem


class ChinaEcology01Spider(scrapy.Spider):
    name = 'China_Ecology_02'

    base_url = 'http://www.mee.gov.cn/'
    url_name = '中华人民共和国生态环境部'

    urls = {
        '部文件令-8': 'http://www.mee.gov.cn/zcwj/bwj/ling/',
        '部文件公告-34': 'http://www.mee.gov.cn/zcwj/bwj/gg/',
        '部文件文件-34': 'http://www.mee.gov.cn/zcwj/bwj/wj/',
        '部文件函-34': 'http://www.mee.gov.cn/zcwj/bwj/han/',
        '办公厅文件函-34': 'http://www.mee.gov.cn/zcwj/bgtwj/han/',
        '办公厅文件文件-34': 'http://www.mee.gov.cn/zcwj/bgtwj/wj/',
        '行政审批文件-34': 'http://www.mee.gov.cn/zcwj/xzspwj/',
        '核安全局文件文件-34': 'http://www.mee.gov.cn/zcwj/haqjwj/wj/',
        '核安全局文件函-34': 'http://www.mee.gov.cn/zcwj/haqjwj/han/',
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
        base_url = 'http://www.mee.gov.cn/'
        links = response.xpath('//ul[@id="div"]/li/a/@href').extract()
        for li in links:
            url = base_url + li.replace('../', '').replace('./', '')
            req = scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True)
            news_id = request.request_fingerprint(req)
            req.meta.update({'news_id': news_id})
            yield req

    def detail_parse(self, response):
        title = response.xpath('//div[@class="content_top_box"]/ul/li[@class="first"]/div/p/text()').extract_first()
        issue_time = response.xpath('//div[@class="content_top_box"]/ul/li[3]/div[2]/text()').extract_first()
        source = response.xpath('//div[@class="content_top_box"]/ul/li[3]/div[1]//text()').extract()[1:]
        tags = response.xpath('//div[@class="content_top_box"]/ul/li[2]/div[2]/text()').extract_first()
        content = response.xpath('//div[@class="content_body_box"]').extract_first()
        # print(title, issue_time, source, tags)

        item = InfoItem()

        item['news_id'] = response.meta['news_id']
        item['category'] = '环保经济'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = issue_time
        item['information_source'] = '中华人民共和国生态环境部'
        item['source'] = ','.join(source) if source else None
        item['author'] = None
        item['content'] = content
        item['images'] = None
        item['title_image'] = None
        item['attachments'] = None
        item['area'] = None
        item['address'] = None
        item['tags'] = tags
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))

        item['headers'] = None
        item['images_url'] = None
        if content:
            yield item
            # self.logger.info('title: {}, issue_time: {}'.format(title, issue_time))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'China_Ecology_02'])
