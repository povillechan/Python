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
        url = item('a').attr('href')
        name = item('a').attr('title')
        still = item('img').attr('src')
        stills = []
        result = re.search('(https.*?/)\d.jpg', still, re.S).group(1)

        for i in range(1, 6):
            stills.append(
                result + str(i) + '.jpg'
            )

        data_brief = {
            'name': self.webParser.utils.format_name(name),
            'url': url,
            'stills': stills,
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None

        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page_by_chrome(url, 'video.fp-engine', headless=False)
        if html:
            b = BeautifulSoup(html, 'lxml')

            video = b.select_one('video.fp-engine').get('src')

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    'video': video,
                    'stills': item.get('brief').get('stills'),
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail
        return data


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
                    items = a('span.model_items')

                    for item in items.items():
                        modelurlText = item.attr('onclick')
                        modelurl = re.search('\'(http.*?)\'', modelurlText, re.S).group(1)
                        model = item.attr('title')

                        html2 = self.utils.get_page(modelurl)
                        if html2:
                            b = pq(html2)
                            items_model = b('div.content div.item')
                            for item_model in items_model.items():
                                data_p = self.common.parse_item(item_model)
                                data_t = {
                                    'name': model,
                                    'url': modelurl,
                                    'refurl': url
                                }

                                data = dict(data_t, **data_p)
                                yield data
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
        'savePath': os.path.join('WatchMyGF', '{filePath}'),
        'url': 'https://watch-my-gf.com/girls.html?mode=async&function=get_block&block_id=list_models_models_list&section=&sort_by=avg_videos_popularity&from={page}/',
        'database': 'WatchMyGF',
        'start': 1,
        'end': 34
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
