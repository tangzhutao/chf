import scrapy
import json
import time
from Scrapy_E_Data_V1_01.pipelines import mysql_config
from Scrapy_E_Data_V1_01.items import DataItem
from Scrapy_E_Data_V1_01.settings import root_id


class D44Aimei01Spider(scrapy.Spider):
    name = 'E_AiMei_02'
    b_url = 'https://data.iimedia.cn/front/childList'
    base_url = 'https://data.iimedia.cn/'
    url_name = '艾煤数据中心_02'

    # 爬取类目
    catelog = {
        '71164': '5004001001-家具建材',
        '30332955': '5004005001-建筑与房地产',
    }

    # json数据接口, post请求
    def start_requests(self):
        # 搜索结果json
        for k, v in self.catelog.items():
            cate = v.split('-')

            menu_id = cate[0]
            menu_name = cate[1]
            parent_menu_id = cate[0][:-3]
            isRep = k
            if not mysql_config.select(menu_name, parent_menu_id, isRep):
                mysql_config.insert(menu_id, menu_name, parent_menu_id, isRep)
            else:
                menu_id = mysql_config.select(menu_name, parent_menu_id, isRep)['menu_id']

            data = {
                'pid': k,
            }
            req = scrapy.FormRequest(url=self.b_url, formdata=data, callback=self.parse,
                                     dont_filter=True, meta={'parent_id': menu_id})
            req.headers["referer"] = "https://data.iimedia.cn"

            yield req

    # 建立二级目录
    def parse(self, response):
        parent_id = response.meta['parent_id']
        config_info = json.loads(response.text)['data']
        for info in config_info:
            n = mysql_config.select_count(parent_id) + 1
            menu_id = parent_id + "{:03d}".format(n)
            menu_name = info['name']

            if not mysql_config.select(menu_name, parent_id, info['id']):
                mysql_config.insert(menu_id, menu_name, parent_id, info['id'])
            else:
                menu_id = mysql_config.select(menu_name, parent_id, info['id'])['menu_id']
            if info['is_end']:
                data = {
                    'node_id': info['id']
                }
                yield scrapy.FormRequest(url='https://data.iimedia.cn/front/getObjInfoByNodeId',
                                         callback=self.parse_detail, dont_filter=True,
                                         formdata=data, meta={'parent_id': menu_id, 'data': data})

            else:
                data = {
                    'pid': info['id'],
                }
                req = scrapy.FormRequest(url=self.b_url, callback=self.parse, dont_filter=True, formdata=data,
                                         meta={'parent_id': menu_id})
                yield req

    # 返回详细数据, 并储存
    def parse_detail(self, response):
        self.logger.info({'data': response.meta['data']})
        get_info = json.loads(response.text)['data']
        if get_info:
            objValue = get_info['objValue']
            nodeInfo = get_info['nodeInfo']
            objInfo = get_info['objInfo']

            parent_menu_id = response.meta['parent_id']
            n = mysql_config.select_count(parent_menu_id) + 1
            menu_id = parent_menu_id + "{:03d}".format(n)
            menu_name = nodeInfo['name']
            isRep = nodeInfo['nodeId']
            if not mysql_config.select(menu_name, parent_menu_id, isRep):
                mysql_config.insert(menu_id, menu_name, parent_menu_id, isRep)
            else:
                menu_id = mysql_config.select(menu_name, parent_menu_id, isRep)['menu_id']

            for info in objValue['form']:
                item = DataItem()
                value = info[1]
                date = info[0]
                year = int(date[:4])
                month = int(date[5:7])
                day = int(date[-2:])
                frequency = objInfo["frequenceName"]
                if frequency == '年':
                    # 频率
                    item['frequency'] = 5
                elif frequency == '季度':
                    if month in [1, 2, 3]:
                        item['frequency'] = 1
                    elif month in [4, 5, 6]:
                        item['frequency'] = 2
                    elif month in [7, 8, 9]:
                        item['frequency'] = 3
                    elif month in [10, 11, 12]:
                        item['frequency'] = 4
                elif frequency == '月':
                    # 频率
                    item['frequency'] = 6
                elif frequency == '周':
                    # 频率
                    item['frequency'] = 7
                elif frequency == '天':
                    # 频率
                    item['frequency'] = 8
                else:
                    # 频率
                    item['frequency'] = 0

                item['region'] = None
                item['country'] = None
                item['indic_name'] = menu_name
                item['parent_id'] = menu_id
                item['root_id'] = menu_id[0]
                item['data_year'] = year
                item['data_month'] = month
                item['data_day'] = day
                item['unit'] = objInfo['unit']
                item['data_source'] = '艾煤数据中心'
                item['create_time'] = date
                item['update_time'] = str(int(time.time() * 1000))
                item['data_value'] = float(value)
                item['sign'] = '19'
                item['status'] = 1
                item['cleaning_status'] = 0
                # print(item)
                yield item
                self.logger.info({'title': menu_name, 'create_time': date, 'data_value': value})


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute("scrapy crawl E_AiMei_02".split())
