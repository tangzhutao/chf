# -*- coding: utf-8 -*-
import pymongo
import time
import os
import logging
from pybase.apollo_setting import get_project_settings
from Scrapy_D44_info_V1_01.MysqlPool import MysqlPool

config = MysqlPool()
logger = logging.getLogger(__name__)


class MongoPipeline(object):
    st = get_project_settings()

    def __init__(self):
        self.mongo_uri = self.st.get('MONGO_URI')
        self.mongo_db = self.st.get('MONGO_DB')
        self.collection_name = self.st.get('MONGO_COLLECTION_INFO')
        self.count = 0
        self.menu_count = 0
        self.client = None
        self.db = None

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        update_time = time.strftime("%Y-%m-%d", time.localtime())
        config.SpiderLog('D44_info 电力、热力生产及供应业', spider.name, update_time, self.count, self.menu_count, spider.base_url,
                         spider.url_name)
        self.client.close()

    def process_item(self, item, spider):
        if self.db[self.collection_name].count_documents(
                {
                    'id': item['id'],
                }
        ) == 0:
            self.db[self.collection_name].insert(dict(item))
            self.count += 1
            update = 'the data is update ：' + item['title']
            return update
        else:
            err = 'the data is repetition .' + item['title']
            logger.info(err)
            return
