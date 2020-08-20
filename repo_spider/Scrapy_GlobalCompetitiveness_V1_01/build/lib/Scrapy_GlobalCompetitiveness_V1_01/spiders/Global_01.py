import scrapy, hashlib
from Scrapy_GlobalCompetitiveness_V1_01.items import RepoItem
from Scrapy_GlobalCompetitiveness_V1_01.pipelines import MysqlConfig


class Global01Spider(scrapy.Spider):
    name = 'Global_01'
    base_url = 'https://cn.weforum.org/'
    url_name = '世界经济论坛网'
    file_id = hashlib.md5(url_name.encode('utf-8')).hexdigest()

    def start_requests(self):
        p_id = '23'
        p_name = '全球竞争力指数'
        MysqlConfig.insert(p_id, p_name, None, p_name)
        m_id = '23001'
        m_name = '世界经济论坛网'
        MysqlConfig.insert(m_id, m_name, p_id, m_name)

        for i in range(5):
            url = f'https://cn.weforum.org/reports?page={i + 1}'
            # print(url)
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'parent_id': m_id})
            yield req

    def parse(self, response):
        config_info = response.xpath('//div[@class="collection-group collection-group--custom js-scroll"]/div')
        for info in config_info:
            url = info.xpath('./div[@class="report-listing-tout__content"]/div[@class="report-listing-tout__footer"]/a[@class="report-listing-tout__cta"]/@href').extract_first()
            title = info.xpath('./div[@class="report-listing-tout__content"]/div[@class="report-listing-tout__details"]/h4[@class="report-listing-tout__title"]/text()').extract_first().strip()
            link = self.base_url + url
            req = scrapy.Request(url=link, callback=self.parse2, dont_filter=True,
                                 meta={'parent_id': response.meta['parent_id'], 'title': title})
            yield req

    def parse2(self, response):
        parent_id = response.meta['parent_id']
        proxy = response.meta['proxy']
        headers = {}
        for k, v in response.request.headers.items():
            headers[k.decode()] = v[0].decode()
        CHINESENUMBERS = {
            '一': 1,
            '二': 2,
            '三': 3,
            '四': 4,
            '五': 5,
            '六': 6,
            '七': 7,
            '八': 8,
            '九': 9,
            '十': 10,
            '十一': 11,
            '十二': 12
        }

        # pdf_url = response.xpath('//div[@class="report__actions-container"]/a/@href').extract_first()
        pdf_url = response.xpath(
            '//div[@class="report"]/div[@class="row report__display-info"]/div[@class="report__meta"]/a[@class="report__button report__button--padded"]/@href').extract_first()
        date = response.xpath('//div[@class="report__date"]/text()').extract()[1].strip().split(' ')
        issue_time = '{}-{:02d}-{:02d}'.format(date[3], CHINESENUMBERS[date[2][:-1]], int(date[1]))
        item = RepoItem()
        item['headers'] = headers
        item['proxy'] = proxy
        if pdf_url and pdf_url[-3:] == 'pdf':
            item['paper'] = None
            item['paper_abstract'] = None
            item['title'] = response.meta['title']
            item['paper_url'] = pdf_url
            item['date'] = issue_time
            item['paper_from'] = '世界经济论坛'
            item['author'] = None
            item['parent_id'] = parent_id
            item['cleaning_status'] = 0
            item['paper_type'] = 0
            item['image_url'] = None
            # print(item)
            yield item
            self.logger.info("title:{}, date: {}".format(item['title'], item['date']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Global_01'])
