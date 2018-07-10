# -*- coding: utf-8 -*-
import scrapy


class A8080Spider(scrapy.Spider):
    name = '8080'
    allowed_domains = ['8080.net']
    start_urls = ['http://www.8080.net/']

    def parse(self, response):
        pass
