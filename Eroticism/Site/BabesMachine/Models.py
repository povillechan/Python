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
from urllib.parse import urljoin


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    #
    def parse_item(self, item):
        url = urljoin('https://www.babesmachine.com/', item.attr('href'))
        name = item('img').attr('alt')

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
            b = pq(html)

            previews = b('#gallery table:eq(0) tr td a img')
            stills = []
            for preview in previews.items():
                stills.append(('https:' + preview.attr('src')).replace('/tn_', '/'))

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


class CWebParserSite(CWebParserSingleUrl):
    def __init__(self, **kwArgs):
        super().__init__(**kwArgs)
        self.utils = CWebSpiderUtils(self.savePath)
        self.common = CWebParserSiteCommon(self)
        self.dbUtils = CWebDataDbUtis(kwArgs.get('database'))
        self.utils.verify = False

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

                html = self.utils.get_page(url)
                if html:
                    a = pq(html)
                    # items
                    items = a('#models tr td a')
                    for item in items.items():
                        name = item.attr('title')
                        model_url = urljoin('https://www.babesmachine.com', item.attr('href'))

                        if self.dbUtils.get_db_url(model_url):
                            continue

                        html2 = self.utils.get_page(model_url)
                        if html2:
                            b = pq(html2)
                            modelitems = b('#posts tr td a')
                            parse_succeed = True
                            for modelitem in modelitems.items():
                                try:
                                    data_p = self.common.parse_item(modelitem)
                                    data_t = {
                                        'name': self.utils.format_name(name),
                                        'url': model_url,
                                        'refurl': url
                                    }

                                    data = dict(data_t, **data_p)
                                    yield data
                                except:
                                    parse_succeed = False
                                    continue

                            if parse_succeed:
                                self.log('parsed url %s' % model_url)
                                self.dbUtils.put_db_url(model_url)
                        else:
                            self.log('request %s error' % model_url)
                            continue
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
    for url in range(ord("A"), ord("Z") + 1):
        para_args = {
            'savePath': os.path.join('BabesMachine', '{filePath}'),
            'url': "https://www.babesmachine.com/model/?letter=%s" % chr(url),
            'database': 'BabesMachine'
        }

        job = CWebParserSite(**para_args)
        job.call_process()


if __name__ == '__main__':
    job_start()
