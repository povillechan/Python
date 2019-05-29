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
        url = urljoin('https://www.erosberry.com/', item.attr('href'))
        name = item('img').attr('alt')

        data_brief = {
            'url': url,
            'name': self.webParser.utils.format_name(name)
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
            items = b('#photo div.form_comment').prev_all('div.container a img')
            if items:
                stills = []
                for still in items.items():
                    stills.append(urljoin('https://www.erosberry.com/', still.attr("src").replace("/tn_", "/")))

                data_detail = {
                    'galleries': {
                        'name': item.get('brief').get('name'),
                        'url': item.get('brief').get('url'),
                        'stills': stills
                    }
                }
            else:
                video = b('source[type="video/mp4"]')
                if video:
                    data_detail = {
                        'videos': {
                            'name': item.get('brief').get('name'),
                            'url': item.get('brief').get('url'),
                            'video': urljoin('https://www.erosberry.com/', video.attr('src'))
                        }
                    }
                else:
                    video = b('source[type="video/flv"]')
                    if video:
                        data_detail = {
                            'videos': {
                                'name': item.get('brief').get('name'),
                                'url': item.get('brief').get('url'),
                                'video': urljoin('https://www.erosberry.com/', video.attr('src'))
                            }
                        }
            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def process_data(self, data):
        #         print(data)
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

            # galleries
        galleries = data.get('detail').get('galleries')
        if galleries:
            board = galleries.get('board')
            if board:
                result &= self.webParser.utils.download_file(board,
                                                             os.path.join('%s', 'galleries', '%s', '%s') % (
                                                                 sub_dir_name, galleries.get('name'),
                                                                 galleries.get('name')),
                                                             headers={'Referer': galleries.get('url')}
                                                             )

            stills = galleries.get('stills')
            if stills:
                for i, subVal in enumerate(stills, start=1):
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                                                     os.path.join('%s', 'galleries', '%s', '%s') % (
                                                                         sub_dir_name, galleries.get('name'), str(i)),
                                                                     headers={'Referer': galleries.get('url')}
                                                                     )

                        # videos
        videos = data.get('detail').get('videos')
        if videos:
            board = videos.get('board')
            if board:
                result &= self.webParser.utils.download_file(board,
                                                             os.path.join('%s', 'videos', '%s', '%s') % (
                                                                 sub_dir_name, videos.get('name'), videos.get('name')),
                                                             headers={'Referer': videos.get('url')}
                                                             )

            stills = videos.get('stills')
            if stills:
                for i, subVal in enumerate(stills, start=1):
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                                                     os.path.join('%s', 'videos', '%s', '%s') % (
                                                                         sub_dir_name, videos.get('name'), str(i)),
                                                                     headers={'Referer': videos.get('url')}
                                                                     )

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
        self.utils.verify = False
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
                    pass

                html = self.utils.get_page(url)
                if html:
                    a = pq(html)
                    # items
                    items = a('div.thumbs div.thumb > a')
                    processNum = 0
                    parse_succeed = True
                    for item in items.items():
                        try:
                            name = item.text()
                            model_url = urljoin('https://www.erosberry.com/', item.attr('href'))

                            html2 = self.utils.get_page(model_url)
                            if html2:
                                b = pq(html2)
                                board = urljoin('https://www.erosberry.com/', b('div.info > img').attr('src'))
                                modelitems = b('div.girl_thumbs div.container > a')
                                for modelitem in modelitems.items():
                                    try:
                                        data_p = self.common.parse_item(modelitem)
                                        data_t = {
                                            'name': self.utils.format_name(name),
                                            'url': model_url,
                                            'board': board,
                                            'refurl': url
                                        }

                                        data = dict(data_t, **data_p)
                                        yield data
                                        processNum += 1
                                    except:
                                        parse_succeed = False
                                        continue
                        except:
                            parse_succeed = False
                            continue
                    if parse_succeed and processNum > 0:
                        self.log('parsed url %s' % url)
                        self.dbUtils.put_db_url(url)
                else:
                    self.log('request %s error' % url)
                    continue
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log('error in parse url %s' % url)
                continue

        yield None

    def urls_genarator(self):
        for i in range(self.start, self.end + 1):
            yield self.url.format(page=i * 44)
        yield None


def job_start():
    para_args = {
        'savePath': os.path.join('ErosBerry', '{filePath}'),
        'url': 'https://www.erosberry.com/models?from={page}',
        'database': 'ErosBerry',
        'start': 0,
        'end': 36
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
