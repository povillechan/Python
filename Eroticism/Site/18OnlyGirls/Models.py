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
from pyquery import PyQuery as pq
from copy import deepcopy


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    #
    def parse_item(self, item):
        board = item('img').attr('src')
        product_url = item('a').attr('href')
        product_name = item('a').attr('title')
        data_brief = {
            'board': board,
            'url': product_url,
            'name': self.webParser.utils.format_name(product_name)
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page(url, headers={"Accept-Encoding": "", })

        if html:
            b = pq(html)

            video = None
            video_item = b('video source')
            if video_item:
                video = video_item.attr('src')

            stills = []
            previews = b('div.ngg-gallery-thumbnail')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))

            if video:
                data_detail = {
                    'videos': {
                        'name': self.webParser.utils.format_name(item.get('brief').get('name')),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'video': video,
                        'stills': stills,
                    }
                }
            else:
                data_detail = {
                    'galleries': {
                        'name': self.webParser.utils.format_name(item.get('brief').get('name')),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
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
                    items = a('ul.links li')

                    for item in items.items():
                        modelurl = item('a').attr('href')
                        name = item('a').attr('title')

                        if self.dbUtils.get_db_url(modelurl):
                            continue

                        html = self.utils.get_page(modelurl, headers={"Accept-Encoding": "", })
                        if html:
                            b = pq(html)
                            products = b('li.box-shadow')
                            try:
                                for product in products.items():
                                    data_p = self.common.parse_item(product)
                                    data_t = {
                                        'name': self.utils.format_name(name),
                                        'url': modelurl,
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
                continue

        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('18OnlyGirls', '{filePath}'),
        'url': 'https://www.18onlygirlsblog.com/models-list/',
        'database': '18OnlyGirls'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
