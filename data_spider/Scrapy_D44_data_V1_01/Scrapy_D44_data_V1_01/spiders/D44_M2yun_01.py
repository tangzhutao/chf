# D44_M2yun_01
# -*- coding: utf-8 -*-
import scrapy
import json
import time
import datetime
from Scrapy_D44_data_V1_01.pipelines import mysql_config
from Scrapy_D44_data_V1_01.items import DataItem


class ScrapyRobodata01Spider(scrapy.Spider):
    name = 'D44_M2yun_01'
    base_urls = 'http://data.m2investment.com/'
    url_name = '觅途云'

    cate_id = {
        "互联网行业": "1383",
        "行业固定资产投资和产能": "1382",
        "中国对外贸易指数": "1381",
        "行业财务指标": "1380",
        "电力": "1379",
        "工业产能利用率": "1378",
        "平均工资": "1377",
        "投入产出表": "1376",
        "工业生产者出厂价格指数（PPI）": "1375",
        "工业企业经济效益总指标": "1374",
        "信心指数": "1247",
        "科技活动": "1246",
        "就业": "1245",
        "景气指数": "1244",
        "固定资产投资资金来源": "1243",
        "固定资产投资项目": "1242",
        "工业增加值": "1241",
        "工业企业经济效益指标：分行业": "1240",
        "产品产量和消费量": "1239",
        "固定资产投资完成额：分行业": "497",
    }

    def start_requests(self):
        p_id = '4001010'
        p_name = '觅途云'
        parent_id = '4001'
        isRep = '电力、热力生产和供应业'
        if not mysql_config.select(p_name, parent_id, isRep):
            mysql_config.insert(p_id, p_name, parent_id, isRep)

        for k, v in self.cate_id.items():
            n = mysql_config.select_count(p_id) + 1
            menu_id = p_id + "{:03d}".format(n)

            if not mysql_config.select(k, p_id, v):
                mysql_config.insert(menu_id, k, p_id, v)
            else:
                menu_id = mysql_config.select(k, p_id, v)['menu_id']

            url = f'http://www.gongyeyinxiang.com/bd/relateds?typeId={v}&cateId=12&limit=200'
            req = scrapy.Request(url=url, callback=self.parse, meta={'parent_id': menu_id, 'cate': k}, dont_filter=True)
            yield req

    def parse(self, response):
        config_info = json.loads(response.text)['data']
        parent_id = response.meta['parent_id']
        for info in config_info['list']:
            n = mysql_config.select_count(parent_id) + 1
            menu_id = parent_id + "{:03d}".format(n)
            menu_name = info['name']
            isRep = info['id']
            if not mysql_config.select(menu_name, parent_id, isRep):
                mysql_config.insert(menu_id, menu_name, parent_id, isRep)
            else:
                menu_id = mysql_config.select(menu_name, parent_id, isRep)['menu_id']
                menu_name = mysql_config.select(menu_name, parent_id, isRep)['menu_name']

            url = f'http://www.gongyeyinxiang.com/bd/datas?dataId={isRep}&flag=list'
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True,
                                 meta={'parent_id': menu_id, 'menu_name': menu_name})
            yield req

    def parse_detail(self, response):
        parent_id = response.meta['parent_id']
        menu_name = response.meta['menu_name']
        config_info = json.loads(response.text)['data']['list']
        for info in config_info:
            date = info['date']
            value = info['num']
            year = int(date[:4])
            month = int(date[-2:]) if len(date) == 7 else 12
            create_time = str(self.last_day(datetime.date(year, month, 1)))
            day = int(create_time[-2:])
            frequency = 5 if len(date) == 4 else 6
            item = DataItem()
            item['frequency'] = frequency
            item['indic_name'] = menu_name
            item['parent_id'] = parent_id
            item['root_id'] = parent_id[0]
            item['data_year'] = year
            item['data_month'] = month
            item['data_day'] = day
            item['unit'] = None
            item['data_source'] = '觅途云'
            item['region'] = '全国'
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

    args = "scrapy crawl D44_M2yun_01".split()
    cmdline.execute(args)
