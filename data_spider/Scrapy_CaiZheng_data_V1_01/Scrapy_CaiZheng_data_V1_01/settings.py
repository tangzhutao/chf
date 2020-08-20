# -*- coding: utf-8 -*-

# Scrapy settings for Scrapy_CaiZheng_data_V1_01 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Scrapy_CaiZheng_data_V1_01'

SPIDER_MODULES = ['Scrapy_CaiZheng_data_V1_01.spiders']
NEWSPIDER_MODULE = 'Scrapy_CaiZheng_data_V1_01.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Scrapy_CaiZheng_data_V1_01 (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'Scrapy_CaiZheng_data_V1_01.middlewares.ProxyMiddleWare': 330,
    # 'Scrapy_CaiZheng_data_V1_01.middlewares.ScrapyRobodatabaseV115DownloaderMiddleware': 543,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,

}

ITEM_PIPELINES = {
    'Scrapy_CaiZheng_data_V1_01.pipelines.MongoDBPipeline': 300,
}

# 日志等级
LOG_LEVEL = 'INFO'

DOWNLOAD_DELAY = 7

# Apollo配置
APP_ID = 'Comprehensive_config_chf,Scrapy_CaiZheng_data_chf'
CLUSTER = 'default'
CONFIG_SERVER_URL = 'http://192.168.3.85:8096/'

RETRY_ENABLED = False  # 打开重试开关
RETRY_TIMES = 3  # 重试次数
DOWNLOAD_TIMEOUT = 10  # 超时
RETRY_HTTP_CODES = [503, 500, 502, 404, 400, 403, 302]

# 爬取十年以前的数据，爬取结束后可取消cookie
# COOKIE = {
#     "JSESSIONID": "1754DB638E98955BB2975EEF95B2B764",
#     "u": "1",
#     "experience": "show",
#     "_trs_uv": "kc1qy830_6_13w3",
# }

# import os
# os.getenv('MONGO_HOST','192.168.0.11')
