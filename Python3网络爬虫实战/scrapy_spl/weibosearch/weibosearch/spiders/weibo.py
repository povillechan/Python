# -*- coding: utf-8 -*-
from scrapy import Spider, FormRequest


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'http://weibo.cn/search/mblog'
    start_urls = ['http://weibo.cn/']
    max_page = 100

    def start_requests(self):
        keyword = '000001'
        url = '{url}?keyword={keyword}'.format(url=self.search_url, keyword=keyword)
        for page in range(self.max_page):
            data = {
                'mp':str(self.max_page),
                'page': str(page)
            }
            yield FormRequest(url, callback=self.parse_index, formdata=data)

    def parse_index(self, response):
        pass
        
    def parse(self, response):
        pass
