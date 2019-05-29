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

        html = self.webParser.utils.get_page(url)
        if html:
            script_pattern = re.search('jwplayer\("videoplayer"\).setup\((.*?)\)', html, re.S)
            if script_pattern:
                value_json = script_pattern.group(1)
                video = None
                stills = []

                value_parttern = re.search('file:.*?\'(http.*?)\',', value_json, re.S)
                if value_parttern:
                    video = value_parttern.group(1)

                still_pattern = re.search('image:.*?\'(http.*?)\d+\.jpg\',', value_json, re.S)
                if still_pattern:
                    for i in range(1, 30):
                        stills.append('%s%s.jpg' % (still_pattern.group(1), i))

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
        sub_dir_name = ""
        return sub_dir_name


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

                html = self.utils.get_page(url)
                if html:
                    a = pq(html)
                    # items
                    items = a('ul.listThumbs li a.title')
                    parse_succeed = True
                    for item in items.items():
                        try:
                            data_p = self.common.parse_item(item)
                            data_t = {
                                'name': 'videos',
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
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log('error in parse url %s' % url)
                continue

        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('Hubjizz', '{filePath}'),
        'url': 'http://hubjizz.com/page{page}.html',
        'database': 'Hubjizz',
        'start': 1,
        'end': 2076
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
