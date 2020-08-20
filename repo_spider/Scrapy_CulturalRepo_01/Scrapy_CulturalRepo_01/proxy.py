import requests


# 获取代理
def get_proxy():
    proxy = requests.get("http://192.168.3.85:5010/get/").json().get("proxy")
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
    get_all_proxy = requests.get('http://192.168.3.85:5010/get_all/').json()
    for proxy in get_all_proxy:
        proxy_list.append(proxy['proxy'])
    return proxy_list


# 查看代理数量
def get_status():
    useful_proxy = requests.get('http://192.168.3.85:5010/get_status/').json().get('useful_proxy')
    return useful_proxy
