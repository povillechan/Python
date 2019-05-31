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
        url = item('a').attr('href')
        model = item('span').text().replace(item('span span').text(), '')
        board = item('img').attr('src')
        productName = item('a').attr('title')

        data_brief = {
            'name': model,
            'url': url,
            'board': board,
            'productName': productName,
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page(url)

        if html:
            b = pq(html)
            board = None
            video = None
            video_item = b('video source')
            if video_item.items(0):
                video = video_item.attr('src')
                board = b('video').attr('poster')

            stills = []
            previews = b('ul.gallery-e li')
            for preview in previews.items():
                stills.append(preview('a').attr('href'))

            if video:
                data_detail = {
                    'videos': {
                        'name': item.get('brief').get('productName'),
                        'url': item.get('brief').get('url'),
                        'board': board,
                        'video': video,
                        'stills': stills,
                    }
                }
            else:
                data_detail = {
                    'galleries': {
                        'name': item.get('brief').get('productName'),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
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
                items = a('ul.gallery-d li')

                for item in items.items():
                    data_p = self.common.parse_item(item)
                    data_t = {
                        'name':  data_p.get('brief').get('name'),
                        'url':   data_p.get('brief').get('url'),
                        'board': data_p.get('brief').get('board'),
                        'refurl': url
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
        'savePath': os.path.join('BabeHub', '{filePath}'),
        'url': 'https://www.babehub.com/page/{page}/',
        'database': 'BabeHub',
        'start': 0,
        'end': 146
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
