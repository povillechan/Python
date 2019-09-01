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
        url = item.attr('href')
        name = item.text()

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
            # video = b('div.player-container  a.player-container__no-player').attr('href')
            video = b('body > div.main-wrap > div.width-wrap.with-player-container > div.player-container > a').attr(
                'href')
            if video:
                data_detail = {
                    'videos': {
                        'name': item.get('brief').get('name'),
                        'url': item.get('brief').get('url'),
                        'video': video,
                    }
                }
                data = deepcopy(item)
                data['detail'] = data_detail

        return data

    def process_data(self, data):
        result = True
        sub_dir_name = self.get_sub_dir_name(data)

        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # board
        board = data.get('board')
        if board:
            result &= self.webParser.utils.download_file(board,
                                                         os.path.join('%s', '%s') % (sub_dir_name, data.get('name')),
                                                         headers={'Referer': data.get('url')}
                                                         )
        # videos
        videos = data.get('detail').get('videos')
        if videos:
            video = videos.get('video')
            if video:
                if type(video) is list:
                    video = video[0]
                result &= self.webParser.utils.download_file(video,
                                                             os.path.join('%s', 'videos', '%s') % (
                                                                 sub_dir_name, videos.get('name')),
                                                             headers={'Referer': videos.get('url')}
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

            html = self.utils.get_page(url)
            if html:
                if self.dbUtils.get_db_url(url):
                    pass
                else:
                    a = pq(html)
                    items = a(
                        'body > div.main-wrap > div.best-list-block.hide-on-search > div.width-wrap > div.thumb-container div.pornstar-thumb-container div.pornstar-thumb-container__info div.pornstar-thumb-container__info-title a')
                    for item in items.items():
                        model_url_origin = item.attr('href')
                        name = item.text()

                        index = 1
                        while True:
                            model_url = "%s/%s" % (model_url_origin, index)
                            if index == 1:
                                if self.dbUtils.get_db_url(model_url_origin):
                                    index = index + 1
                                    continue
                            elif self.dbUtils.get_db_url(model_url):
                                index = index + 1
                                continue

                            break

                        if index > 2:
                            index = index - 1
                            model_url = "%s/%s" % (model_url_origin, index)
                        else:
                            model_url = model_url_origin

                        while True:
                            self.log('request %s' % model_url)
                            html2 = self.utils.get_page(model_url)
                            if html2:
                                if self.dbUtils.get_db_url(model_url):
                                    pass
                                else:
                                    board = pq(html2)('div.pornstar-logo img').attr('src')
                                    data_ps, parse_res = self.parse_sub_page(html2)
                                    for data_p in data_ps:
                                        data_t = {
                                            'name': name,
                                            'url': model_url,
                                            'board': board,
                                            'refurl': url
                                        }

                                        data = dict(data_t, **data_p)
                                        yield data

                                    if parse_res:
                                        self.log('parsed url %s' % model_url)
                                        self.dbUtils.put_db_url(model_url)

                                next_url = pq(html2)('li.next a').attr("href")
                                if next_url:
                                    model_url = next_url
                                else:
                                    break
                            else:
                                break;
            else:
                self.log('request %s error' % url)
        except:
            self.log('error in parse url %s' % url)
            yield None

        yield None

    def parse_sub_page(self, html):
        b = pq(html)
        items = b(
            'body > div.main-wrap > main > div > article > div.index-videos.mixed-section > div.thumb-list.thumb-list--sidebar.thumb-list--recent > div.thumb-list__item.video-thumb a.video-thumb-info__name')

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
        'savePath': os.path.join('Xhamster', '{filePath}'),
        'url': 'https://xhamster.com/pornstars/{page}',
        'database': 'Xhamster',
        'start': 1,
        'end': 277
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
