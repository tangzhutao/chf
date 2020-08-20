# import requests
# from Scrapy_E_Data_V1_01.proxy import get_proxy
#
# url = 'https://data.iimedia.cn/front/getObjInfoByNodeId'
#
# headers = {
#     "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
# }
#
# a = get_proxy()
# proxies = {
#     'https': a['https']
# }
# data = {
#     'node_id': '13176854',
# }
#
# req = requests.post(url=url, headers=headers, proxies=proxies, data=data)
#
# print(req.text)
# # import datetime
#
# # datetime.date(year, month, 1)
# def last_day(any_day):
#     next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
#     return next_month - datetime.timedelta(days=next_month.day)
#
#
# if __name__ == '__main__':
#     a = datetime.date(2020, 12, 1)
#     b = last_day(a)
#     print(b)


import pymongo, time


def test():
    #     "parent_id" : "5004001006003003001001409",
    #     "indic_name" : "国有及国有控股建筑业企业教育用房屋竣工价值_累计值-江西省",
    #     "root_id" : "5",
    #     "region" : "江西",
    #     "country" : "中国",
    #     "data_year" : 2013,
    #     "data_month" : 6,
    #     "data_day" : 30,
    #     "frequency" : 2,
    #     "unit" : "亿元",
    #     "data_source" : "中国国家统计局",
    #     "create_time" : "2013-06-30",
    #     "data_value" : 2.15,
    b = time.time()
    cn = pymongo.MongoClient('192.168.3.85')
    db = cn['industry']
    a = db['E_data_pass'].count_documents({
        'indic_name': "国有及国有控股建筑业企业教育用房屋竣工价值_累计值-江西省",
        'frequency': 2,
        'data_source': "中国国家统计局",
        'region': "江西",
        'country': "中国",
        'data_value': 2.15,
        "create_time": "2013-06-30",
        "parent_id": "5004001006003003001001409",
        "unit": "亿元"
    })
    c = time.time()
    print(c - b)
    print(a)
    cn.close()


if __name__ == '__main__':
    test()
