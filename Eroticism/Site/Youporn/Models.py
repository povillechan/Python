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
        product_url = urljoin('https://www.youporn.com/', item.attr('href'))
        product_name = item('img').attr('alt')

        data_brief = {
            'url': product_url,
            'name': self.webParser.utils.format_name(product_name)
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page_by_chrome(url, 'video source', headless=False)

        if html:
            b = BeautifulSoup(html, 'lxml')
            video = b.select_one('video source').get('src')

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    'video': video
                }
            }
            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def process_data(self, data):
        result = True
        sub_dir_name = "%s" % (data.get('name'))

        dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        #         with open(dir_name + '\\info.json', 'w') as f:
        #             json.dump(data, f)

        board = data.get('board')
        if board:
            result &= self.webParser.utils.download_file(board,
                                                         '%s\\%s' % (sub_dir_name, data.get('name'))
                                                         )

        video = data.get('detail').get('videos').get('video')
        if video:
            result &= self.webParser.utils.download_file(video,
                                                         '%s\\%s' % (
                                                         sub_dir_name, data.get('detail').get('videos').get('name')),
                                                         fileType='mp4'
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

    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True:
            try:
                url = next(urlsGen)
                if not url:
                    yield None

                if self.dbUtils.get_db_url(url):
                    continue

                html = self.utils.get_page(url)
                if html:
                    a = pq(html)

                    # items
                    items = a('div.fifteen-column > div > div.three-column > a')
                    parse_url_success = True
                    for item in items.items():
                        model_url = urljoin('https://www.youporn.com/', item.attr('href'))
                        model_name = item('img').attr('alt')
                        model_board = item('img').attr('data-original')

                        while True:
                            model_html = self.utils.get_page(model_url)
                            next_url = None
                            if model_html:

                                if self.dbUtils.get_db_url(model_url):
                                    pass
                                else:
                                    parse_success = True
                                    b = pq(model_html)

                                    video_items = b('div.video-box > a.video-box-image')
                                    for video_item in video_items.items():
                                        try:
                                            #                                             data = self.common.parse_item(video_item)
                                            #
                                            #                                             data['model_url']   = model_url
                                            #                                             data['model_name']  = model_name
                                            #                                             data['model_board'] = model_board
                                            #                                             yield data

                                            data_p = self.common.parse_item(video_item)
                                            data_t = {
                                                'name': self.utils.format_name(model_name),
                                                'url': model_url,
                                                'board': model_board,
                                                'refurl': model_url
                                            }

                                            data = dict(data_t, **data_p)
                                            yield data

                                        except:
                                            parse_url_success = False
                                            parse_success = False
                                            continue

                                    if parse_success:
                                        self.dbUtils.put_db_url(model_url)

                                next_url = b('#next div.prev-next a').attr('href')

                            if not next_url:
                                break
                            else:
                                model_url = urljoin('https://www.youporn.com/', next_url)
                    self.log('parsed url %s' % url)
                    if parse_url_success:
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
        'savePath': 'Youporn\\{filePath}',
        'url': 'https://www.youporn.com/pornstars/?page={page}',
        'database': 'Youporn',
        'start': 1,
        'end': 204
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
