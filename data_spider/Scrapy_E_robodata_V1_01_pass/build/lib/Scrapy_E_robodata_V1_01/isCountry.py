from Scrapy_E_robodata_V1_01.settings import COUNTRY, PROVINCES


def find_region(name):
    item = {}
    # 国家
    for c in COUNTRY:
        if c in name:
            if c != '中国':
                item['country'] = c
                item['region'] = '全国'
    # 地区
    for p in PROVINCES['all']:
        if p in name:
            item['country'] = '中国'
            item['region'] = p
            break
    for city in PROVINCES['city']:
        key = city.replace('市', '')
        if key in name:
            item['country'] = '中国'
            item['region'] = city
            break
    if len(item) <= 0:
        # 国家
        item['country'] = None
        # 地区
        item['region'] = None
    # print(item)
    return item


if __name__ == '__main__':
    name = 'NYMEX:日本:持仓比重:总计持仓:原有持仓'
    name1 = '洲际交易所(欧洲):低硫轻质原油:资产管理机构:报告头寸:多头:所有'
    a = find_region(name)
    print(a)
