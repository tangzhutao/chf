# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoItem(scrapy.Item):
    # 1、news_id
    news_id = scrapy.Field()
    # 2、所属类别
    category = scrapy.Field()
    # 3、链接地址
    content_url = scrapy.Field()
    # 4、标题
    title = scrapy.Field()
    # 5、发布时间
    issue_time = scrapy.Field()
    # 6、资讯来源(网站名)
    information_source = scrapy.Field()
    # 7、来源
    source = scrapy.Field()
    # 8、作者
    author = scrapy.Field()
    # 9、内容详情
    content = scrapy.Field()
    # 10、内容图片 需下载并保存到本地
    images = scrapy.Field()
    # 11、标题图片 需下载并保存到本地
    title_image = scrapy.Field()
    # 12、附件 需下载并保存到本地
    attachments = scrapy.Field()
    # 13、地区
    area = scrapy.Field()
    # 14、地址
    address = scrapy.Field()
    # 15、标签
    tags = scrapy.Field()
    # 16、签名
    sign = scrapy.Field()
    # 17、时间戳
    update_time = scrapy.Field()
