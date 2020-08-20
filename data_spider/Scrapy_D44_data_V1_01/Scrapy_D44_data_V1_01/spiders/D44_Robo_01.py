# -*- coding: utf-8 -*-
import scrapy, json, os, re
import scrapy
import json
import time
from Scrapy_D44_data_V1_01.pipelines import mysql_config, cookie
from Scrapy_D44_data_V1_01.items import DataItem
from Scrapy_D44_data_V1_01.settings import root_id


class ScrapyRobodata01Spider(scrapy.Spider):
    name = 'D44_Robo_01'
    base_urls = 'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/'
    base_url = 'https://robo.datayes.com/'
    url_name = '萝卜投研'

    # 登陆
    def start_requests(self):
        url = 'https://gw.datayes.com/usermaster/authenticate/web.json'
        data = {
            # ly
            'username': cookie['usr'],
            'password': cookie['pwd'],
            'rememberMe': 'false'
        }
        yield scrapy.FormRequest(url=url, formdata=data, callback=self.parse_data, dont_filter=True)
        self.logger.info({'登录账号：': cookie['phonenumber']})
        mysql_config.change_state(cookie)

    # 根据关键字查找数据目录
    def parse_data(self, response):
        code = json.loads(response.text)['content']['result']
        if code == 'SUCCESS':
            self.logger.info('登录成功！')
        else:
            self.logger.info('登录失败！')
            return
        for k, v in root_id.items():
            menu_id = v
            menu_name = k
            parent_menu_id = '4001'
            isRep = k
            if not mysql_config.select(menu_name, parent_menu_id, isRep):
                mysql_config.insert(menu_id, menu_name, parent_menu_id, isRep)
            else:
                menu_id = mysql_config.select(menu_name, parent_menu_id, isRep)['menu_id']

            url = f'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/query?input={k}'
            req = scrapy.Request(url=url, callback=self.parse1, dont_filter=True,
                                 meta={'parent_id': menu_id, 'sourcekey': k})
            req.headers['referer'] = "https://robo.datayes.com"
            yield req

    # 返回目录 json
    def parse1(self, response):
        sourcekey = response.meta['sourcekey']
        parent_id = response.meta['parent_id']
        config_info = json.loads(response.text)['data']['catelog']
        if config_info:
            for info in config_info:
                nameCn = info['nameCn']
                hasChildren = info['hasChildren']
                n = mysql_config.select_count(parent_id) + 1
                menu_id = parent_id + "{:03d}".format(n)
                menu_name = nameCn
                isRep = info['indicId']

                if not mysql_config.select(menu_name, parent_id, isRep):
                    mysql_config.insert(menu_id, menu_name, parent_id, isRep)
                else:
                    menu_id = mysql_config.select(menu_name, parent_id, isRep)['menu_id']
                yield from self.rec(info['childData'], nameCn, sourcekey, menu_id)

    # 解析目录
    def rec(self, data, catelog, sourcekey, parent_id):
        for i in data:
            n = mysql_config.select_count(parent_id) + 1
            menu_name = i['nameCn']
            menu_id = parent_id + "{:03d}".format(n)
            if not mysql_config.select(menu_name, parent_id, i['indicId']):
                mysql_config.insert(menu_id, menu_name, parent_id, i['indicId'])
            else:
                menu_id = mysql_config.select(menu_name, parent_id, i['indicId'])['menu_id']

            if i['hasChildren']:
                yield from self.rec(i['childData'], catelog, sourcekey, menu_id)
            else:
                for j in data:
                    menu_name = j['nameCn']
                    routeNames = j['routeNames']
                    indicId = j['indicId']
                    n = mysql_config.select_count(parent_id) + 1
                    menu_id = parent_id + "{:03d}".format(n)
                    if not mysql_config.select(menu_name, parent_id, indicId):
                        mysql_config.insert(menu_id, menu_name, parent_id, indicId)
                    else:
                        menu_id = mysql_config.select(menu_name, parent_id, indicId)['menu_id']

                    url = f'https://gw.datayes.com/rrp_adventure/web/supervisor/macro/query?input={sourcekey}&macro={catelog}&catelog={routeNames}&pageIndex=1&pageSize=1000&highlight=true'
                    req = scrapy.Request(url=url, callback=self.parse2, dont_filter=True, meta={'parent_id': menu_id})
                    req.headers['referer'] = "https://robo.datayes.com"
                    yield req

    # 返回最后一级的数据Json, 并根据 indicId 发送请求
    def parse2(self, response):
        config_info = json.loads(response.text)['data']
        if config_info:
            for info in config_info['hits']:
                indicId = info['indicId']
                url = f'https://gw.datayes.com/rrp_adventure/web/dataCenter/indic/{indicId}?compare=false'
                req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True,
                                     meta={'parent_id': response.meta['parent_id']})
                req.headers['referer'] = "https://robo.datayes.com"
                yield req

    # 返回详细数据, 并储存
    def parse_detail(self, response):
        parent_id = response.meta['parent_id']
        config_info = json.loads(response.text)['data']
        if config_info:
            indic = config_info['indic']
            data = config_info['data']
            n = mysql_config.select_count(parent_id) + 1
            menu_id = parent_id + "{:03d}".format(n)
            menu_name = indic['indicName']
            isRep = indic['indicID']
            if not mysql_config.select(menu_name, parent_id, isRep):
                mysql_config.insert(menu_id, menu_name, parent_id, isRep)
            else:
                menu_id = mysql_config.select(menu_name, parent_id, isRep)['menu_id']
            for info in data:
                item = DataItem()
                value = info['dataValue']
                create_time = info['periodDate']
                year = int(create_time[:4])
                month = int(create_time[5:7])
                day = int(create_time[-2:])
                try:
                    frequency = indic['frequency']
                except Exception as e:
                    print(e)
                    frequency = None
                if frequency == '年':
                    item['frequency'] = 5
                elif frequency == '季':
                    if month in [1, 2, 3]:
                        item['frequency'] = 1
                    elif month in [4, 5, 6]:
                        item['frequency'] = 2
                    elif month in [7, 8, 9]:
                        item['frequency'] = 3
                    elif month in [10, 11, 12]:
                        item['frequency'] = 4
                elif frequency == '月':
                    item['frequency'] = 6
                elif frequency == '周':
                    item['frequency'] = 7

                elif frequency == '日':
                    item['frequency'] = 8
                else:
                    item['frequency'] = 0
                item['indic_name'] = menu_name
                item['parent_id'] = menu_id
                item['root_id'] = menu_id[0]
                item['data_year'] = year
                item['data_month'] = month
                item['data_day'] = day
                item['unit'] = indic['unit']
                item['data_source'] = '萝卜投研'
                item['region'] = indic['region']
                item['country'] = indic['country']
                item['create_time'] = create_time
                item['update_time'] = str(int(time.time() * 1000))
                item['data_value'] = float(value)
                item['sign'] = '19'
                item['status'] = 1
                item['cleaning_status'] = 0
                yield item
                self.logger.info({'title': menu_name, 'create_time': create_time, 'data_value': value})


if __name__ == '__main__':
    from scrapy import cmdline

    args = "scrapy crawl D44_Robo_01".split()
    cmdline.execute(args)

