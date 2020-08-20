# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import time
import logging
from Scrapy_Price_data_V1_01 import ApolloConfig as Config
from Scrapy_Price_data_V1_01.MysqlPool import MysqlPool

config = MysqlPool()
cookie = config.get_cookie()
logger = logging.getLogger(__name__)


class MongoDBPipeline(object):

    def __init__(self):
        self.mongo_uri = Config.MONGO_URI
        self.mongo_db = Config.MONGO_DB
        self.collection_name = Config.MONGO_COLLECTION
        self.count = 0
        self.menu_count = None
        self.client = None
        self.db = None

    def open_spider(self, spider):
        config.check_table()
        self.menu_count = config.menu_count()
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if self.db[self.collection_name].count_documents(
                {
                    'indic_name': item['indic_name'],
                    'frequency': item['frequency'],
                    'data_value': item['data_value'],
                    "create_time": item["create_time"],
                    "parent_id": item['parent_id'],
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
        config.restore(cookie)
        over = config.menu_count()
        update_menu = over - self.menu_count
        update_time = time.strftime("%Y-%m-%d", time.localtime())
        config.SpiderLog('Price_data 价格指数', spider.name, update_time, self.count, update_menu, spider.base_url,
                         spider.url_name)
        self.client.close()
