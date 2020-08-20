# Scrapy settings for Scrapy_InternationalEconomic_info_V1_01 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Scrapy_InternationalEconomic_info_V1_01'

SPIDER_MODULES = ['Scrapy_InternationalEconomic_info_V1_01.spiders']
NEWSPIDER_MODULE = 'Scrapy_InternationalEconomic_info_V1_01.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Scrapy_InternationalEconomic_info_V1_01 (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 3

DOWNLOADER_MIDDLEWARES = {
    'Scrapy_InternationalEconomic_info_V1_01.middlewares.ProxyMiddleWare': 300,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'Scrapy_InternationalEconomic_info_V1_01.pipelines.MongoPipeline': 500,
}

# apollo 配置中心
APP_ID = '123456'
CLUSTER = 'InternationalEconomic_info'
CONFIG_SERVER_URL = 'http://192.168.3.85:8096/'

from pybase.apollo_setting import get_project_settings
settings = get_project_settings()

# 图片储存
IMAGES_STORE = settings.get('IMAGES_STORE')
SPIDER_NAME = settings.get("SPIDER_NAME")
UPLOADURL = settings.get('UPLOADURL')

# 日志文件等级
LOG_LEVEL = 'INFO'

# 重试设置
RETRY_ENABLED = False  # 默认开启失败重试，一般关闭
RETRY_TIMES = 3  # 失败后重试次数，默认两次
# DOWNLOAD_TIMEOUT = 40
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408]  # 碰到这些验证码，才开启重试
