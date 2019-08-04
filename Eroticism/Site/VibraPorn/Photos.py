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
        url = item.attr('href')
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

        html = self.webParser.utils.get_page(url)
        if html:
            b = pq(html)
            items = b('#content_center div.gallery_w > a > img ')
            if items:
                stills = []
                for still in items.items():
                    stills.append(urljoin('https://www.vibraporn.com', still.attr("src").replace("/tn_", "/")))

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
        sub_dir_name = ""
        return sub_dir_name


class CWebParserSite(CWebParserMultiUrl):
    def __init__(self, **kwArgs):
        super().__init__(**kwArgs)
        self.utils = CWebSpiderUtils(self.savePath)
        self.utils.verify = False
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
                a = pq(html)
                # items
                items = a('#plugs div.single_plug a')
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

    def urls_genarator(self):
        for i in range(self.start, self.end + 1):
            yield self.url.format(page=i * 30)
        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('VibraPorn', '{filePath}'),
        'url': 'https://www.vibraporn.com/galleries?from={page}',
        'database': 'VibraPorn',
        'start': 0,
        'end': 334
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()