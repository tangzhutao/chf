# -*- coding: utf-8 -*-
import pymongo
import time
import os
import requests
import logging
from pybase.apollo_setting import get_project_settings
from urllib3 import encode_multipart_formdata
from Scrapy_OverallBalance_V1_01.MysqlPool import MysqlPool
from Scrapy_OverallBalance_V1_01 import ApolloConfig as Config

config = MysqlPool()
logger = logging.getLogger(__name__)


class MongoPipeline(object):
    st = get_project_settings()

    def __init__(self):
        self.mongo_uri = Config.MONGO_URI
        self.mongo_db = Config.MONGO_DB
        self.collection_name = Config.MONGO_COLLECTION
        self.count = 0
        self.menu_count = 0
        self.client = None
        self.db = None

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        update_time = time.strftime("%Y-%m-%d", time.localtime())
        config.SpiderLog('综合平衡 资讯', spider.name, update_time, self.count, self.menu_count, spider.base_url, spider.url_name)
        self.client.close()

    def process_item(self, item, spider):

        if self.db[self.collection_name].count_documents(
                {
                    'news_id': item['news_id'],
                    'title': item['title'],
                    'issue_time': item['issue_time'],
                    'information_source': item['information_source'],
                    "source": item["source"],
                }
        ) == 0:
            images = []

            if item['images_url']:
                for url in item['images_url']:
                    # 下载图片
                    # IMAGES_STORE = r'C:\Users\Administrator\Desktop\images\综合平衡'
                    file_path = os.path.join(Config.IMAGES_STORE, spider.url_name)
                    if not os.path.exists(file_path):
                        os.makedirs(file_path)
                    file_name = os.path.join(file_path, url.split('/')[-1])
                    res = download_img(file_name, url, item['headers'], None)
                    if res['success']:
                        logger.info({'图片上传完成': url})
                        images.append(res['data']['url'])

                        # 文件上传成功后删除文件
                        if os.path.exists(file_name):
                            os.remove(file_name)
                    else:
                        logger.info({'图片上传失败': url})

            item['images'] = ','.join(images) if images else None
            del item['headers']
            del item['images_url']
            # del item['proxy']

            self.db[self.collection_name].insert(dict(item))
            self.count += 1
            return item['title']
        else:
            err = 'the data is repetition .' + item['title']
            logger.info(err)
            return


# 下载图片
def download_img(filename, url, headers, proxy):
    # if 'https' in url:
    #     proxies = {
    #         'https': proxy
    #     }
    # else:
    #     proxies = {
    #         'http': proxy
    #     }
    try:
        # resp = requests.get(url=url, headers=headers, proxies=proxies, timeout=40, stream=True, verify=False)
        resp = requests.get(url=url, headers=headers, timeout=40, stream=True, verify=False)

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
        send_url = Config.UPLOADURL + Config.SPIDER_NAME
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        headers_from_data = {"Content-Type": encode_data[1]}
        response = requests.post(url=send_url, headers=headers_from_data, data=file_data).json()
        return response


def formatFloat(num):
    return '{:.2f}'.format(num)
