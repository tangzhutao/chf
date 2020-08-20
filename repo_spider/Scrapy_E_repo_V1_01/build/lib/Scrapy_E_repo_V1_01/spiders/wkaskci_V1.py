# -*- coding: utf-8 -*-
import scrapy, time, os, requests, json, re, hashlib
from urllib.parse import urlencode
from Scrapy_E_repo_V1_01.items import RepoItem
from urllib3 import encode_multipart_formdata
from Scrapy_E_repo_V1_01.settings import SPIDER_NAME, UPLOADURL
from Scrapy_E_repo_V1_01.pipelines import MysqlConfig
from Scrapy_E_repo_V1_01.proxy import get_proxy


class WkaskciV1Spider(scrapy.Spider):
    name = 'wkaskci_V1'
    allowed_domains = ['wk.askci.com']
    base_url = 'https://wk.askci.com/'
    url_name = '前沿报告库'
    file_id = hashlib.md5(url_name.encode('utf-8')).hexdigest()

    menu = {
        '5001': '房屋建筑业',
        '5002': '土木工程建筑业',
        '5003': '建筑安装业',
        '5004': '建筑装饰、装修和其他建筑业',
    }
    parent_menu_id = []

    # 报告列表接口
    def start_requests(self):
        for id, name in self.menu.items():
            MysqlConfig.insert(id, name, id[0], name)
            menu_name = "前沿报告库"
            if not MysqlConfig.select(menu_name, id, menu_name):
                n = MysqlConfig.select_count(id) + 1
                menu_id = id + "{:03d}".format(n)
                self.parent_menu_id.append(menu_id)
                MysqlConfig.insert(menu_id, menu_name, id, menu_name)
            else:
                menu_id = MysqlConfig.select(menu_name, id, menu_name)['menu_id']
                self.parent_menu_id.append(menu_id)

        for p in range(10):
            # tradeId=8 表示建筑房产行业， page 表示页数，    limit   表示每一页显示多少内容
            url = f'https://wk.askci.com/ListTable/GetList?keyword=&bookName=&tradeId=8&typeId=&tagName=&publisher=&page={p + 1}&limit=90'
            req = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield req

    # 判断是否在E47
    def isCate(self, cate):
        keys = ['房', '地产', '办公', '物业', '写字楼', '公寓', '酒店', '楼宇']
        for k in keys:
            if k in cate:
                return True

    # 获取详情页面链接并返回response
    def parse(self, response):
        config_list = json.loads(response.text)
        for i in config_list['data']:
            if not i['BookEditablePrice']:
                title = i['BookName']
                cate = i['StrBookTagName'].replace('/', '和').replace(',', '')
                if ',' in cate:
                    cate = cate.split(',')[0]

                date_time = i['StrBookPublishDate']
                paper_from = i['BookPublisher']
                ReadUrl = i['ReadUrl']

                if self.isCate(cate):
                    parent_id = self.parent_menu_id[0]
                    n = MysqlConfig.select_count(parent_id) + 1
                    menu_id = parent_id + "{:03d}".format(n)
                    categories = 47
                elif '工程' in cate:
                    parent_id = self.parent_menu_id[1]
                    n = MysqlConfig.select_count(parent_id) + 1
                    menu_id = parent_id + "{:03d}".format(n)
                    categories = 48
                elif '安装' in cate:
                    parent_id = self.parent_menu_id[2]
                    n = MysqlConfig.select_count(parent_id) + 1
                    menu_id = parent_id + "{:03d}".format(n)
                    categories = 49
                else:
                    parent_id = self.parent_menu_id[3]
                    n = MysqlConfig.select_count(parent_id) + 1
                    menu_id = parent_id + "{:03d}".format(n)
                    categories = 50
                if not MysqlConfig.select(cate, parent_id, cate):
                    MysqlConfig.insert(menu_id, cate, parent_id, cate)
                else:
                    menu_id = MysqlConfig.select(cate, parent_id, cate)['menu_id']

                yield scrapy.Request(url=ReadUrl, callback=self.parse2,
                                     meta={'title': title, 'paper_from': paper_from, 'date_time': date_time,
                                           'p_id': menu_id, 'cate': cate, 'categories': categories})

    # 详情页面获取download_url
    def parse2(self, response):
        user_agent = response.request.headers['User-Agent']
        p_id = response.meta['p_id']
        Coo = response.headers['Set-Cookie']
        link = re.search(r'wkpdfpath=(.+); domain=', str(Coo)).group(1).replace('%253a', ':').replace('%252f', '/')
        item = RepoItem()
        item['paper_abstract'] = None
        item['title'] = response.meta['title']
        item['paper_url'] = link
        item['date'] = response.meta['date_time']
        item['author'] = None
        item['paper_from'] = '前沿报告库'
        item['cleaning_status'] = 0
        item['image_url'] = None
        item['paper_type'] = 0
        item['categories'] = response.meta['categories']
        item['parent_id'] = p_id
        item['user_agent'] = user_agent
        item['paper'] = None

        if link:
            yield item
            # self.logger.info("title:{}, date: {}".format(item['title'], item['date']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'wkaskci_V1'])
