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
        name = item('.grid-meta a').text()
        product = urljoin('http://www.hegregirls.com/', item('.grid-meta a').attr('href'))

        url = None
        if item('.preview-link a'):
            url = urljoin('http://www.hegregirls.com/', item('.preview-link a').attr('href'))

        board = item('.field-type-image a').attr('rel')

        data_brief = {
            'url': url,
            'name': name,
            'product': product,
            'board': board
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')

        if url:
            html = self.webParser.utils.get_page(url)
            if html:
                b = pq(html)

                stills = []
                stills.append(b('#preview-board img').attr('src'))

                previews = b('.content .content .grid-24.bottom-border-solid .grid-4 a')
                for preview in previews.items():
                    stills.append(preview.attr('href'))

                cover = b('.content .grid-24.alpha.omega .grid-12.alpha img')
                if cover:
                    stills.append(cover.attr('src'))

                data_detail = {
                    'galleries': {
                        'name': item.get('brief').get('name'),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'stills': stills
                    }
                }
                data = deepcopy(item)
                data['detail'] = data_detail
        else:
            url = item.get('brief').get('product')

            html = self.webParser.utils.get_page(url)
            if html:
                b = pq(html)

                stills = []
                stills.append(
                    b('div.content > div.grid-20.alpha.omega > div.grid-20.board.alpha.omega > a > img').attr('src'))

                data_detail = {
                    'galleries': {
                        'name': item.get('brief').get('name'),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'stills': stills
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
            if url is None:
                yield None

            if self.dbUtils.get_db_url(url):
                yield None

            html = self.utils.get_page(url)
            if html:
                a = pq(html, parser='html')
                # items
                items = a('#block-system-main .node-grid')

                for item in items.items():
                    board = item('div.field-type-image img').attr('src')
                    name = item('.grid-meta a').text()
                    modelurl = urljoin('http://www.hegregirls.com/', item('.grid-meta a').attr('href'))

                    html2 = self.utils.get_page(modelurl)
                    if html2:
                        b = pq(html2, parser='html')
                        items_model = b('#main-content .content .content .grid-4')
                        for item_model in items_model.items():
                            try:
                                if not re.search('galleries', item_model.attr('about')):
                                    continue

                                data_p = self.common.parse_item(item_model)
                                data_t = {
                                    'name': name,
                                    'url': modelurl,
                                    'board': board,
                                    'refurl': url
                                }

                                data = dict(data_t, **data_p)
                                yield data
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


def job_start():
    para_args = {
        'savePath': os.path.join('Hegre', '{filePath}'),
        'url': 'http://hegregirls.com/models?page={page}',
        'database': 'Hegre',
        'start': 0,
        'end': 4
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
