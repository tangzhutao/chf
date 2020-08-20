# -*- coding: utf-8 -*-
import scrapy
import json
import time
import datetime
from Scrapy_D44_data_V1_01.pipelines import mysql_config
from urllib.parse import urlencode
from Scrapy_D44_data_V1_01.items import DataItem


class ScrapyRobodata01Spider(scrapy.Spider):
    name = 'D44_Stats_01'
    base_url = 'http://data.stats.gov.cn/easyquery.htm'
    url_name = '国家统计局'

    # 全国省份行政代码
    ProvinceCode = ['110000', '120000', '130000', '140000', '150000', '210000', '220000', '230000', '310000', '320000',
                    '330000', '340000', '350000', '360000', '370000', '410000', '420000', '430000', '440000', '450000',
                    '460000', '500000', '510000', '520000', '530000', '540000', '610000', '620000', '630000', '640000',
                    '650000']
    # 能源
    data = {
        '年度数据': {
            'id': 'A07',
            'dbcode': 'hgnd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '月度数据': {
            'id': 'A03',
            'dbcode': 'hgyd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '分省月度数据': {
            'id': 'A03',
            'dbcode': 'fsyd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '分省年度数据': {
            'id': 'A07',
            'dbcode': 'fsnd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
    }

    # 从1990年开始爬取
    # COOKIE = {
    #     "JSESSIONID": "2639EF3D2DBB422FB898C5642FDAE577",
    #     "experience": "show",
    #     "u": "1",
    #     "_trs_uv": "kc1qy830_6_13w3",
    # }

    def start_requests(self):
        p_id = '4001009'
        p_name = '国家统计局'
        parent_id = '4001'
        isRep = '能源'
        if not mysql_config.select(p_name, parent_id, isRep):
            mysql_config.insert(p_id, p_name, parent_id, isRep)

        for k, v in self.data.items():
            n = mysql_config.select_count(p_id) + 1
            menu_id = p_id + "{:03d}".format(n)
            isRep = v['id']
            if not mysql_config.select(k, p_id, isRep):
                mysql_config.insert(menu_id, k, p_id, isRep)
            else:
                menu_id = mysql_config.select(k, p_id, isRep)['menu_id']

            req = scrapy.FormRequest(url=self.base_url, callback=self.parse, dont_filter=True, formdata=v,
                                     meta={'parent_menu_id': menu_id})
            req.headers['Referer'] = 'http://data.stats.gov.cn/easyquery.htm?cn=C01'
            yield req

    # 返回目录 json
    def parse(self, response):
        parent_id = response.meta['parent_menu_id']
        get_info = json.loads(response.text)
        for info in get_info:
            n = mysql_config.select_count(parent_id) + 1
            menu_id = parent_id + "{:03d}".format(n)
            menu_name = info['name']
            isRep = info['id']

            if not mysql_config.select(menu_name, parent_id, isRep):
                mysql_config.insert(menu_id, menu_name, parent_id, isRep)
            else:
                menu_id = mysql_config.select(menu_name, parent_id, isRep)['menu_id']

            if info['isParent']:

                data = {
                    'id': info['id'],
                    'dbcode': info['dbcode'],
                    'wdcode': 'zb',
                    'm': 'getTree',
                }
                req = scrapy.FormRequest(url=self.base_url, callback=self.parse, dont_filter=True, formdata=data,
                                         meta={'parent_menu_id': menu_id})
                req.headers['Referer'] = 'http://data.stats.gov.cn/easyquery.htm?cn=C01'
                yield req
            else:
                keyvalue = {}
                # 参数填充
                if info['dbcode'] in ['fsyd', 'fsnd']:
                    for code in self.ProvinceCode:
                        keyvalue['m'] = 'QueryData'
                        keyvalue['dbcode'] = info['dbcode']
                        keyvalue['rowcode'] = 'zb'
                        keyvalue['colcode'] = 'sj'
                        keyvalue['wds'] = '[{"wdcode": "reg", "valuecode": "%s"}]' % (code)
                        keyvalue['dfwds'] = '[{"wdcode": "zb", "valuecode": "%s"}]' % (info['id'])
                        keyvalue['k1'] = str(int(round(time.time() * 1000)))
                        keyvalue['h'] = '1'
                        param = urlencode(keyvalue).replace('+', '')
                        req = scrapy.Request(url=self.base_url + '?' + param, callback=self.data_parse,
                                             dont_filter=True,
                                             meta={'parent_id': menu_id})
                        yield req
                else:
                    keyvalue['m'] = 'QueryData'
                    keyvalue['dbcode'] = info['dbcode']
                    keyvalue['rowcode'] = 'zb'
                    keyvalue['colcode'] = 'sj'
                    keyvalue['wds'] = '[]'
                    keyvalue['dfwds'] = '[{"wdcode": "zb", "valuecode": "%s"}]' % (info['id'])
                    keyvalue['k1'] = str(int(round(time.time() * 1000)))
                    keyvalue['h'] = '1'
                    param = urlencode(keyvalue).replace('+', '')
                    req = scrapy.Request(url=self.base_url + '?' + param, callback=self.data_parse, dont_filter=True,
                                         meta={'parent_id': menu_id})
                    yield req

    def data_parse(self, response):
        parent_id = response.meta['parent_id']
        datanodes = json.loads(response.text)['returndata']['datanodes']
        wdnodes = json.loads(response.text)['returndata']['wdnodes']
        menu = {}
        for node in wdnodes[0]['nodes']:
            menu[node['code']] = node

        region = wdnodes[1]['nodes'][0]['name'] if wdnodes[1]['wdcode'] == 'reg' else None

        for data in datanodes:
            if data['data']['hasdata']:
                data_info = data['data']
                value = data_info['strdata']

                date = data['code'].split('.')[-1]
                if len(date) == 4:
                    year = int(date)
                    month = 12
                    day = 31
                    create_time = str(self.last_day(datetime.date(year, month, 1)))
                    frequency = 5
                else:
                    year = int(date[:4])
                    month = int(date[-2:])
                    create_time = str(self.last_day(datetime.date(year, month, 1)))
                    day = int(create_time[-2:])
                    frequency = 6

                wds = data['wds']
                name_valuecode = wds[0]['valuecode']
                n = mysql_config.select_count(parent_id) + 1
                menu_id = parent_id + "{:03d}".format(n)
                menu_name = region + ":" + menu[name_valuecode]['name'] if region else menu[name_valuecode]['name']

                if not mysql_config.select(menu_name, parent_id, name_valuecode):
                    mysql_config.insert(menu_id, menu_name, parent_id, name_valuecode)
                else:
                    menu_id = mysql_config.select(menu_name, parent_id, name_valuecode)['menu_id']

                unit = menu[name_valuecode]['unit']

                item = DataItem()
                item['frequency'] = frequency
                item['indic_name'] = menu_name
                item['parent_id'] = menu_id
                item['root_id'] = menu_id[0]
                item['data_year'] = year
                item['data_month'] = month
                item['data_day'] = day
                item['unit'] = unit
                item['data_source'] = '国家统计局'
                item['region'] = region if region else "全国"
                item['country'] = '中国'
                item['create_time'] = create_time
                item['update_time'] = str(int(time.time() * 1000))
                item['data_value'] = float(value)
                item['sign'] = '19'
                item['status'] = 1
                item['cleaning_status'] = 0
                # print(item)
                yield item
                self.logger.info({'title': menu_name, 'create_time': create_time, 'data_value': value})

    # 通过年份和月份获取当前月份的最后一天
    def last_day(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)


if __name__ == '__main__':
    from scrapy import cmdline

    args = "scrapy crawl D44_Stats_01".split()
    cmdline.execute(args)
