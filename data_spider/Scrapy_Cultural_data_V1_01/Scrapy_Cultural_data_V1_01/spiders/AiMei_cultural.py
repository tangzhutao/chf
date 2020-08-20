import scrapy
import json
import time
from Scrapy_Cultural_data_V1_01.pipelines import config
from Scrapy_Cultural_data_V1_01.items import DataItem


class AimeiSpider(scrapy.Spider):
    name = 'AiMei_cultural'

    # base_url = 'https://data.iimedia.cn/front/childList'
    base_url = 'https://data.iimedia.cn/'
    url_name = '艾煤数据库'

    # json数据接口, post请求
    def start_requests(self):
        menu_id = '4'
        menu_name = '文化资源'
        parent_menu_id = None
        isRep = None
        if not config.select(menu_name, parent_menu_id, isRep):
            config.insert(menu_id, menu_name, parent_menu_id, isRep)

        menu_id = '4002'
        menu_name = '艾煤数据库'
        parent_menu_id = '4'
        isRep = '文化'
        if not config.select(menu_name, parent_menu_id, isRep):
            config.insert(menu_id, menu_name, parent_menu_id, isRep)

        data = {
            'key': isRep,
            'sourceType': '1',
            'nodeIdOfRoot': '0',
            'returnType': '0',
        }
        req = scrapy.FormRequest(url='https://data.iimedia.cn/front/search', formdata=data, callback=self.parse1,
                                 dont_filter=True, meta={'cate': isRep, 'parent_id': menu_id, 'data': data})
        req.headers["referer"] = "https://data.iimedia.cn"
        yield req

    # 建立二级目录
    def parse1(self, response):
        config_info = json.loads(response.text)['data']['index']
        for info in config_info:
            n = config.select_count(response.meta['parent_id']) + 1
            parent_menu_id = response.meta['parent_id']
            name = info['name']
            child = info['child']  # 判断是否还有子数据，若为空，则没有子数据
            menu_id = parent_menu_id + "{:03d}".format(n)
            menu_name = name
            if not config.select(menu_name, parent_menu_id, info['id']):
                config.insert(menu_id, menu_name, parent_menu_id, info['id'])
            else:
                menu_id = config.select(menu_name, parent_menu_id, info['id'])['menu_id']
            if child:
                yield from self.rec(menu_id, child)

    # 解析数据结构
    def rec(self, parent_menu_id, info):
        for data in info:
            n = config.select_count(parent_menu_id) + 1
            menu_name = data['name']
            menu_id = parent_menu_id + "{:03d}".format(n)
            if not config.select(menu_name, parent_menu_id, data['id']):
                config.insert(menu_id, menu_name, parent_menu_id, data['id'])
            else:
                menu_id = config.select(menu_name, parent_menu_id, data['id'])['menu_id']

            if data['child']:
                yield from self.rec(menu_id, data['child'])

            else:
                for Ids in data['childIds']:
                    data = {
                        'node_id': str(Ids)
                    }
                    yield scrapy.FormRequest(url='https://data.iimedia.cn/front/getObjInfoByNodeId',
                                             callback=self.parse_detail, dont_filter=True,
                                             formdata=data, meta={'data': data, 'parent_id': menu_id})

    # 返回详细数据, 并储存
    def parse_detail(self, response):
        self.logger.info({'data': response.meta['data']})
        get_info = json.loads(response.text)['data']
        if get_info:
            objValue = get_info['objValue']
            nodeInfo = get_info['nodeInfo']
            objInfo = get_info['objInfo']

            parent_menu_id = response.meta['parent_id']
            n = config.select_count(parent_menu_id) + 1
            menu_id = parent_menu_id + "{:03d}".format(n)
            menu_name = nodeInfo['name']
            isRep = nodeInfo['nodeId']
            if not config.select(menu_name, parent_menu_id, isRep):
                config.insert(menu_id, menu_name, parent_menu_id, isRep)
            else:
                menu_id = config.select(menu_name, parent_menu_id, isRep)['menu_id']

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
                    item['frequency'] = 6
                elif frequency == '周':
                    item['frequency'] = 7
                elif frequency == '天':
                    item['frequency'] = 8
                else:
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
                yield item
                self.logger.info({'title': menu_name, 'create_time': date, 'data_value': value})


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute("scrapy crawl AiMei_cultural".split())
