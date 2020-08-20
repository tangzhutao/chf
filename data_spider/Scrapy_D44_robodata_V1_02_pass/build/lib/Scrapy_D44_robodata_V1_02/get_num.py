import pymongo
import time


class lalal():
    def __init__(self):
        self.mongourl = '192.168.0.11'
        self.mongoDB = 'industry'
        self.client = pymongo.MongoClient(self.mongourl)
        self.db = self.client[self.mongoDB]
        self.collection_name = 'CaiZheng_data'
        #

    def connect(self):
        # a = "2020-04-01"
        a = "2020-07-01"
        b = time.mktime(time.strptime(a, "%Y-%m-%d"))
        for i in range(30):
            c = b + 86400 * i
            d = time.strftime("%Y-%m-%d", time.localtime(c))
            date = {'issue_time': f'{d}'}
            a1 = self.db[self.collection_name].find(date).count()
            print(a1)

    def close(self):
        self.client.close()


if __name__ == '__main__':
    a = lalal()
    a.connect()
