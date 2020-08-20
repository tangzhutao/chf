# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import time
import logging
from pybase.apollo_setting import get_project_settings
from Scrapy_CaiZheng_data_V1_01.MysqlPool import MysqlPool

mysql_config = MysqlPool()
cookie = mysql_config.get_cookie()

logger = logging.getLogger(__name__)


class MongoDBPipeline(object):

    settings = get_project_settings()

    def __init__(self):
        self.mongo_uri = self.settings.get('MONGO_URI')
        self.mongo_db = self.settings.get('MONGO_DB')
        self.collection_name = self.settings.get('MONGO_COLLECTION_DATA')
        # self.collection_name = self.settings.get('MONGO_COLLECTION_TEST')

        self.count = 0

    def open_spider(self, spider):
        mysql_config.check_table()
        self.menu_count = mysql_config.menu_count()
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if self.db[self.collection_name].count_documents(
                {
                    'indic_name': item['indic_name'],
                    'frequency': item['frequency'],
                    'data_source': item['data_source'],
                    'region': item['region'],
                    'country': item['country'],
                    'data_value': item['data_value'],
                    "create_time": item["create_time"],
                    "parent_id": item['parent_id'],
                    "unit": item['unit']
                }
        ) == 0:
            self.db[self.collection_name].insert(dict(item))
            self.count += 1
            return item['indic_name']
        else:
            err = 'the data is repetition .' + item['indic_name']
            logger.info(err)
            return None

    def close_spider(self, spider):
        mysql_config.restore(cookie)
        over = mysql_config.menu_count()
        update_menu = over - self.menu_count
        update_time = time.strftime("%Y-%m-%d", time.localtime())
        mysql_config.SpiderLog('Caizheng_data 财政指数', spider.name, update_time, self.count, update_menu, spider.base_url, spider.url_name)

        self.client.close()
