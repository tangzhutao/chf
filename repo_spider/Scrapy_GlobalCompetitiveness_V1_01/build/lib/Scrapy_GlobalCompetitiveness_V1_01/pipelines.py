# -*- coding: utf-8 -*-
import pymongo
import requests
import time
import os
import logging
from pybase.apollo_setting import get_project_settings
from Scrapy_GlobalCompetitiveness_V1_01.MySQL_Pool import Mysql
from urllib3 import encode_multipart_formdata
from Scrapy_GlobalCompetitiveness_V1_01.settings import SPIDER_NAME, UPLOADURL

logger = logging.getLogger(__name__)
MysqlConfig = Mysql()


class MongoPipeline(object):
    st = get_project_settings()

    def __init__(self):
        self.mongo_uri = self.st.get('MONGO_URI')
        self.mongo_db = self.st.get('MONGO_DB')
        self.collection_name = self.st.get('MONGO_COLLECTION_REPO')
        self.filepath = self.st.get("PDF_PATH")
        # self.filepath = 'C:\\Users\\Administrator\\Desktop\\'
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
        MysqlConfig.SpiderLog('GlobalCompetitiveness_repo', spider.name, update_time, self.count, update_menu_count,
                              spider.base_url, spider.url_name)
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
            # 下载文件
            file_path = os.path.join(self.filepath, spider.url_name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = os.path.join(file_path, item['paper_url'].split('/')[-1])

            res = download_repo(file_name, item['paper_url'], item['headers'], item['proxy'])
            if res['success']:
                logger.info({'PDF上传完成': item['paper_url']})
                item['paper'] = res['data']['url']

                # 文件上传成功后删除文件
                if os.path.exists(file_name):
                    os.remove(file_name)

            else:
                logger.info({'PDF上传失败': item['paper_url']})
                item['paper'] = None
            del item['headers']
            del item['proxy']
            self.db[self.collection_name].insert(dict(item))
            self.count += 1
            return item['title']
        else:
            err = 'the data is repetition .' + item['title']
            logger.info(err)
            return


# 下载文件
def download_repo(filename, url, headers, proxy):
    proxies = {
        'http': proxy[8:]
    }
    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies, timeout=40, stream=True, verify=False)

        length = float(resp.headers['content-length'])
        with open(filename, 'wb') as f:
            count = 0
            count_tmp = 0
            time1 = time.time()
            # f.write(resp.content)
            for chunk in resp.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
                    count += len(chunk)
                    if time.time() - time1 >= 6:
                        p = count / length * 100
                        speed = (count - count_tmp) / 1024 / 1024 / 6
                        count_tmp = count
                        logger.info(os.path.basename(filename) + ': ' + formatFloat(p) + '%' + ' Speed: ' + formatFloat(
                            speed) + 'M/S')
                        time1 = time.time()
    except Exception as e:
        logger.info("下载超时：" + url + "----------错误为：")
        logger.info(e)
        return

    name = os.path.basename(filename)
    with open(filename, mode='rb') as a:
        file = {
            'file': (name, a.read())
        }
        send_url = UPLOADURL + SPIDER_NAME
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        headers_from_data = {"Content-Type": encode_data[1]}
        response = requests.post(url=send_url, headers=headers_from_data, data=file_data).json()
        return response


def formatFloat(num):
    return '{:.2f}'.format(num)
