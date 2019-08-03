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
        url = urljoin('http://godsartnudes.com/', item.attr('href'))
        name = item('img').attr("title")

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

            previews = b('div.container-fluid div.col-xxs-12.col-xs-6.col-sm-6.col-md-4.gallery-thumb img')
            stills = []
            for preview in previews.items():
                stills.append(preview.attr('src').replace("thumb", "big"))

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

            html = self.utils.get_page(url, headers={"Host": "godsartnudes.com",
                                                     "Upgrade-Insecure-Requests": "1"})
            if html:
                a = pq(html)
                # items
                items = a(
                    'div.row.gan-central div.col-xxs-12.col-xs-6.col-sm-4.col-md-3 div.Thumb a:last-of-type')
                for item in items.items():
                    name = item.text()
                    # board = item('a img').attr('lsrc') + '.jpg'
                    model_url = urljoin('http://godsartnudes.com', item.attr('href'))

                    if self.dbUtils.get_db_url(model_url):
                        continue

                    html2 = self.utils.get_page(model_url)
                    if html2:
                        b = pq(html2)
                        modelitems = b(
                            'div.row.spacetop div.col-xxs-12.col-xs-6.col-sm-4.col-md-3 div.thumbImage > a:first-child')
                        parse_succeed = True
                        processNum = 0
                        for modelitem in modelitems.items():
                            parse_succeed &= True
                            try:
                                data_p = self.common.parse_item(modelitem)
                                data_t = {
                                    'name': name,
                                    'url': model_url,
                                    'refurl': url
                                }

                                data = dict(data_t, **data_p)
                                yield data
                                processNum += 1
                            except:
                                parse_succeed = False
                                continue

                        if parse_succeed and processNum > 0:
                            self.log('parsed url %s' % model_url)
                            self.dbUtils.put_db_url(model_url)
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None

    def urls_genarator(self):
        for url in range(ord("A"), ord("Z") + 1):
            yield self.url.format(page=chr(url))
        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('GodArtNudes', '{filePath}'),
        'url': "http://godsartnudes.com/models-listing/letter-{page}",
        'database': 'GodArtNudes'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
