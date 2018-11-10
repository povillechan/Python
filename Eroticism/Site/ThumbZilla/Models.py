# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os, sys, re, json, collections

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
        data = None

        url = urljoin('https://www.thumbzilla.com/', item.attr('href'))
        name = item('span.info span.title').text()

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

            video = b('ul.filterMenu li:last-of-type a')
            if video:
                video = video.attr('data-quality')

            stills = []
            img_text = b('img.mainImage').attr('src')
            if img_text:
                img_pattern = re.search('(https.*?\))\d+\.jpg', img_text, re.S)
                if img_pattern:
                    for i in range(1, 17):
                        stills.append('%s%s.jpg'%(img_pattern.group(1),i) )

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

                html = self.utils.get_page(url)
                if html:
                    if self.dbUtils.get_db_url(url):
                        pass
                    else:
                        a = pq(html)
                        # items
                        items = a('#content > ul  li.pornstars a')
                        for item in items.items():
                            name = item('a img').attr('alt')
                            board = item('a img').attr('src')
                            model_url = urljoin('https://www.thumbzilla.com/', item.attr('href'))

                            while True:
                                html2 = self.utils.get_page(model_url)
                                if html2:
                                    if self.dbUtils.get_db_url(model_url):
                                        pass
                                    else:
                                        data_ps, parse_res = self.parse_sub_page(html2)
                                        for data_p in data_ps:
                                            data_t = {
                                                'name': self.utils.format_name(name),
                                                'url': model_url,
                                                'board': board,
                                                'refurl': url
                                            }

                                            data = dict(data_t, **data_p)
                                            yield data

                                        if parse_res:
                                            self.log('parsed url %s' % model_url)
                                            self.dbUtils.put_db_url(model_url)

                                    next_url = pq(html2)('li.page_next a')
                                    if next_url:
                                        model_url = urljoin('https://www.thumbzilla.com', next_url.attr('href'))
                                        self.log('request %s' % model_url)
                                    else:
                                        break
                else:
                    self.log('request %s error' % url)
                    continue
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log('error in parse url %s' % url)
                continue

        yield None

    def parse_sub_page(self, html):
        b = pq(html)
        items = b('#content ul li:gt(4) a')

        sub_datas = []
        parse_successed = None
        for item in items.items():
            try:
                data_p = self.common.parse_item(item)
                sub_datas.append(data_p)

                if not parse_successed:
                    parse_successed = True
                else:
                    parse_successed = True & parse_successed
            except:
                parse_successed = False

        return sub_datas, parse_successed


def job_start():
    para_args = {
        'savePath': 'ThumbZilla\\{filePath}',
        'url': 'https://www.thumbzilla.com/pornstars?page={page}',
        'database': 'ThumbZilla',
        'start': 1,
        'end': 275
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
