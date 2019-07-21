# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

from Common.CWebParser import CParseType, CWebParser, CWebParserMultiUrl, CWebParserSingleUrl
from Common.CWebDataDbUtis import CWebDataDbUtis
from Common.CWebSpiderUtils import CWebSpiderUtils
from Common.CWebParserProcess import CWebParserProcess
from copy import deepcopy
from pyquery import PyQuery as pq


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    def parse_item(self, item):
        product_url = item.attr('href')
        data_brief = {
            'url': product_url,
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

            previews = b('dt.gallery-icon a')
            stills = []
            for preview in previews.items():
                stills.append(preview.attr('href'))

            product_name = b('h1.single_title').text()
            data_detail = {
                'galleries': {
                    'name': product_name,
                    'url': product_url,
                    'stills': stills,
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail
        return data


class CWebParserSite(CWebParserMultiUrl):
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

            html = self.utils.get_page(url)
            if html:
                a = pq(html)
                # items
                items = a('div.ts-responsive-wrap div.tshowcase-inner-box div.tshowcase-box-photo > a')

                for item in items.items():
                    modelurl = item.attr('href')
                    name = item('img').attr('title')
                    board = item('img').attr('src')

                    html = self.utils.get_page(modelurl)
                    if html:
                        b = pq(html)
                        products = b('div.home_tall_box > a')
                        for product in products.items():
                            data_p = self.common.parse_item(product)
                            data_t = {
                                'name': name,
                                'url': modelurl,
                                'board': board,
                                'refurl': modelurl
                            }

                            data = dict(data_t, **data_p)
                            yield data

                self.log('parsed url %s' % url)
                self.dbUtils.put_db_url(url)
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('Erocurves', '{filePath}'),
        'url': 'https://www.erocurves.com/model-archives/?tpage={page}',
        'database': 'Erocurves',
        'start': 1,
        'end': 72
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
