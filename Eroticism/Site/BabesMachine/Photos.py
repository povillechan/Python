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
        name = item.attr('title')

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
            items = b('#gallery table:nth-of-type(1) a img')
            stills = []
            for still in items.items():
                stills.append(urljoin('https://www.babesmachine.com/', still.attr('src').replace('tn_', '')))

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
        return ""

    def process_data(self, data):
        result = True
        sub_dir_name = self.get_sub_dir_name(data)

        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # galleries
        galleries = data.get('detail').get('galleries')
        if galleries:
            stills = galleries.get('stills')
            if stills:
                for i, subVal in enumerate(stills, start=1):
                    if subVal:
                        self.webParser.utils.verify = False
                        result &= self.webParser.utils.download_file(subVal,
                                                                     os.path.join('%s', 'galleries', '%s', '%s') % (
                                                                         sub_dir_name,
                                                                         self.format_save_name(galleries.get('name')),
                                                                         str(i))
                                                                     )
        return result


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
                a = pq(html)
                # items
                items = a('section.blackback table tr td a')
                parse_succeed = True
                for item in items.items():
                    try:
                        data_p = self.common.parse_item(item)
                        data_t = {
                            'name': "galleries",
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
        for i in range(self.start, self.end + 1, 60):
            yield self.url.format(page=i)
        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('BabesMachine', '{filePath}'),
        'url': 'https://www.babesmachine.com/galleries?from={page}',
        'database': 'BabesMachinePhotos',
        'start': 0,
        'end': 5580
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
