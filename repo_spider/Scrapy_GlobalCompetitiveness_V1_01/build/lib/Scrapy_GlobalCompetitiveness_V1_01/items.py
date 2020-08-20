# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# class ScrapyItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     # # 1.行业名称
#     # menu = scrapy.Field()
#     # 2.摘要
#     abstract = scrapy.Field()
#     # 3.标题
#     title = scrapy.Field()
#     # 4.文件下载地址
#     paper_url = scrapy.Field()
#     # 5.时间
#     date = scrapy.Field()
#     # 6.文件来源
#     paper_from = scrapy.Field()
#     # 7.文件路径
#     paper = scrapy.Field()
#     # 8.作者
#     author = scrapy.Field()
#     # # 9.父级目录
#     # parent_name = scrapy.Field()
#     # 10.父级菜单
#     parent_id = scrapy.Field()
#     # 11.清洗位
#     cleaning_status = scrapy.Field()


class RepoItem(scrapy.Item):
    # 1.摘要
    paper_abstract = scrapy.Field()
    # 2.标题
    title = scrapy.Field()
    # 3.文件下载地址
    paper_url = scrapy.Field()
    # 4.时间
    date = scrapy.Field()
    # 5.文件来源
    paper_from = scrapy.Field()
    # 6.文件路径
    paper = scrapy.Field()
    # 7.作者
    author = scrapy.Field()
    # 8.父级菜单
    parent_id = scrapy.Field()
    # 9.清洗位
    cleaning_status = scrapy.Field()
    # 10.paper_type
    paper_type = scrapy.Field()
    # 11.image_url
    image_url = scrapy.Field()

    headers = scrapy.Field()
    proxy = scrapy.Field()
