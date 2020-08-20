import requests


# 获取代理
def get_proxy():
    proxy = requests.get("http://192.168.0.11:5010/get/").json().get("proxy")
    # proxy = '223.111.131.100:8080'
    if proxy:
        proxy_dict = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        return proxy_dict
    else:
        return ('The proxys is empty')


# 获取所有代理
def get_all():
    proxy_list = []
    get_all_proxy = requests.get('http://192.168.0.11:5010/get_all/').json()
    for proxy in get_all_proxy:
        proxy_list.append(proxy['proxy'])
    return proxy_list


# 查看代理数量
def get_status():
    useful_proxy = requests.get('http://192.168.0.11:5010/get_status/').json().get('useful_proxy')
    return useful_proxy


# if __name__ == '__main__':
    # print(get_proxy())
    # print(get_status())

    # p = get_all()
    # print(p)
    # p.remove(p[0])
    # print(p)
# MiddleWare
# class ProxyMiddleWare(object):
#     def process_request(self, request, spider):
#         # 对 request 加上 proxy
#         proxy = get_proxy()
#         # print('this is request ip :' + proxy['https'])
#         request.meta['proxy'] = proxy['http']
#
#     def process_response(self, request, response, spider):
#         # 如果返回的 response 状态不是 200 ，重新声称当前的 request 对象
#         try:
#             if response.statys != 200:
#                 proxy = get_proxy()
#                 request.meta[proxy] = proxy
#                 print('this is response ip:' + proxy['http'])
#                 # 对当前request 加上代理
#                 return request
#         except:
#             proxy =get_proxy()
#             request.meta['proxy'] = proxy['http']
#             print('this is response ip:' + proxy['http'])
#             # 对当前 request 加上代理
#             return request
#
#         return response
