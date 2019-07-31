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
from urllib.parse import urljoin


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    #
    def parse_item(self, item):
        board = item('img').attr('src')
        url = item('a').attr('href')
        result = re.search('.*?(\?\d+x\d+x\d+)', item('a').attr('href'))
        if result:
            url = url.replace(result.group(1), '')

        url = urljoin('http://www.hotxart.com/', url)
        name = item('img').attr('alt')

        data_brief = {
            'url': url,
            'name': name,
            'board': board
        }

        data = {'brief': data_brief}

        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('url')
        html = self.webParser.utils.get_page(url, headers={'Referer': 'http://www.hotxart.com/'})

        if html:
            b = pq(html)

            photos = b('body table:nth-child(2) table td>a')
            stills = []
            for photo in photos.items():
                detail_url = urljoin('http://www.hotxart.com/', photo.attr('href'))
                detail_html = self.webParser.utils.get_page(detail_url)
                large = None
                if detail_html:
                    c = pq(detail_html)
                    large = c('span.galprov img').attr('src')

                stills.append(large)

            if len(stills) > 0:
                data_detail = {
                    'galleries': {
                        'name': item.get('brief').get('name'),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'stills': stills,
                    }
                }

                data = deepcopy(item)
                data['detail'] = data_detail

        return data

    def get_sub_dir_name(self, data):
        return ''

    @staticmethod
    def get_gallery_dir():
        return ''


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

            html = self.utils.get_page(url)
            if html:
                a = pq(html)
                # items
                items = a('ul.picmain li')
                for item in items.items():
                    data_p = self.common.parse_item(item)
                    data_t = {
                        'name': "HotXArt",
                        'url': data_p.get('brief').get('url'),
                        'refurl': url
                    }

                    data = dict(data_t, **data_p)
                    yield data

                self.log('parsed url %s' % url)
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('HotXArt', '{filePath}'),
        'url': 'http://www.hotxart.com/',
        'database': 'HotXArt',
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
