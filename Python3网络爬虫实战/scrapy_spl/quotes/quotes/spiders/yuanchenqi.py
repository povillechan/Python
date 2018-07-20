# -*- coding: utf-8 -*-
import scrapy
import os

need_req = []
already_req = []

class YuanchenqiSpider(scrapy.Spider):
    name = 'yuanchenqi'
    allowed_domains = ['cnblogs.com']
    start_urls = ['http://www.cnblogs.com/yuanchenqi/articles/8507109.html']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS':{
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
    }

    def parse(self, response):
     #   print(response.text)
        title = response.css('title::text').extract_first()
        file_path = "%s\\%s.html" % ('E:\\yuanchenqi', title) 
         
        if os.path.exists(file_path):
            os.remove(file_path)
             
        if not os.path.exists(file_path):
            with open(file_path,'wb') as f:
                f.write(response.text.encode("utf-8"))
                f.close()
        

        already_req.append(response.url)
        ab = response.css('#post_next_prev a').extract()         
