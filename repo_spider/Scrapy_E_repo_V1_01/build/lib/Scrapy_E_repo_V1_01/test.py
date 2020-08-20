import requests, random
from Scrapy_E_repo_V1_01.proxy import get_proxy
from urllib3 import encode_multipart_formdata
from Scrapy_E_repo_V1_01.settings import SPIDER_NAME, UPLOADURL, MY_USER_AGENT


def download_repo(url):
    headers = {
        'User-Agent': MY_USER_AGENT[random.randrange(1, len(MY_USER_AGENT), 1)]
    }
    print(MY_USER_AGENT[random.randrange(1, len(MY_USER_AGENT), 1)])
    proxies = get_proxy()
    resp = requests.get(url, headers=headers, proxies=proxies)
    # print(resp)
    # print(resp.elapsed.total_seconds())
    file_name = url.split('/')[-1]
    file = {
        'file': (file_name, resp.content)
    }
    send_url = UPLOADURL + SPIDER_NAME
    encode_data = encode_multipart_formdata(file)
    file_data = encode_data[0]
    headers_from_data = {
        "Content-Type": encode_data[1]
    }
    response = requests.post(url=send_url, headers=headers_from_data, data=file_data).json()
    return response


if __name__ == '__main__':
    url = 'https://wkpdf.askci.com/20-07-24/202072418297774.pdf'
    # url = 'https://www.cnblogs.com/canglongdao/p/13440834.html'
    res = download_repo(url)
    print(res)
