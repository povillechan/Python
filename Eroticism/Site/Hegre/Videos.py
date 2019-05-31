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
        name = item('a').attr('title')
        url = urljoin('http://www.hegre.com/', item('a').attr('href'))

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

            board = b('meta[name="twitter:image"]').attr('content')

            stills = []
            previews = b('.video-stills .board_image a')
            for preview in previews.items():
                stills.append(preview.attr('href'))

            video = b('.resolution.trailer.top-resolution a').attr('href')

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': url,
                    'board': board,
                    'video': video,
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

    '''
    parse_page
    
    @author: chenzf
    '''

    def parse_page(self, url):
        try:
            if url is None:
                yield None

            html = self.utils.get_page(url)
            if html:
                a = pq(html, parser='html')
                # items
                items = a('a.artwork')
                for item in items.items():
                    modelurl = urljoin('http://www.hegre.com/', item.attr('href').strip())
                    board = item('img').attr('src')
                    name = item.attr('title')

                    if self.dbUtils.get_db_url(modelurl):
                        continue

                    bFarseSucceed = True
                    html2 = self.utils.get_page(modelurl)
                    if html2:
                        b = pq(html2, parser='html')
                        item_models = b('#films-wrapper div.item')
                        for item_model in item_models.items():
                            try:
                                data_p = self.common.parse_item(item_model)
                                data_t = {
                                    'name': self.utils.format_name(name),
                                    'url': modelurl,
                                    'board': board,
                                    'refurl': modelurl
                                }

                                data = dict(data_t, **data_p)
                                yield data
                            except:
                                bFarseSucceed = False
                                continue
                        b = pq(html2, parser='html')
                        item_models = b('#massages-wrapper div.item')
                        for item_model in item_models.items():
                            try:
                                data_p = self.common.parse_item(item_model)
                                data_t = {
                                    'name': self.utils.format_name(name),
                                    'url': modelurl,
                                    'board': board,
                                    'refurl': modelurl
                                }

                                data = dict(data_t, **data_p)
                                yield data
                            except:
                                bFarseSucceed = False
                                continue

                        self.log('parsed url %s' % modelurl)
                        if bFarseSucceed:
                            self.dbUtils.put_db_url(modelurl)

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
        'savePath': os.path.join('Hegre', '{filePath}'),
        'url': 'https://www.hegre.com/models',
        'database': 'Hegre'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
