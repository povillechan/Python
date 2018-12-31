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

        url = urljoin('https://www.youporn.com/', item.attr('href'))
        name = item('div.video-box-title').text()

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

            video = b('#downloadModal  .modal-box-content .downloadVideoLink')
            videos = []
            if video:
                for video_item in video.items():
                    videos.append(video_item.attr('href'))

            stills = []
            img_text = b('meta[property="og:image"]').attr('content')
            if img_text:
                img_pattern = re.search('(https.*?original/)\d+(/.*?-)\d+\.jpg', img_text, re.S)
                if img_pattern:
                    for i in range(1, 17):
                        stills.append('%s%s%s%s.jpg'%(img_pattern.group(1), i, img_pattern.group(2), i))

            data_detail = {
                'videos': {
                    'name': item.get('brief').get('name'),
                    'url': item.get('brief').get('url'),
                    'video': videos,
                    'stills': stills
                }
            }
            data = deepcopy(item)
            data['detail'] = data_detail

        return data

    def parse_detail_fr_brief_duplicate(self, item):
        url = item.get('brief').get('url')
        html = self.webParser.utils.get_page(url)
        if html:
            b = pq(html)
            if b('a.pornstar-name'):
                return True
            else:
                return False
        else:
            return True


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

    def parse_page(self):
        urlsGen = self.urls_genarator()
        while True:
            try:
                url = next(urlsGen)
                if not url:
                    yield None
                    break

                url_origin = url
                index = 1
                while True:
                    search_url = "%s?page=%s" % (url_origin, index)
                    if index == 1:
                        if self.dbUtils.get_db_url(url_origin):
                            index = index + 1
                            continue
                    elif self.dbUtils.get_db_url(search_url):
                        index = index + 1
                        continue
                    break

                if index > 2:
                    index = index - 1
                    search_url = "%s?page=%s" % (url_origin, index)
                else:
                    search_url = url_origin

                while True:
                    self.log('request %s' % search_url)
                    html2 = self.utils.get_page(search_url)
                    if html2:
                        if self.dbUtils.get_db_url(search_url):
                            pass
                        else:
                            a = pq(html2)
                            items = a('div.js_video_row  div.video-box  a.video-box-image')
                            parse_successed = True
                            for item in items.items():
                                try:
                                    data_p = self.common.parse_item(item)
                                    if not data_p:
                                        parse_successed = False
                                        continue
                                    elif self.common.parse_detail_fr_brief_duplicate(data_p):
                                        continue

                                    data_t = {
                                        'name': 'Categories',
                                        'url': data_p.get('brief').get('url'),
                                        # 'refurl': search_url
                                    }

                                    data = dict(data_t, **data_p)
                                    yield data
                                except:
                                    parse_successed = False
                                    continue

                                if parse_successed:
                                    self.log('parsed url %s' % search_url)
                                    self.dbUtils.put_db_url(search_url)
                                else:
                                    self.log('request %s error' % search_url)

                        next_url = pq(html2)('#next .prev-next a').attr("href")
                        if next_url:
                            search_url = urljoin('https://www.youporn.com/', next_url)
                        else:
                            break
            except (GeneratorExit, StopIteration):
                break
            except:
                self.log('error in parse url %s' % url)
                continue

        yield None

    def urls_genarator(self):
        html = self.utils.get_page(self.url)
        if html:
            a = pq(html)
            categorys = a('#categoryList a.categoryBox')
            for category in categorys.items():
                yield urljoin("https://www.youporn.com", category.attr('href'))
        yield None


def job_start():
    para_args = {
        'savePath': 'Youporn\\{filePath}',
        'url': "https://www.youporn.com/categories/alphabetical/",
        'database': 'YoupornVideo'
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
