# -*- coding: utf-8 -*-
import scrapy
import json
import time
import datetime
from Scrapy_Price_data_V1_01.pipelines import config
from Scrapy_Price_data_V1_01.items import DataItem
from urllib.parse import urlencode


# 爬取地区数据
class Stats01Spider(scrapy.Spider):
    name = 'Stats_02'
    base_url = 'http://data.stats.gov.cn/easyquery.htm'
    url_name = '国家统计局'

    # 全国省份行政代码
    ProvinceCode = ['110000', '120000', '130000', '140000', '150000', '210000', '220000', '230000', '310000', '320000', '330000', '340000', '350000', '360000', '370000', '410000', '420000', '430000', '440000', '450000', '460000', '500000', '510000', '520000', '530000', '540000', '610000', '620000', '630000', '640000', '650000']
    # 36个城市行政代码
    CityCode = ['110000', '120000', '130100', '130200', '130300', '140100', '150100', '150200', '210100', '210200', '210600', '210700', '220100', '220200', '230100', '231000', '310000', '320100', '320200', '320300', '321000', '330100', '330200', '330300', '330700', '340100', '340300', '340800', '350100', '350200', '350500', '360100', '360400', '360700', '370100', '370200', '370600', '370800', '410100', '410300', '410400', '420100', '420500', '420600', '430100', '430600', '430700', '440100', '440200', '440300', '440800', '441300', '450100', '450300', '450500', '460100', '460200', '500000', '510100', '510500', '511300', '520100', '520300', '530100', '532900', '610100', '620100', '630100', '640100', '650100']

    url = 'http://data.stats.gov.cn/easyquery.htm'
    data = {
        '分省年度数据': {
            'id': 'A09',
            'dbcode': 'fsnd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '分省季度数据': {
            'id': 'A05',
            'dbcode': 'fsjd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '分省月度数据': {
            'id': 'A01',
            'dbcode': 'fsyd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
        '主要城市月度价格': {
            'id': 'A01',
            'dbcode': 'csyd',
            'wdcode': 'zb',
            'm': 'getTree',
        },
    }

    def start_requests(self):
        menu_id = '2'
        menu_name = '价格指数'
        parent_menu_id = None
        config.insert(menu_id, menu_name, parent_menu_id, None)

        menu_id = '2001'
        menu_name = '国家统计局'
        parent_menu_id = '2'
        config.insert(menu_id, menu_name, parent_menu_id, None)

        for k, v in self.data.items():
            if not config.select(k, menu_id, v['id']):
                n = config.select_count(menu_id)
                m_id = menu_id + "{:03d}".format(n)
                config.insert(m_id, k, menu_id, v['id'])
            else:
                m_id = config.select(k, menu_id, v['id'])['menu_id']
            req = scrapy.FormRequest(url=self.url, callback=self.parse, dont_filter=True, formdata=v,
                                     meta={'parent_id': m_id, 'dbcode': v['dbcode']})

            req.headers['Referer'] = 'http://data.stats.gov.cn/easyquery.htm?cn=E0102'
            yield req

    def parse(self, response):
        parent_id = response.meta['parent_id']
        get_info = json.loads(response.text)
        print(get_info)
        # for info in get_info:
        #     menu_name = info['name']
        #     isRep = info['id']
        #     if not config.select(menu_name, parent_id, isRep):
        #         n = config.select_count(parent_id)
        #         menu_id = parent_id + "{:03d}".format(n)
        #         config.insert(menu_id, menu_name, parent_id, isRep)
        #     else:
        #         menu_id = config.select(menu_name, parent_id, isRep)['menu_id']
        #
        #     if info['isParent']:
        #         formData = {
        #             'id': info['id'],
        #             'dbcode': response.meta['dbcode'],
        #             'wdcode': 'zb',
        #             'm': 'getTree',
        #         }
        #
        #         req = scrapy.FormRequest(url=self.url, formdata=formData, callback=self.parse, dont_filter=True,
        #                                  meta={'parent_id': menu_id, 'dbcode': response.meta['dbcode']})
        #         req.headers['Referer'] = 'http://data.stats.gov.cn/easyquery.htm'
        #         yield req
        #     else:
        #         keyvalue = {}
        #         if response.meta['dbcode'] == 'csyd':
        #             for code in self.CityCode:
        #                 # 参数填充
        #                 keyvalue['m'] = 'QueryData'
        #                 keyvalue['dbcode'] = response.meta['dbcode']
        #                 keyvalue['rowcode'] = 'zb'
        #                 keyvalue['colcode'] = 'sj'
        #                 keyvalue['wds'] = '[{"wdcode": "reg", "valuecode": "%s"}]' % (code)
        #                 keyvalue['dfwds'] = '[{"wdcode": "zb", "valuecode": "%s"}]' % (isRep)
        #                 keyvalue['k1'] = str(int(round(time.time() * 1000)))
        #                 keyvalue['h'] = '1'
        #                 parameters = urlencode(keyvalue).replace('+', '')
        #                 req = scrapy.FormRequest(url=self.url + '?' + parameters, callback=self.parse2,
        #                                          dont_filter=True,
        #                                          meta={'parent_id': menu_id, 'indic_name': info['name'],
        #                                                'dbcode': response.meta['dbcode']})
        #                 yield req
        #         else:
        #             for code in self.ProvinceCode:
        #                 # 参数填充
        #                 keyvalue['m'] = 'QueryData'
        #                 keyvalue['dbcode'] = response.meta['dbcode']
        #                 keyvalue['rowcode'] = 'zb'
        #                 keyvalue['colcode'] = 'sj'
        #                 keyvalue['wds'] = '[{"wdcode": "reg", "valuecode": "%s"}]' % (code)
        #                 keyvalue['dfwds'] = '[{"wdcode": "zb", "valuecode": "%s"}]' % (isRep)
        #                 keyvalue['k1'] = str(int(round(time.time() * 1000)))
        #                 keyvalue['h'] = '1'
        #                 parameters = urlencode(keyvalue).replace('+', '')
        #                 req = scrapy.FormRequest(url=self.url + '?' + parameters, callback=self.parse2,
        #                                          dont_filter=True, meta={'parent_id': menu_id, 'indic_name': info['name'],
        #                                                                  'dbcode': response.meta['dbcode']})
        #                 yield req

    def parse2(self, response):
        # print(response.text)
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
                sj_valuecode = data['wds'][2]['valuecode']
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
                item['region'] = name_info[1]['nodes'][0]['cname']
                item['country'] = '中国'
                item['data_value'] = float(data['data']['strdata'])
                item['sign'] = '19'
                item['status'] = 1
                item['cleaning_status'] = 0
                item['indic_name'] = indic_name
                item['unit'] = unit
                item['update_time'] = str(int(time.time() * 1000))
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

    cmdline.execute(['scrapy', 'crawl', 'Stats_02'])
