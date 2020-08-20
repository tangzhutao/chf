# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 名称1
    indic_name = scrapy.Field()
    # 数据目录2
    parent_id = scrapy.Field()
    # 根目录id3
    root_id = scrapy.Field()
    # 年4
    data_year = scrapy.Field()
    # 月5
    data_month = scrapy.Field()
    # 日6
    data_day = scrapy.Field()
    # 频率7
    frequency = scrapy.Field()
    # 单位8
    unit = scrapy.Field()
    # 数据来源(网站名)9
    data_source = scrapy.Field()
    # 地区10
    region = scrapy.Field()
    # 国家11
    country = scrapy.Field()
    # 数据产生时间12
    create_time = scrapy.Field()
    # 数据插入时间（爬取时间）13
    update_time = scrapy.Field()
    # 数值14
    data_value = scrapy.Field()
    # 个人编号15
    sign = scrapy.Field()
    # 0:无效  1: 有效16
    status = scrapy.Field()
    # 0 : 未清洗  1 ： 清洗过17
    cleaning_status = scrapy.Field()
