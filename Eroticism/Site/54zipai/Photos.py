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
from urllib.parse import urljoin


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    #
    def parse_item(self, item):
        url = urljoin('https://54zipai.com/', item.attr('href'))
        name = item('img').attr('alt')

        data_brief = {
            'url': url,
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

        html = self.webParser.utils.get_page_raw(url)
        if html:
            b = pq(html)
            items = b('div.content_left img')
            stills = []
            for still in items.items():
                stills.append(urljoin('https://54zipai.com/', still.attr("src")))

            data_detail = {
                'galleries': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    'stills': stills
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

class CWebParserSite(CWebParserMultiUrl):
    def __init__(self, **kwArgs):
        super().__init__(**kwArgs)
        self.utils = CWebSpiderUtils(self.savePath)
        # self.utils.verify = False
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

            html = self.utils.get_page_raw(url)
            if html:
                a = pq(html)
                # items
                items = a('li.i_list.list_n2 > a')
                parse_succeed = True
                icount = 0
                for item in items.items():
                    try:
                        data_p = self.common.parse_item(item)
                        data_t = {
                            'name': data_p.get('brief').get('name'),
                            'url': data_p.get('brief').get('url'),
                            'refurl': url
                        }

                        data = dict(data_t, **data_p)
                        yield data
                        icount += 1
                    except:
                        parse_succeed = False
                        continue
                if parse_succeed and icount > 0:
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
        'savePath': os.path.join('54zipai', '{filePath}'),
        'url': 'https://54zipai.com/index_{page}.html',
        'database': '54zipai',
        'start': 1,
        'end': 40
    }

    job = CWebParserSite(**para_args)
    job.call_process()

    para_args = {
        'savePath': os.path.join('54zipai', '{filePath}'),
        'url': 'https://54zipai.com/selfies/index_{page}.html',
        'database': '54zipai',
        'start': 1,
        'end': 779
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
