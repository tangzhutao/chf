# -*- coding: utf-8 -*-
import scrapy, time, os, requests, json, re, hashlib
from Scrapy_D44_repo_V1_01.items import RepoItem
from Scrapy_D44_repo_V1_01.pipelines import MysqlConfig


class WkaskciV1Spider(scrapy.Spider):
    name = 'WkAskci_V1'
    # allowed_domains = ['wk.askci.com/']
    base_url = 'http://wk.askci.com/Search/'
    url_name = '前沿报告库'
    file_id = hashlib.md5(url_name.encode('utf-8')).hexdigest()

    cookie = {
        'LoginKey': '5D55891D41FF4DA5A32C010E478E3F09',
    }

    CATES_DICT = {
        "电力": 10,
        "风电": 2,
        "火电": 1,
        "水电": 1,
        "核电": 1,
        "光伏": 5,
        "热力": 1,
    }

    # 报告列表接口
    def start_requests(self):
        p_id = '4001'
        p_name = '电力、热力生产及供应业'
        MysqlConfig.insert(p_id, p_name, p_id[0], p_name)

        m_id = '4001002'
        m_name = self.url_name
        MysqlConfig.insert(m_id, m_name, p_id, m_name)

        for menu_name, page in self.CATES_DICT.items():
            if not MysqlConfig.select(menu_name, m_id, menu_name):
                n = MysqlConfig.select_count(m_id) + 1
                menu_id = m_id + "{:03d}".format(n)
                MysqlConfig.insert(menu_id, menu_name, m_id, menu_name)
            else:
                menu_id = MysqlConfig.select(menu_name, m_id, menu_name)['menu_id']

            for i in range(page):
                url = f'https://wk.askci.com/ListTable/GetList?keyword=&bookName=&tradeId=&typeId=&tagName={menu_name}&publisher=&page={i}&limit=30'
                yield scrapy.Request(url=url, callback=self.parse, cookies=self.cookie,
                                     meta={'cate': m_name, 'parent_id': menu_id}, dont_filter=True)

    # 获取详情页面链接并返回response
    def parse(self, response):
        parent_id = response.meta['parent_id']
        config_info = json.loads(response.text)['data']
        for info in config_info:
            if not info['BookEditablePrice']:
                title = info['BookName']
                date_time = info['StrBookPublishDate']
                paper_from = info['BookPublisher']
                ReadUrl = info['ReadUrl']
                yield scrapy.Request(url=ReadUrl, callback=self.parse2,
                                     meta={'title': title, 'paper_from': paper_from, 'date_time': date_time,
                                           'parent_id': parent_id})

    # 详情页面获取download_url
    def parse2(self, response):
        Coo = response.headers['Set-Cookie']
        link = re.search(r'wkpdfpath=(.+); domain=', str(Coo)).group(1).replace('%253a', ':').replace('%252f', '/')

        item = RepoItem()
        item['paper_abstract'] = None
        item['title'] = response.meta['title']
        item['paper_url'] = link
        item['date'] = response.meta['date_time']
        item['author'] = None
        item['paper_from'] = response.meta['paper_from']
        item['parent_id'] = response.meta['parent_id']
        item['cleaning_status'] = 0
        item['paper'] = None
        item['user_agent'] = response.request.headers['User-Agent']
        item['image_url'] = None
        item['paper_type'] = 0

        if link[-3:] == 'pdf':
            yield item
            # self.logger.info("title:{}, date: {}".format(item['title'], item['date']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'WkAskci_V1'])
