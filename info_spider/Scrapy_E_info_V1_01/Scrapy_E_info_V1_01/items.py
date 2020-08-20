# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoItem(scrapy.Item):
    # 1.id
    id = scrapy.Field()
    # 2.行业门类
    industry_categories = scrapy.Field()
    # 3.行业大类
    industry_Lcategories = scrapy.Field()
    # 4.行业中类
    industry_Mcategories = scrapy.Field()
    # 5.行业小类
    industry_Scategories = scrapy.Field()
    # 6.资讯类别
    information_categories = scrapy.Field()
    # 7.链接地址
    content_url = scrapy.Field()
    # 8.标题
    title = scrapy.Field()
    # 9.发布时间
    issue_time = scrapy.Field()
    # 10.资讯来源(网站名)
    information_source = scrapy.Field()
    # 11.来源
    source = scrapy.Field()
    # 12.作者
    author = scrapy.Field()
    # 13.内容
    content = scrapy.Field()
    # 14.图片
    images = scrapy.Field()
    # 15.附件
    attachments = scrapy.Field()
    # 16.地区
    area = scrapy.Field()
    # 17.地址
    address = scrapy.Field()
    # 18.标签
    tags = scrapy.Field()
    # 19.sign
    sign = scrapy.Field()
    # 20.update_time
    update_time = scrapy.Field()
    # 21.title_images
    title_images = scrapy.Field()