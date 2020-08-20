# -*- coding: utf-8 -*-
import scrapy
import json
import time
import datetime
from Scrapy_Price_data_V1_01.pipelines import config
from Scrapy_Price_data_V1_01.items import DataItem
from urllib.parse import urlencode


# 爬取全国月度、季度、年度数据
class Stats01Spider(scrapy.Spider):
    name = 'Stats_01'
    base_url = 'http://data.stats.gov.cn/easyquery.htm'
    url_name = '国家统计局'

    url = 'http://data.stats.gov.cn/easyquery.htm'
    data = {
        '年度数据': {
            'id': 'A09',
            'dbcode': 'hgnd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '季度数据': {
            'id': 'A06',
            'dbcode': 'hgjd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '月度数据': {
            'id': 'A01',
            'dbcode': 'hgyd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
    }

    def start_requests(self):
        menu_id = "2"
        menu_name = "价格指数"
        parent_menu_id = None
        config.insert(menu_id, menu_name, parent_menu_id, None)

        menu_id = '2001'
        menu_name = '国家统计局'
        parent_menu_id = '2'
        config.insert(menu_id, menu_name, parent_menu_id, '0')

        for k, v in self.data.items():
            if not config.select(k,menu_id, v['id']):
                n = config.select_count(menu_id)
                m_id = menu_id + "{:03d}".format(n)
                config.insert(m_id, k, menu_id, v['id'])
            else:
                m_id = config.select(k, menu_id, v['id'])['menu_id']
            req = scrapy.FormRequest(url=self.url, callback=self.parse, dont_filter=True, formdata=v,
                                     meta={'parent_id': m_id, 'dbcode': v['dbcode']})

            req.headers['Referer'] = 'http://data.stats.gov.cn/easyquery.htm?cn=C01'

            yield req

    def parse(self, response):
        parent_id = response.meta['parent_id']
        get_info = json.loads(response.text)
        for info in get_info:
            menu_name = info['name']
            isRep = info['id']
            if not config.select(menu_name, parent_id, isRep):
                n = config.select_count(parent_id)
                menu_id = parent_id + "{:03d}".format(n)
                config.insert(menu_id, menu_name, parent_id, isRep)
            else:
                menu_id = config.select(menu_name, parent_id, isRep)['menu_id']

            if info['isParent']:
                formData = {
                    'id': info['id'],
                    'dbcode': response.meta['dbcode'],
                    'wdcode': 'zb',
                    'm': 'getTree',
                }

                req = scrapy.FormRequest(url=self.url, formdata=formData, callback=self.parse, dont_filter=True,
                                         meta={'parent_id': menu_id, 'dbcode': response.meta['dbcode']})
                req.headers['Referer'] = 'http://data.stats.gov.cn/easyquery.htm'
                yield req
            else:
                keyvalue = {}
                # 参数填充
                keyvalue['m'] = 'QueryData'
                keyvalue['dbcode'] = response.meta['dbcode']
                keyvalue['rowcode'] = 'zb'
                keyvalue['colcode'] = 'sj'
                keyvalue['wds'] = '[]'
                keyvalue['dfwds'] = '[{"wdcode": "zb", "valuecode": "%s"}]' % (isRep)
                keyvalue['k1'] = str(int(round(time.time() * 1000)))
                keyvalue['h'] = '1'
                param = urlencode(keyvalue).replace('+', '')
                req = scrapy.FormRequest(url=self.url + '?' + param, callback=self.parse2,
                                         dont_filter=True, meta={'parent_id': menu_id, 'indic_name': info['name'],
                                                                 'dbcode': response.meta['dbcode']})

                yield req

    # 
    def parse2(self, response):
        data_info = json.loads(response.text)['returndata']['datanodes']
        name_info = json.loads(response.text)['returndata']['wdnodes']
        parent_id = response.meta['parent_id']
        for data in data_info:
            if data['data']['hasdata']:
                code = data['wds'][0]['valuecode']
                for de in name_info[0]['nodes']:
                    if code == de['code']:
                        indic_name = de['name']
                        unit = de['unit']

                item = DataItem()
                item['root_id'] = 2
                sj_valuecode = data['wds'][1]['valuecode']
                if len(sj_valuecode) == 4:
                    item['data_year'] = int(sj_valuecode)
                    item['data_month'] = 12
                    create_time = str(self.last_day(datetime.date(item['data_year'], item['data_month'], 1)))
                    item['data_day'] = int(create_time[-2:])
                    item['create_time'] = create_time
                    item['frequency'] = 5

                elif len(sj_valuecode) == 5:
                    item['data_year'] = int(sj_valuecode[:4])
                    if 'A' in sj_valuecode:
                        item['data_month'] = 3
                        item['frequency'] = 1
                    elif 'B' in sj_valuecode:
                        item['data_month'] = 6
                        item['frequency'] = 2
                    elif 'C' in sj_valuecode:
                        item['data_month'] = 9
                        item['frequency'] = 3
                    elif 'D' in sj_valuecode:
                        item['data_month'] = 12
                        item['frequency'] = 4
                    create_time = str(self.last_day(datetime.date(item['data_year'], item['data_month'], 1)))
                    item['data_day'] = int(create_time[-2:])
                    item['create_time'] = create_time
                elif len(sj_valuecode) == 6:
                    item['data_year'] = int(sj_valuecode[:4])
                    item['data_month'] = int(sj_valuecode[-2:])
                    create_time = str(self.last_day(datetime.date(item['data_year'], item['data_month'], 1)))
                    item['data_day'] = int(create_time[-2:])
                    item['create_time'] = create_time
                    item['frequency'] = 6

                item['data_source'] = '国家统计局'
                item['region'] = '全国'
                item['country'] = '中国'
                item['data_value'] = float(data['data']['strdata'])
                item['sign'] = '19'
                item['status'] = 1
                item['cleaning_status'] = 0
                item['update_time'] = str(int(time.time() * 1000))
                item['indic_name'] = indic_name
                item['unit'] = unit
                menu_name = indic_name
                isRep = code
                if not config.select(menu_name, parent_id, isRep):
                    n = config.select_count(parent_id)
                    menu_id = parent_id + "{:03d}".format(n)
                    item['parent_id'] = int(menu_id)
                    config.insert(menu_id, menu_name, parent_id, isRep)
                else:
                    menu_id = config.select(menu_name, parent_id, isRep)['menu_id']
                    item['parent_id'] = int(menu_id)
                yield item
                self.logger.info(
                    {'title': item['indic_name'], 'create_time': item['create_time'], 'data_value': item['data_value']})

    # 通过年份和月份获取当前月份的最后一天
    def last_day(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Stats_01'])
