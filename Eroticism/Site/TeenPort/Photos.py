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

    #
    def parse_item(self, item):
        board = item('img').attr('src')
        product_url = item.attr('href')
        product_name = item.text()

        data_brief = {
            'url': product_url,
            'board': board,
            'name': self.webParser.utils.format_name(product_name)
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

            data_detail = {
                'galleries': {
                    'name': item.get('brief').get('name'),
                    'url': product_url,
                    'stills': stills,
                    'board': item.get('brief').get('board'),
                    'site': b('div.title a:last-child').attr('title')
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def get_sub_dir_name(self, data):
        sub_dir_name = os.path.join("%s", "%s") % (data.get('detail').get('galleries').get('site'), data.get('name'))
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

    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True:
            try:
                url = next(urlsGen)
                if not url:
                    yield None

                html = self.utils.get_page(url, headers={"Accept-Encoding": "", })
                if html:
                    a = pq(html)
                    # items
                    items = a('a.list_model')

                    for item in items.items():
                        modelurl = item.attr('href')
                        name = item('b').text()
                        board = item('img').attr('src')

                        if self.dbUtils.get_db_url(modelurl):
                            continue

                        html = self.utils.get_page(modelurl)
                        if html:
                            b = pq(html)
                            products = b('a.list_model2')
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
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log('error in parse url %s' % url)
                yield None

        yield None


def job_start():
    print(__file__, "start!")

    job_list = [
        ('S', 'http://www.teenport.com/galleries/teen-mega-world'),
        ('S', 'http://www.teenport.com/galleries/x-art'),
        ('S', 'http://www.teenport.com/galleries/anal-angels'),
        ('S', 'http://www.teenport.com/galleries/tricky-masseur'),
        ('S', 'http://www.teenport.com/galleries/watch-me-fucked'),
        ('S', 'http://www.teenport.com/galleries/first-bgg'),
        ('S', 'http://www.teenport.com/galleries/cream-pie-angels'),
        ('S', 'http://www.teenport.com/galleries/18-stream'),
        ('S', 'http://www.teenport.com/galleries/nubiles/'),
        ('S', 'http://www.teenport.com/galleries/club-seventeen/'),
    ]

    for job_item in job_list:
        para_args = {
            'savePath': os.path.join('TeenPort', '{filePath}'),
            'url': job_item[1],
            'database': 'TeenPort'
        }

        job = CWebParserSite(**para_args)
        job.call_process()


if __name__ == '__main__':
    job_start()
