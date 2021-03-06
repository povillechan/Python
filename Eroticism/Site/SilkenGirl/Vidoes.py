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
        url = urljoin('https://www.silkengirl.net', item.attr('href'))
        name = item.attr('title')

        data_brief = {
            'url': url,
            'name': name,
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

            video = urljoin('https://www.silkengirl.net', b('#my-video source').attr('src'))

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    'video': video
                }
            }
            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def get_sub_dir_name(self, data):
        return ""

    @staticmethod
    def get_gallery_dir():
        return ''

    def get_video_file_path(self, videos):
        return ''


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

            if self.dbUtils.get_db_url(url) is not None:
                yield None

            html = self.utils.get_page(url)
            if html:
                a = pq(html)
                # items
                items = a('div.thumb.thumb2025 a')
                parse_succeed = True
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
                    except:
                        parse_succeed = False
                        continue
                if parse_succeed:
                    self.log('parsed url %s' % url)
                    self.dbUtils.put_db_url(url)
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None

    def urls_genarator(self):
        for i in range(self.start, self.end + 1):
            yield self.url.format(page=i * 40)
        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('SilkenGirl', '{filePath}'),
        'url': 'https://www.silkengirl.net/videos/?from={page}',
        'database': 'SilkenGirlVideo',
        'start': 0,
        'end': 21
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
