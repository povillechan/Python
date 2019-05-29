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
        url = item.attr('href')
        name = item.attr('title')

        data_brief = {
            'url': url,
            'name': self.webParser.utils.format_name(name),
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')

        html = self.webParser.utils.get_page(url, headers={'Referer': 'https://www.fukvids.com',
                                                           "User-Agent": "",
                                                           "Accept": "",
                                                           "Accept-Encoding": "",
                                                           "Accept-Language": "",
                                                           "Cache-Control": "",
                                                           'Connection': ''})
        if html:
            b = pq(html)

            video_items = b('#thisPlayer source')
            video = []
            if video_items:
                for items_v in video_items.items():
                    video.append(items_v.attr('src'))

            stills = []
            img_text = b('meta[property="og:image"]').attr('content')
            if img_text:
                img_pattern = re.search('(https.*?-)\d+\.jpg', img_text, re.S)
                if img_pattern:
                    for i in range(1, 10):
                        stills.append('%s%s.jpg' % (img_pattern.group(1), i))

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    'video': video,
                    'stills': stills
                }
            }
            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def get_sub_dir_name(self, data):
        return ""


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

    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True:
            try:
                url = next(urlsGen)
                if url is None:
                    yield None

                if self.dbUtils.get_db_url(url):
                    continue

                html = self.utils.get_page(url, headers={"User-Agent": "",
                                                         "Accept": "",
                                                         "Accept-Encoding": "",
                                                         "Accept-Language": "",
                                                         "Cache-Control": "",
                                                         'Connection': ''})
                if html:
                    a = pq(html)
                    # items
                    items = a('div.inner-box-container > div.row div.item-col.col > div.item-inner-col.inner-col >a')
                    parse_successed = True
                    for item in items.items():
                        data_p = self.common.parse_item(item)
                        if not data_p:
                            parse_successed = False
                            continue

                        data_t = {
                            'url': data_p.get('brief').get('name'),
                            'url': data_p.get('brief').get('url'),
                            'refurl': url
                        }

                        data = dict(data_t, **data_p)
                        yield data
                    if parse_successed:
                        self.dbUtils.put_db_url(url)
                else:
                    self.log('request %s error' % url)
                    continue
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log('error in parse url %s' % url)
                continue

        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('Fukvids', '{filePath}'),
        'url': 'https://www.fukvids.com/page{page}.html',
        'database': 'Fukvids',
        'start': 1,
        'end': 1117
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
