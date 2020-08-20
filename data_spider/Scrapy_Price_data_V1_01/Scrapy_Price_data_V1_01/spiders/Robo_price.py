# -*- coding: utf-8 -*-
import scrapy, json, re, time
from Scrapy_Price_data_V1_01.items import DataItem
from Scrapy_Price_data_V1_01.pipelines import config, cookie


class Robo01Spider(scrapy.Spider):
    name = 'Robo_price'
    base_url = 'https://robo.datayes.com/'
    url_name = '萝卜投研-价格指数'
    headers = {
        'origin': 'https://robo.datayes.com',
        'referer': 'https://robo.datayes.com/v2/landing/indicator_library',
    }

    # 登录
    def start_requests(self):
        # 登陆网站， https://gw.datayes.com/usermaster/authenticate/web.json
        url = 'https://gw.datayes.com/usermaster/authenticate/web.json'
        data = {
            'username': cookie['usr'],
            'password': cookie['pwd'],
            'rememberMe': 'false'
        }
        yield scrapy.FormRequest(url=url, formdata=data, callback=self.parse, dont_filter=True)
        config.change_state(cookie)

    # 起始网站
    def parse(self, response):
        menu_id = '2002'
        menu_name = '萝卜投研'
        parent_menu_id = '2'
        isRep = '价格指数'
        if not config.select(menu_name, parent_menu_id, isRep):
            config.insert(menu_id, menu_name, parent_menu_id, isRep)

        menu_id = '2002001'
        menu_name = '中国宏观'
        parent_menu_id = '2002'
        isRep = '中国宏观'
        if not config.select(menu_name, parent_menu_id, isRep):
            config.insert(menu_id, menu_name, parent_menu_id, isRep)
        # 70238 中国宏观价格指数
        url = f'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/70238'
        req = scrapy.Request(url=url, callback=self.parse1, dont_filter=True,
                             meta={'link': url, 'parent_id': menu_id}, headers=self.headers)

        yield req

    # 建立下一级目录
    def parse1(self, response):
        base_url = 'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/'
        parent_id = response.meta['parent_id']
        config_info = json.loads(response.text)
        childData = config_info['data']['childData']
        # i = 1
        for child in childData:
            id = child['id']
            indicId = child['indicId']
            nameCn = child['nameCn']
            hasChildren = child['hasChildren']

            a = config.select(nameCn, parent_id, indicId)
            if not a:
                n = config.select_count(parent_id)
                menu_id = parent_id + "{:03d}".format(n)
                config.insert(menu_id, nameCn, parent_id, indicId)
            else:
                menu_id = a['menu_id']

            if hasChildren:
                url = base_url + id
                req = scrapy.Request(url=url, callback=self.parse1, dont_filter=True, meta={'parent_id': menu_id},
                                     headers=self.headers)
                yield req
            else:
                url = f'https://gw.datayes.com/rrp_adventure/web/dataCenter/indic/{indicId}?compare=false'
                req = scrapy.Request(url=url, callback=self.detail, dont_filter=True, meta={'parent_id': menu_id, 'indic_name': nameCn},
                                     headers=self.headers)
                yield req

    def detail(self, response):
        info = json.loads(response.text)['data']
        indic = info['indic']
        data = info['data']

        if info:
            for v in data:
                if indic['frequency'] != '旬':
                    dataValue = v['dataValue']
                    periodDate = v['periodDate']

                    item = DataItem()
                    item['root_id'] = 2
                    item['parent_id'] = response.meta['parent_id']
                    item['indic_name'] = response.meta['indic_name']
                    item['data_year'] = int(periodDate[:4])
                    item['data_month'] = int(periodDate[5:7])
                    item['data_day'] = int(periodDate[-2:])
                    if indic['frequency'] == '年':
                        item['frequency'] = 5
                    elif indic['frequency'] == '月':
                        item['frequency'] = 6
                    elif indic['frequency'] == '周':
                        item['frequency'] = 7
                    else:
                        if item['data_month'] in [1, 2, 3]:
                            item['frequency'] = 1
                        elif item['data_month'] in [4, 5, 6]:
                            item['frequency'] = 2
                        elif item['data_month'] in [7, 8, 9]:
                            item['frequency'] = 3
                        elif item['data_month'] in [10, 11, 12]:
                            item['frequency'] = 4
                    item['unit'] = indic['unit']
                    item['data_source'] = '萝卜投研'
                    item['region'] = indic['region']
                    item['country'] = indic['country']
                    item['create_time'] = periodDate
                    item['data_value'] = float(dataValue)
                    item['sign'] = '19'
                    item['status'] = 1
                    item['cleaning_status'] = 0
                    item['update_time'] = str(int(time.time() * 1000))
                    yield item
                    self.logger.info({'title': item['indic_name'], 'create_time': item['create_time'], 'data_value': item['data_value']})


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Robo_price'])
