# -*- coding: utf-8 -*-
import scrapy, json, os, re
import scrapy
import json
import time
from Scrapy_Cultural_data_V1_01.pipelines import config
from Scrapy_Cultural_data_V1_01.items import DataItem


class EQianzhan01Spider(scrapy.Spider):
    name = 'Qianzhan_cultural'
    base_url = 'https://d.qianzhan.com'
    url_name = '前瞻数据库'

    # 2 文化资源
    cate = {
        '中国宏观-151': 'https://d.qianzhan.com/xdata/xsearch?q=%e6%96%87%e5%8c%96&cls=01&page=',
        '行业经济-75': 'https://d.qianzhan.com/xdata/xsearch?q=%e6%96%87%e5%8c%96&cls=02&page=',
        '区域宏观-69': 'https://d.qianzhan.com/xdata/xsearch?q=%e6%96%87%e5%8c%96&cls=04&page=',
    }

    def start_requests(self):
        p_id = '4'
        m_id = '4004'
        p_name = '前瞻数据库'
        p_isRep = '前瞻数据库'
        config.insert(m_id, p_name, p_id, p_isRep)

        for k, u in self.cate.items():
            keys = k.split('-')
            n = config.select_count(m_id) + 1
            menu_id = m_id + "{:03d}".format(n)
            menu_name = keys[0]
            isRep = keys[0]
            if not config.select(menu_name, m_id, isRep):
                config.insert(menu_id, menu_name, m_id, isRep)
            else:
                menu_id = config.select(menu_name, m_id, isRep)['menu_id']

            for i in range(int(keys[1])):
                url = u + str(i + 1)
                req = scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'parent_id': menu_id})
                yield req

    def parse(self, response):
        parent_id = response.meta['parent_id']
        config_list = response.xpath('//div[@class="search-result_con search-result_con2"]/table/tbody/tr')
        for i in range(1, len(config_list)):
            title = config_list[i].xpath('./td[1]//text()').extract()
            title = ''.join(title)
            menu = title.split(':')
            unit = config_list[i].xpath('./td[2]/text()').extract_first()
            url = self.base_url + config_list[i].xpath('./td[1]/a/@href').extract_first()
            yield from self.save_menu(menu, parent_id, url, unit)

    def save_menu(self, menu, parent_id, url, unit):
        menu_name = menu.pop(0)
        isRep = menu_name
        if not config.select(menu_name, parent_id, isRep):
            n = config.select_count(parent_id) + 1
            menu_id = parent_id + "{:03d}".format(n)
            config.insert(menu_id, menu_name, parent_id, isRep)
        else:
            menu_id = config.select(menu_name, parent_id, isRep)['menu_id']
        if menu:
            yield from self.save_menu(menu, menu_id, url, unit)
        else:
            req = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True, meta={'parent_id': menu_id, 'menu_name': menu_name, 'unit': unit})
            yield req

    def parse_detail(self, response):
        parent_id = response.meta['parent_id']
        menu_name = response.meta['menu_name']
        unit = response.meta['unit']
        config_list = response.xpath('//table[@class="search-result_table"]/tbody/tr')

        for i in range(2, len(config_list)):
            value = config_list[i].xpath('./td[3]/text()').extract_first()
            issue_time = config_list[i].xpath('./td[@class="f_blue3"]/text()').extract_first().replace('.', '-')
            if value:
                fre = re.search(r'\((.+)\)', menu_name).group(1)
                if fre == '年':
                    frequency = 5
                    year = issue_time
                    month = 12
                    day = 31
                elif fre == '季度':
                    if issue_time[-2:] == '03':
                        frequency = 1
                    elif issue_time[-2:] == '06':
                        frequency = 2
                    elif issue_time[-2:] == '09':
                        frequency = 3
                    else:
                        frequency = 4
                    year = issue_time[:4]
                    month = issue_time[-2:]
                    day = 31
                elif fre == '周':
                    frequency = 7
                    year = issue_time[:4]
                    month = issue_time[5:7]
                    day = issue_time[-2:]
                elif fre == '日':
                    frequency = 8
                    year = issue_time[:4]
                    month = issue_time[5:7]
                    day = issue_time[-2:]
                else:
                    frequency = 6
                    year = issue_time[:4]
                    month = issue_time[-2:]
                    day = 31
                item = DataItem()
                item['frequency'] = frequency
                item['indic_name'] = menu_name
                item['parent_id'] = parent_id
                item['root_id'] = parent_id[0]
                item['data_year'] = year
                item['data_month'] = month
                item['data_day'] = day
                item['unit'] = unit
                item['data_source'] = '前瞻数据库'
                item['region'] = None
                item['country'] = '中国'
                item['create_time'] = f'{year}-{month}-{day}'
                item['update_time'] = str(int(time.time() * 1000))
                item['data_value'] = float(value)
                item['sign'] = '19'
                item['status'] = 1
                item['cleaning_status'] = 0
                yield item
                self.logger.info({'title': menu_name, 'create_time': item['create_time'], 'data_value': value})


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'Qianzhan_cultural'])
