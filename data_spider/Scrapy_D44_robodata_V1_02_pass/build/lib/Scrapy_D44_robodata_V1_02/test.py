import requests
from Scrapy_D44_robodata_V1_02.proxy import get_proxy

url = 'https://data.iimedia.cn/front/getObjInfoByNodeId'

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
}

a = get_proxy()
proxies = {
    'https': a['https']
}
data = {
    'node_id': '30416885',
}

req = requests.post(url=url, headers=headers, proxies=proxies, data=data)

print(req.text)
# import datetime
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
