# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RepoItem(scrapy.Item):
    # 1.行业名称
    menu = scrapy.Field()
    # 2.摘要
    abstract = scrapy.Field()
    # 3.标题
    title = scrapy.Field()
    # 4.文件下载地址
    paper_url = scrapy.Field()
    # 5.时间
    date = scrapy.Field()
    # 6.文件来源
    paper_from = scrapy.Field()
    # 7.文件路径
    paper = scrapy.Field()
    # 8.文件作者
    author = scrapy.Field()
    # 9. 更新时间
    update_time = scrapy.Field()
    # 10.父级菜单
    parent_id = scrapy.Field()
    # 11 sign
    sign = scrapy.Field()
    # 12 清洗位
    cleaning_status = scrapy.Field()
