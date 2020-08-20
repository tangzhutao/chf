# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo, datetime, time, pymysql
import logging
from pymysql.cursors import DictCursor
from pybase.apollo_setting import get_project_settings
from Scrapy_E_robodata_V1_01.mysqlAPI import change_state, restore
from Scrapy_E_robodata_V1_01.spiders.E_Robo_01 import cookie

logger = logging.getLogger(__name__)


class MongoDBPipeline(object):

    settings = get_project_settings()

    def __init__(self):
        self.mongo_uri = self.settings.get('MONGO_URI')
        self.mongo_db = self.settings.get('MONGO_DB')
        self.collection_name = self.settings.get('MONGO_COLLECTION_DATA')
        # self.collection_name = self.settings.get('MONGO_COLLECTION_TEST')
        # self.mongo_uri = '192.168.0.39'
        # self.mongo_db = 'Electricity_datas'
        # self.collection_name = 'D44_data_new'

        # self.MYSQL_HOST = self.settings.get("MYSQL_HOST")
        # self.MYSQL_USER = self.settings.get("MYSQL_USER")
        # self.MYSQL_PASSWORD = self.settings.get("MYSQL_PASSWORD")
        # self.MYSQL_DATABASE = self.settings.get("MYSQL_DATABASE")

    def open_spider(self, spider):
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
            return item['indic_name']
        else:
            err = 'the data is repetition .' + item['indic_name']
            logger.info(err)
            return None
        # self.db[COLLECTION_NAME].insert(dict(item))
        # self.db[self.collection_name].update({'paper_url':item['paper_url']},{'$set':item}, True)
        # return item

    def close_spider(self, spider):
        restore(cookie)
        self.client.close()
