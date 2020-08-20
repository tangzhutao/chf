# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
import hashlib
from Scrapy_CulturalRepo_01.items import RepoItem
from Scrapy_CulturalRepo_01.pipelines import MysqlConfig


class CulturalSpider(scrapy.Spider):
    name = 'Cul_GD'

    base_url = 'http://whly.gd.gov.cn/'
    url_name = '广东省文化和旅游厅'
    file_id = hashlib.md5(url_name.encode('utf-8')).hexdigest()

    def start_requests(self):
        # 广东省文化和旅游部
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

        # url = 'http://whly.gd.gov.cn/gkmlpt/annualreport#2629'
        url = 'http://whly.gd.gov.cn/gkmlpt/api/all/2629?page=1&sid=175'
        yield scrapy.Request(url=url, callback=self.parse1, dont_filter=True, meta={'parent_id': menu_id})

    def parse1(self, response):
        # 获取报告标题
        config_info = json.loads(response.text)['articles']
        for info in config_info:
            title = info['title']
            url = info['url']
            issue_time = time.strftime("%Y-%m-%d", time.localtime(int(info['create_time'])))
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse2, dont_filter=True,
                                 meta={'parent_id': response.meta['parent_id'], 'title': title,
                                       'issue_time': issue_time})

    def parse2(self, response):
        item = RepoItem()
        # title = response.xpath('//h1[@class="content-title"]/text()').extract_first()
        # issue_time = response.xpath('//div[@class="content-desc"]/span[1]/text()').extract_first().split(' ')[0][6:]
        # 获取正文
        content = response.xpath('//div[@class="content"]')
        srcs = content.css('img')
        if not content.get():
            return
        h1 = '<h1 style="text-align: center; font-weight:bold;">' + response.meta['title'] + '</h1>'
        # 重构html文本
        html = '<html><head><meta charset="utf-8"></head><body>' + h1 + content.get() + '</body></html>'
        # 替换图片路径
        for src in srcs:
            link = response.urljoin(src.attrib.get("src"))
            html = re.sub(src.attrib.get('src'), link, html)

        item["menu"] = '文化资源'
        item["abstract"] = None
        item["paper_from"] = '广东省文化和旅游厅'
        item['author'] = None
        item["parent_id"] = response.meta['parent_id']
        item["cleaning_status"] = 0
        item["sign"] = '19'
        item["update_time"] = str(int(time.time()) * 1000)
        item["paper_url"] = response.urljoin(response.url)
        item["title"] = response.meta['title']
        item["date"] = response.meta['issue_time']
        item['paper'] = None

        yield item
        # self.logger.info("title:{}, date: {}".format(item['title'], item['date']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute("scrapy crawl Cul_GD".split())
