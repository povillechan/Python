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
        modelurl = urljoin('https://au.fleshlight.com/', item('a.permacover').attr('href'))
        name = item('a.permacover .v-bottom h3').text()
        board_str = re.search('url\(\'(.*?)\'', item('.grid-image').attr('style'))
        board = urljoin('https://', board_str.group(1))

        data_brief = {
            # 'board': board,
            'url': modelurl,
            'name': name
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

            stills = []

            meta_imgs = b('meta[property="og:image"]')
            for meta in meta_imgs.items():
                stills.append(meta.attr('content'))

            board_str = re.search('url\(\'(.*?)\'', b('.main-product-container--pornstar').attr('style'))
            if board_str and len(board_str.group(1)) > 0:
                board = urljoin('https://', board_str.group(1))
                stills.append(board)

            if b('#combos'):
                board_str = re.search('url\(\'(.*?)\'', b('#combos').attr('style'))
                if board_str and len(board_str.group(1)) > 0:
                    board = urljoin('https://', board_str.group(1))
                    stills.append(board)

            if b('.girl-stats .girl-stats-image span'):
                board_str = re.search('url\(\'(.*?)\'', b('.girl-stats .girl-stats-image span').attr('style'))
                if board_str and len(board_str.group(1)) > 0:
                    board = urljoin('https://', board_str.group(1))
                    stills.append(board)

            data_detail = {
                'galleries': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    # 'board': item.get('brief').get('board'),
                    'stills': stills,
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail
        return data

    def get_sub_dir_name(self, data):
        sub_dir_name = ""
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

            if self.dbUtils.get_db_url(url):
                yield None

            html = self.utils.get_page(url)
            if html:
                a = pq(html)
                # items
                items = a('.products .contain .grid .col-sm-12')
                parse_succeed = True
                for item in items.items():
                    try:
                        data_p = self.common.parse_item(item)
                        data_t = {
                            'name': data_p.get('brief').get('name'),
                            'url': data_p.get('brief').get('url'),
                            # 'board': data_p.get('brief').get('board'),
                            'refurl': url
                        }

                        data = dict(data_t, **data_p)
                        yield data
                    except:
                        parse_succeed = False
                        continue
                if parse_succeed:
                    self.dbUtils.put_db_url(url)
            else:
                self.log('html none in parse url %s' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None


def job_start():
    job_list = [
        {
            'savePath': os.path.join('FleshlightGirls', '{filePath}'),
            'url': 'https://au.fleshlight.com/collections/fleshlight-girls/',
            'database': 'FleshlightGirls'
        },
        {
            'savePath': os.path.join('FleshlightGirls', '{filePath}'),
            'url': 'https://au.fleshlight.com/collections/legends',
            'database': 'FleshlightGirls'
        },
        {
            'savePath': os.path.join('FleshlightGirls', '{filePath}'),
            'url': 'https://au.fleshlight.com/collections/dorcel-girls',
            'database': 'FleshlightGirls'
        },
        {
            'savePath': os.path.join('FleshlightGirls', '{filePath}'),
            'url': 'https://au.fleshlight.com/collections/camstars',
            'database': 'FleshlightGirls'
        }
    ]

    for job_item in job_list:
        job = CWebParserSite(**job_item)
        job.call_process()


if __name__ == '__main__':
    job_start()
