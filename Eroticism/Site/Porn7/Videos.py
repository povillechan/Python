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


class CWebParserSiteCommon(CWebParserProcess):
    def __init__(self, webParser):
        super().__init__(webParser)

    #
    def parse_item(self, item):
        url = item.attr('href')
        name = item.attr('title')

        data_brief = {
            'name': name,
            'url': url
        }

        data = {'brief': data_brief}

        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page_by_chrome(url, 'video', headless=False)

        if html:
            b = BeautifulSoup(html, 'lxml')

            video = b.select_one('video.fp-engine').get('src')

            board = None
            board_url = re.search('preview_url: \'(https.*?)\'', html, re.S)
            if board_url:
                board = board_url.group(1)

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': url,
                    'board': board,
                    'video': video,
                    'stills': [],
                }
            }

            data = deepcopy(item)
            data['detail'] = data_detail
        return data

    def process_data(self, data):
        result = True
        sub_dir_name = ""

        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        board = data.get('detail').get('videos').get('board')
        if board:
            result &= self.webParser.utils.download_file(board,
                                                         self.format_save_name(
                                                             data.get('detail').get('videos').get('name')),
                                                         headers={
                                                             'Referer': data.get('detail').get('videos').get('url')}
                                                         )

        video = data.get('detail').get('videos').get('video')
        if video:
            result &= self.webParser.utils.download_file(video,
                                                         self.format_save_name(
                                                             data.get('detail').get('videos').get('name')),
                                                         fileType='mp4',
                                                         headers={
                                                             'Referer': data.get('detail').get('videos').get('url')}
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
            if not url:
                yield None

            if self.dbUtils.get_db_url(url):
                yield None

            html = self.utils.get_page(url)
            if html:
                a = pq(html)
                # items
                items = a('#list_videos_common_videos_list_items > div > a')

                for item in items.items():
                    data_p = self.common.parse_item(item)
                    data_t = {
                        'name': data_p.get('brief').get('name'),
                        'url': data_p.get('brief').get('url'),
                        'refurl': url
                    }

                    data = dict(data_t, **data_p)
                    yield data
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
        'savePath': os.path.join('Porn7', '{filePath}'),
        'url': 'https://www.porn7.xxx/rated/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=rating&from={page}',
        'database': 'Porn7',
        'start': 0,
        'end': 222
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
