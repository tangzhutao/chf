# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # id
    id = scrapy.Field()
    # 行业门类
    industry_categories = scrapy.Field()
    # 行业大类
    industry_Lcategories = scrapy.Field()
    # 行业中类
    industry_Mcategories = scrapy.Field()
    # 行业小类
    industry_Scategories = scrapy.Field()
    # 资讯类别
    information_categories = scrapy.Field()
    # 链接地址
    content_url = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 发布时间
    issue_time = scrapy.Field()
    # 资讯来源(网站名)
    information_source = scrapy.Field()
    # 来源
    source = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 内容
    content = scrapy.Field()
    # 图片
    images = scrapy.Field()
    # 附件
    attachments = scrapy.Field()
    # 地区
    area = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 标签
    tags = scrapy.Field()
    # sign
    sign = scrapy.Field()
    # update_time
    update_time = scrapy.Field()
    # title_images
    title_images = scrapy.Field()
