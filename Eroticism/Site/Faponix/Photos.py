# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParser import CParseType, CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from Common.CWebParserProcess import CWebParserProcess
from copy import deepcopy
from pyquery import PyQuery as pq


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    #
    def parse_item(self, item):
        product_name = item.attr('title')
        product_url = item.attr('href')

        data_brief = {
            'url': product_url,
            'name': product_name,
        }

        data = {'brief': data_brief}

        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None

        product_url = item.get('brief').get('url')
        html = self.webParser.utils.get_page(product_url)
        if html:
            b = pq(html)
            stills = []
            previews = b('div.masonry_thumbs div.item div.masonry_item > a')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))

            data_detail = {
                'galleries': {
                    'name': item.get('brief').get('name'),
                    'url': product_url,
                    'stills': stills,
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail

        return data


class CWebParserSite(CWebParserSingleUrl):
    def __init__(self, **kwArgs):
        super().__init__(**kwArgs)
        self.utils = CWebSpiderUtils(self.savePath)
        self.common = CWebParserSiteCommon(self)
        self.dbUtils = CWebDataDbUtis(kwArgs.get('database'))

    '''
    parse_page
    
    @author: chenzf
    '''

    def parse_page(self, url):
        try:
            if not url:
                yield None

            if self.dbUtils.get_db_url(url):
                yield None

            end_pos = url.rfind('/') - 1  # 倒数第一个"/"的位置再左移一位
            start_pos = url.rfind('/', 0, end_pos)  # 网址从开始截至到end_pos的位置，从右往左出现的第一个"/"也就是我们要找的倒数第二个"/"
            name = url[start_pos + 1:]  # 截取网址的倒数第二个 "/" 后面的内容

            data_total = 1
            html = self.utils.get_page(url)
            if html:
                a = pq(html)
                data_total = a('button.js-load-more').attr('data-total')
                if not data_total:
                    data_total = 1

            if int(data_total) > 0:
                for page in range(1, int(data_total) + 1):
                    try:
                        cate_url = '%s?mode=async&action=get_block&block_id=list_albums_common_albums_list&from=%s' % (
                            url, page)

                        if self.dbUtils.get_db_url(cate_url):
                            continue

                        html = self.utils.get_page(cate_url)
                        if html:
                            b = pq(html)

                            items = b('div.masonry_item >a')
                            for item in items.items():
                                data_p = self.common.parse_item(item)
                                data_t = {
                                    'name': name,
                                    'url': data_p.get('brief').get('url'),
                                    'refurl': cate_url
                                }

                                data = dict(data_t, **data_p)
                                yield data
                            self.dbUtils.put_db_url(cate_url)
                    except:
                        continue
                self.log('parsed url %s' % url)
                self.dbUtils.put_db_url(url)
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None

    '''
    urls_genarator
    
    @author: chenzf
    '''

    def urls_genarator(self):
        html = self.utils.get_page(self.url)
        if html:
            a = pq(html)
            categorys = a('div.masonry_item a')
            for category in categorys.items():
                yield category.attr('href'), category.attr('title')
        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('Faponix', '{filePath}'),
        'url': 'https://www.faponix.com/categories/',
        'database': 'Faponix'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
