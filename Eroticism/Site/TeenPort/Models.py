# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os
import sys
import re

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

    #
    def parse_item(self, item):
        board = 'http:' + item('img').attr('src')
        result = re.search('url=(.*?)&p', item.attr('href'), re.S)
        product_url = result.group(1)

        data_brief = {
            'url': product_url,
            'board': board,
            'site': "TeenPort",
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
            for index in range(1, 13):
                stills.append("%s/%02d.jpg" % (product_url, index))

            product_name = b('div.title').text().replace(' «', '').replace(b('div.title a').text(), '')
            data_detail = {
                'galleries': {
                    'name': product_name,
                    'url': product_url,
                    'stills': stills,
                    'board': item.get('brief').get('board'),
                    'site': item.get('brief').get('site')
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def get_sub_dir_name(self, data):
        sub_dir_name = os.path.join("%s", "%s") % (data.get('brief').get('site'), data.get('name'))
        return sub_dir_name


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

            html = self.utils.get_page(url, headers={"Accept-Encoding": "", })
            if html:
                a = pq(html)
                # items
                items = a('a.model_item')

                for item in items.items():
                    modelurl = item.attr('href')
                    name = item('img').attr('alt')
                    board = item('img').attr('src')
                    if self.dbUtils.get_db_url(modelurl):
                        continue

                    html = self.utils.get_page(modelurl)
                    if html:
                        b = pq(html)
                        products = b('div.gallery_box a')
                        try:
                            for product in products.items():
                                data_p = self.common.parse_item(product)
                                data_t = {
                                    'name': self.utils.format_name(name),
                                    'url': modelurl,
                                    'board': board,
                                    'refurl': modelurl
                                }

                                data = dict(data_t, **data_p)
                                yield data
                        except:
                            continue
                        self.dbUtils.put_db_url(modelurl)
                self.log('parsed url %s' % url)
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('TeenPort', '{filePath}'),
        'url': 'https://www.teenport.com/girls/',
        'database': 'TeenPort',
        'start': 1
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
