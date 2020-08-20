# -*- coding: utf-8 -*-
import scrapy, time, os, requests, json, re, hashlib
from urllib.parse import urlencode
from Scrapy_E_repo_V1_01.items import RepoItem
from urllib3 import encode_multipart_formdata
from Scrapy_E_repo_V1_01.settings import SPIDER_NAME, UPLOADURL
from Scrapy_E_repo_V1_01.pipelines import MysqlConfig


class ScrapyEastmoneyV1Spider(scrapy.Spider):
    name = 'EastMoney_V1'
    allowed_domains = ['data.eastmoney.com/']
    download_url = 'http://pdf.dfcfw.com/pdf/H3_AP202002241375408336_1.PDF'

    base_url = 'http://data.eastmoney.com/report/industry.jshtml'
    url_name = '东方财富'
    file_id = hashlib.md5(url_name.encode('utf-8')).hexdigest()

    CATES_DICT = {
        # 环保工程: 728  工程建设：425
        '5002-土木工程建筑业': ['728-43', '425-22'],
        '5004-建筑装饰、装修和其他建筑业': ['424-42', '725-13'],
        # {'水泥建筑': '424', '装修装饰': '725'},
    }

    # 报告列表接口
    def start_requests(self):
        p_id = '5'
        p_name = '建筑业'
        MysqlConfig.insert(p_id, p_name, None, p_name)

        for k, v in self.CATES_DICT.items():
            m_id = k.split('-')[0]
            m_name = k.split('-')[1]

            if not MysqlConfig.select(m_name, p_id, m_name):
                # n = select_count(p_id) + 1
                MysqlConfig.insert(m_id, m_name, p_id, m_name)
            else:
                m_id = MysqlConfig.select(m_name, p_id, m_name)['menu_id']

            next_name = self.url_name
            if not MysqlConfig.select(next_name, m_id, next_name):
                n = MysqlConfig.select_count(m_id) + 1
                next_id = m_id + "{:03d}".format(n)
                MysqlConfig.insert(next_id, next_name, m_id, next_name)
            else:
                next_id = MysqlConfig.select(next_name, m_id, next_name)['menu_id']

            for code in v:
                for page in range(int(code.split('-')[1])):
                    p_url = 'http://reportapi.eastmoney.com/report/list?'
                    param = {
                        "cb": "datatable1567473",
                        "industryCode": code.split('-')[0],
                        "pageSize": "50",
                        "industry": "*",
                        "rating": "*",
                        "ratingChange": "*",
                        "beginTime": "2018-02-25",
                        "endTime": time.strftime("%Y-%m-%d", time.localtime()),
                        "pageNo": str(page + 1),
                        "fields": "",
                        "qType": "1",
                        "orgCode": "",
                        "rcode": "",
                        "_": str(time.time() * 1000),
                    }

                    url = (p_url + urlencode(param))
                    req = scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'parent_id': next_id})
                    req.headers['Referer'] = 'http://data.eastmoney.com/report/industry.jshtml'
                    yield req

    # 获取详情页面链接
    def parse(self, response):
        base_url = 'http://data.eastmoney.com/report/zw_industry.jshtml?'
        config_info = response.text[17:-1]

        for info in eval(config_info)['data']:
            title = info['title']
            source = info['orgSName']
            issue_time = info['publishDate'][:10]
            author = info['researcher']
            encodeUrl = info['encodeUrl']
            url = base_url + f'encodeUrl={encodeUrl}'
            req = scrapy.Request(url=url, callback=self.parse2, dont_filter=True,
                                 meta={'title': title, 'paper_from': source, 'author': author, 'date': issue_time,
                                       'parent_id': response.meta['parent_id']})
            req.headers['Referer'] = 'http://data.eastmoney.com/report/industry.jshtml'
            yield req

    # 详情页面获取download_url
    def parse2(self, response):
        parent_id = response.meta['parent_id']
        link = response.xpath('//a[@class="pdf-link"]/@href').extract_first()
        item = RepoItem()

        item['paper'] = None
        item['paper_abstract'] = None
        item['title'] = response.meta['title']
        item['paper_url'] = link
        item['date'] = response.meta['date']
        item['author'] = response.meta['author']
        item['paper_from'] = response.meta['paper_from']
        item['cleaning_status'] = 0
        item['paper_type'] = 0
        item['image_url'] = None
        item['categories'] = 48 if parent_id[:4] == '5002' else 50
        item['parent_id'] = parent_id
        item['user_agent'] = response.request.headers['User-Agent']

        if link:
            yield item
            # self.logger.info("title:{}, date: {}".format(item['title'], item['date']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'EastMoney_V1'])
