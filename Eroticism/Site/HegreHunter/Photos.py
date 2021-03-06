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
        result = re.findall('[a-zA-z]+://[^\s]*', str(item('img').attr('srcset')))

        data_brief = {
            'url': url,
            'board': result[0] if result and len(result) >= 2 else None,
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

            art_site_info = b('#breadcrumbs li')
            info_string = []
            for it in art_site_info.items():
                info_string.append(it.text())

            if len(info_string) >= 3:
                site, model, name = info_string[0], info_string[1], info_string[2]

            video = None
            video_item = b('video')
            stills = []
            if video_item:
                src = []
                for src_item in video_item('source').items():
                    src.append(src_item.attr('src'))
                video = {
                    'src': src,
                    'board': video_item.attr('poster')
                }
            else:
                previews = b('ul.gallery-b  li')
                for preview in previews.items():
                    stills.append(preview('a').attr('href'))

            if video:
                data_detail = {
                    'videos': {
                        'name': '%s %s' % (model, name),
                        'url': item.get('brief').get('url'),
                        'board': video.get('board'),
                        'site': site,
                        'video': video.get('src'),
                        'stills': stills,
                    }
                }
            else:
                data_detail = {
                    'galleries': {
                        'name': '%s %s' % (model, name),
                        'url': item.get('brief').get('url'),
                        'site': site,
                        'stills': stills,
                    }
                }

            data = deepcopy(item)
            data['detail'] = data_detail
            data['name'] = info_string[1]

        return data

    def get_sub_dir_name(self, data):
        if data.get('detail').get('videos'):
            sub_dir_name = os.path.join("%s", "%s") % (
            data.get('detail').get('videos').get('site'), self.format_save_name(data.get('name')))
        else:
            sub_dir_name = os.path.join("%s", "%s") % (
            data.get('detail').get('galleries').get('site'), self.format_save_name(data.get('name')))
        return sub_dir_name


class CWebParserHunterMultiUrl(CWebParserMultiUrl):
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
                items = a('nav.pagination-a').prev_all('ul li')
                parse_succeed = True
                for item in items.items():
                    try:
                        data_p = self.common.parse_item(item)
                        data_t = {
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


class CWebParserHunterSingleUrl(CWebParserSingleUrl):
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
                items = a('#content h2').prev_all('ul.gallery-a li')
                parse_succeed = True
                for item in items.items():
                    try:
                        data_p = self.common.parse_item(item)
                        data_t = {
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


def job_start():
    job_list = [
        ('S', 'https://www.alshunter.com'),
        ('S', 'https://www.centerfoldhunter.com'),
        ('S', 'https://www.domerotica.com'),
        ('S', 'https://www.drommhub.com'),
        ('S', 'https://www.eroticandbeauty.com'),
        ('S', 'https://www.erroticahunter.com'),
        ('S', 'https://www.mplhunter.com'),
        ('S', 'https://www.penthousehub.com'),
        ('S', 'https://www.rylskyhunter.com'),
        ('S', 'https://www.tlehunter.com'),
        ('S', 'https://www.w4bhub.com'),
        ('S', 'https://www.zemanihunter.com'),
        ('S', 'https://www.femangels.com/'),
        ('M', 'https://www.elitebabes.com/archive/page/{page}', 0, 665),
        ('M', 'https://www.femjoyhunter.com/archive/page/{page}', 1, 36),
        ('M', 'https://www.hegrehunter.com/archive/page/{page}', 1, 18),
        ('M', 'https://www.joymiihub.com/archive/page/{page}', 1, 8),
        ('M', 'https://www.jperotica.com/archive/page/{page}', 1, 36),
        ('M', 'https://www.metarthunter.com/archive/page/{page}', 1, 82),
        ('M', 'https://www.pmatehunter.com/archive/page/{page}', 1, 42),
        ('M', 'https://www.xarthunter.com/archive/page/{page}', 1, 9),
    ]

    for job_item in job_list:
        if job_item[0] == 'S':
            para_args = {
                'savePath': os.path.join('Hunter', '{filePath}'),
                'url': job_item[1],
                'database': 'HegreHunter'
            }

            job = CWebParserHunterSingleUrl(**para_args)
        else:
            para_args = {
                'savePath': os.path.join('Hunter', '{filePath}'),
                'url': job_item[1],
                'database': 'HegreHunter',
                'start': job_item[2],
                'end': job_item[3]
            }

            job = CWebParserHunterMultiUrl(**para_args)

        job.call_process()


if __name__ == '__main__':
    job_start()
