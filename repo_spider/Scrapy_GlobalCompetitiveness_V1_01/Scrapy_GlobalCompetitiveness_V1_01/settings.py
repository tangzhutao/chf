# Scrapy config for Scrapy_GlobalCompetitiveness_V1_01 project
#
# For simplicity, this file contains only config considered important or
# commonly used. You can find more config consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/config.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Scrapy_GlobalCompetitiveness_V1_01'

SPIDER_MODULES = ['Scrapy_GlobalCompetitiveness_V1_01.spiders']
NEWSPIDER_MODULE = 'Scrapy_GlobalCompetitiveness_V1_01.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Scrapy_GlobalCompetitiveness_V1_01 (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 5

DOWNLOADER_MIDDLEWARES = {
    'Scrapy_GlobalCompetitiveness_V1_01.middlewares.ProxyMiddleWare': 301,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,

}

ITEM_PIPELINES = {
    'Scrapy_GlobalCompetitiveness_V1_01.pipelines.MongoPipeline': 300,
}

# apollo 配置中心
APP_ID = '123456'
CLUSTER = 'GlobalCompetitiveness_config'
CONFIG_SERVER_URL = 'http://192.168.3.85:8096/'

from pybase.apollo_setting import get_project_settings
config = get_project_settings()

# 上传文件配置
SPIDER_NAME = config.get("SPIDER_NAME")
UPLOADURL = config.get('UPLOADURL')

# 日志文件等级
LOG_LEVEL = 'INFO'

# 重试设置
RETRY_ENABLED = False    # 开始失败重试，默认关闭
RETRY_TIMES = 4
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 404] # 遇到这一类状态码，重试
