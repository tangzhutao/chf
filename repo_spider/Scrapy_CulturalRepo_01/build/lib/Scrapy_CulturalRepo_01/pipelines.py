# -*- coding: utf-8 -*-
import pymongo
import requests
import time
import pdfkit
import os
import logging
from pybase.apollo_setting import get_project_settings
from Scrapy_CulturalRepo_01.MySQL_Pool import Mysql
from urllib3 import encode_multipart_formdata

logger = logging.getLogger(__name__)
MysqlConfig = Mysql()


class MongoPipeline(object):
    config = get_project_settings()

    def __init__(self):
        self.mongo_uri = self.config.get('MONGO_URI')
        self.mongo_db = self.config.get('MONGO_DB')
        self.collection_name = self.config.get('MONGO_COLLECTION_REPO')
        self.filepath = self.config.get("PDF_PATH")
        self.spider_name = self.config.get('SPIDER_NAME')
        self.uploadurl = self.config.get('UPLOADURL')
        self.wkhtmltox_path = self.config.get("WKHTMLTOX_PATH")
        # self.uploadurl = r'C:\Users\Administrator\Desktop'
        self.count = 0
        self.client = None
        self.db = None
        self.menu_count = 0

    def open_spider(self, spider):
        MysqlConfig.check_table()
        self.menu_count = MysqlConfig.menu_count()
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        over = MysqlConfig.menu_count()
        update_menu_count = over - self.menu_count
        update_time = time.strftime("%Y-%m-%d", time.localtime())
        MysqlConfig.SpiderLog('Cultural_repo', spider.name, update_time, self.count, update_menu_count, spider.base_url,
                              spider.url_name)
        MysqlConfig.dispose()
        self.client.close()

    def process_item(self, item, spider):
        if self.db[self.collection_name].count_documents(
                {
                    'paper_url': item['paper_url'],
                    'title': item['title'],
                    'date': item['date'],
                    'parent_id': item['parent_id'],
                    "paper_from": item["paper_from"],
                }
        ) == 0:

            # 下载文件,并上传
            file_path = os.path.join(self.filepath, spider.url_name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = os.path.join(file_path, item['title'] + '.pdf')
            res = download_repo(file_name, item['paper_url'], self.uploadurl, self.spider_name, self.wkhtmltox_path)
            if res['success']:
                logger.info({'PDF上传完成': item['paper_url']})
                item['paper'] = res['data']['url']

                # 文件上传成功后删除文件
                if os.path.exists(file_name):
                    os.remove(file_name)

            else:
                logger.info({'PDF上传失败': item['paper_url']})
                item['paper'] = None

            self.db[self.collection_name].insert(dict(item))
            self.count += 1
            update = 'the date is update: ' + item['title']
            logger.info(update)
            return
        else:
            err = 'the data is repetition .' + item['title']
            logger.info(err)
            return


# 下载文件, 并上传服务器
def download_repo(filename, url, uploadurl, spider_name, wkhtmltox_path):
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltox_path)
    # pdf文件 格式
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",  # 支持中文
    }
    # 生成pdf文件，to_file为文件路径
    pdfkit.from_string(url, filename, configuration=config, options=options)

    name = os.path.basename(filename)
    with open(filename, mode='rb') as a:
        file = {
            'file': (name, a.read())
        }
        send_url = uploadurl + spider_name
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        headers_from_data = {"Content-Type": encode_data[1]}
        response = requests.post(url=send_url, headers=headers_from_data, data=file_data).json()
        return response
