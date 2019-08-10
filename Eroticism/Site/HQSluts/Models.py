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
        url = urljoin('https://www.hqsluts.com/', item('a:nth-child(2)').attr('href'))
        name = item('b span').text()
        if not name:
            name = item('a:nth-child(2)').attr('href').split('/')[1]

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

            previews = b('ul.set.gallery li.item.i a')
            stills = []
            for preview in previews.items():
                stills.append(preview.attr('href'))

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
            if url is None:
                yield None

            while True:
                html = self.utils.get_page(url)
                if html:
                    if self.dbUtils.get_db_url(url):
                        pass
                    else:
                        a = pq(html)
                        # items
                        items = a('ul.set.sluts_main li')
                        parse_succeed = True
                        for item in items.items():
                            try:
                                name = item('b a').text()
                                board = item('a img').attr('lsrc') + '.jpg'
                                model_url = urljoin('https://www.hqsluts.com/', item('b a').attr('href'))

                                html2 = self.utils.get_page(model_url)
                                if html2:
                                    b = pq(html2)
                                    modelitems = b('ul.set.slut li')
                                    for modelitem in modelitems.items():
                                        try:
                                            data_p = self.common.parse_item(modelitem)
                                            data_t = {
                                                'name': self.utils.format_name(name),
                                                'url': model_url,
                                                'board': board,
                                                'refurl': url
                                            }

                                            data = dict(data_t, **data_p)
                                            yield data
                                        except:
                                            parse_succeed = False
                                            continue
                            except:
                                parse_succeed = False
                                continue
                        if parse_succeed:
                            self.log('parsed url %s' % url)
                            self.dbUtils.put_db_url(url)

                    next_url = a('#pages li a[count="Next Page"]')
                    if next_url:
                        url = urljoin('https://www.hqsluts.com/', next_url.attr('href'))
                        self.log('request %s' % url)
                    else:
                        break
                else:
                    self.log('request %s error' % url)
                    continue
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None


def job_start():
    for url in range(ord("A"), ord("Z") + 1):
        para_args = {
            'savePath': os.path.join('HQSluts', '{filePath}'),
            'url': "https://www.hqsluts.com/sluts/%s/" % chr(url),
            'database': 'HQSluts'
        }

        job = CWebParserSite(**para_args)
        job.call_process()


if __name__ == '__main__':
    job_start()
