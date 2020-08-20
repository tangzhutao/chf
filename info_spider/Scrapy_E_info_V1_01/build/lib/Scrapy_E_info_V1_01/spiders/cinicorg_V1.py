# -*- coding: utf-8 -*-
import scrapy, re
from Scrapy_E_info_V1_01.items import InfoItem
import time
from scrapy.utils import request


class CinicorgV1Spider(scrapy.Spider):
    name = 'cinicorg_V1'
    allowed_domains = ['www.cinic.org.cn']
    base_url = 'http://www.cinic.org.cn'
    url_name = '中国产业经济信息网'
    urls = {
        'http://www.cinic.org.cn/hy/jz/index_2.html': '行业资讯4',  # 每页10条
    }

    def start_requests(self):

        for url, cate in self.urls.items():
            page = cate[4:]
            for i in range(2, int(page)):
                link = url.replace(url[-6:-4], f'{i}.')
                yield scrapy.Request(url=link, callback=self.parse, meta={'cate': cate[:4]}, dont_filter=True)

        yield scrapy.Request(url='http://www.cinic.org.cn/hy/jz/index.html', callback=self.parse, meta={'cate': '行业资讯'},
                             dont_filter=True)

    def parse(self, response):
        cate = response.meta['cate']
        config_list = response.xpath('//div[@class="col-l"]/ul/li')
        for config in config_list:
            item = InfoItem()
            title_img = config.xpath('./div/div[@class="img"]/a/img/@src').extract_first()
            title = config.xpath('./div/div[@class="txt"]/h3/a/text()').extract_first()
            link = self.base_url + config.xpath('./div/div[@class="txt"]/h3/a/@href').extract_first()
            issue_time = config.xpath(
                './div/div[@class="txt"]/div/div/div/span[@class="sp2"]/text()').extract_first()
            # tags = config.xpath('./div[@class="right"]/ul/li/a/text()').extract()
            item['title'] = title
            item['issue_time'] = issue_time
            item['content_url'] = link
            item['information_categories'] = cate
            item['title_images'] = self.base_url + title_img if title_img else None
            req = scrapy.Request(url=link, callback=self.parse2,
                                 meta={'item': item},
                                 dont_filter=True)
            item['id'] = request.request_fingerprint(req)
            yield req

    def parse2(self, response):
        item = response.meta['item']
        content = response.xpath('//div[@class="dc-ccm1"]').extract_first()
        images = response.xpath('//div[@class="dc-ccm1"]//img/@src').extract()
        if images:
            images_url = []
            for img in images:
                if 'http' in img:
                    images_url.append(img)
                else:
                    image = f'{self.base_url}{img}'
                    images_url.append(image)
            images_urls = '; '.join(images_url)
            item['images'] = images_urls if images_urls else None
        else:
            item['images'] = None
        item['tags'] = None
        item['industry_categories'] = 'E'
        item['industry_Lcategories'] = '47'
        item['industry_Mcategories'] = None
        item['industry_Scategories'] = None
        item['sign'] = '19'
        item['update_time'] = str(int(time.time() * 1000))
        item['information_source'] = '中国产业经济信息网'
        try:
            source = response.xpath('//div[@class="col-l"]/div[1]/center/text()').extract_first()
            source = re.search(r'来源：(.+)时间', source).group(1).strip()
            item['source'] = source if source else '中国产业经济信息网'
        except:
            item['source'] = None
        item['area'] = None
        item['address'] = None
        item['attachments'] = None
        # item['images'] = None
        # author = response.xpath('//div[@class="info_title"]/span[3]/text()').extract_first()[3:].strip()
        item['author'] = None
        item['content'] = content
        if content:
            yield item
            self.logger.info("title({}), issue_time({})".format(item['title'], item['issue_time']))


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute(['scrapy', 'crawl', 'cinicorg_V1'])
