# -*- coding: utf-8 -*-
import scrapy
import hashlib
import re
import time
from Scrapy_CulturalRepo_01.items import RepoItem
from Scrapy_CulturalRepo_01.pipelines import MysqlConfig


class CulturalSpider(scrapy.Spider):
    name = 'Cul_Country'
    base_url = 'http://www.mct.gov.cn/'
    url_name = '国家文化和旅游部'
    file_id = hashlib.md5(url_name.encode('utf-8')).hexdigest()

    def start_requests(self):
        # 国家文化和旅游部
        p_id = '4'
        p_name = '文化资源'
        MysqlConfig.insert(p_id, p_name, None, p_name)

        menu_name = self.url_name
        if not MysqlConfig.select(menu_name, p_id, menu_name):
            n = MysqlConfig.select_count(p_id) + 1
            menu_id = p_id + "{:03d}".format(n)
            MysqlConfig.insert(menu_id, menu_name, p_id, menu_name)
        else:
            menu_id = MysqlConfig.select(menu_name, p_id, menu_name)['menu_id']

        urls = ['http://zwgk.mct.gov.cn/gknb/index.html', 'http://zwgk.mct.gov.cn/gknb/index_1.html']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse1, dont_filter=True, meta={'parent_id': menu_id})

    def parse1(self, response):
        # 获取报告标题
        content = response.xpath('//a[@class="a1"]')
        for i in content:
            title = i.xpath('./text()').get()
            # 过滤非报告类型url
            if title[-2:] == "报告" and '图解' not in title:
                url = i.xpath('./@href').get()
                url = 'http://zwgk.mct.gov.cn/gknb/' + url[2:]
                yield scrapy.Request(url=response.urljoin(url), callback=self.parse2, dont_filter=True,
                                     meta={'parent_id': response.meta['parent_id']})

    def parse2(self, response):
        item = RepoItem()
        title = response.xpath('//div[@class="main"]/table/tr/td/table/tr[1]/td/text()').extract_first()
        issue_time = response.xpath('//div[@class="main"]/table/tr/td/table/tr[2]/td/text()').extract_first()
        # 获取正文
        content = response.xpath('//div[@class="TRS_Editor"]')
        srcs = content.css('img')
        if not content.get():
            return
        h1 = '<h1 style="text-align: center; font-weight:bold;">' + title + '</h1>'
        # 重构html文本
        html = '<html><head><meta charset="utf-8"></head><body>' + h1 + content.get() + '</body></html>'
        # 替换图片路径
        for src in srcs:
            link = response.urljoin(src.attrib.get("src"))
            html = re.sub(src.attrib.get('src'), link, html)

        item["menu"] = '文化资源'
        item["abstract"] = None
        item["paper_from"] = '中华人民共和国文化和旅游部'
        item['author'] = None
        item["parent_id"] = response.meta['parent_id']
        item["cleaning_status"] = 0
        item["sign"] = '19'
        item["update_time"] = str(int(time.time()) * 1000)
        item["paper_url"] = response.urljoin(response.url)
        item["title"] = title
        item["date"] = issue_time
        item["paper"] = None

        yield item
        # self.logger.info("title:{}, date: {}".format(item['title'], item['date']))


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute(['scrapy', 'crawl', 'Cul_Country'])
