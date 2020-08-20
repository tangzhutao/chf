# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DataItem(scrapy.Item):
    # 1.根目录id(int类型)	1-999
    root_id = scrapy.Field()
    # 2.上一类	(int类型)	1-999 + 001-999 + 001-999
    parent_id = scrapy.Field()
    # 3.名称(str)
    indic_name = scrapy.Field()
    # 4.年：1992(int类型)
    data_year = scrapy.Field()
    # 5.月：1-12(int类型)
    data_month = scrapy.Field()
    # 6.日：1-31(int类型)
    data_day = scrapy.Field()
    # 7.频率(1234 季度 ，5678：年月周日  )(int类型)
    frequency = scrapy.Field()
    # 8.单位(str)
    unit = scrapy.Field()
    # 9.数据来源(网站名)(str)
    data_source = scrapy.Field()
    # 10.全国、省份、市等地区(str)
    region = scrapy.Field()
    # 11.国家(str)
    country = scrapy.Field()
    # 12.数据产生时间(datetime类型)
    create_time = scrapy.Field()
    # 13.数值(double)
    data_value = scrapy.Field()
    # 14.个人编号(str)
    sign = scrapy.Field()
    # 15.0:无效  1: 有效(int类型)
    status = scrapy.Field()
    # 16.0 : 未清洗  1 ： 清洗过(int类型)
    cleaning_status = scrapy.Field()
    
    update_time = scrapy.Field()
