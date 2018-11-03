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

    def parse_item(self, item):
        data = None
        #         ?4x174x20576
        url = None
        url_pre = re.search('(.*?)\?\d+x\d+x\d+', item.attr('href'), re.S)
        if url_pre.group():
            url = urljoin('http://theeroticbeauties.com/', url_pre.group(1))
        else:
            url = urljoin('http://theeroticbeauties.com/', item.attr('href'))

        board = item('img').attr('src')

        data_brief = {
            'url': url,
            'board': board,
        }

        data = {'brief': data_brief}
        if self.webParser.parseOnly == CParseType.Parse_Brief:
            return data
        else:
            return self.parse_detail_fr_brief(data)

    def parse_detail_fr_brief(self, item):
        data = None
        url = item.get('brief').get('url')
        while True:
            html = self.webParser.utils.get_page(url)

            if html:
                b = pq(html)

                name = b('#all')
                if not name:
                    continue

                name = b('#all > h1').text()

                stills = []
                previews = b('div.thumbs4 a')
                for preview in previews.items():
                    stills.append(preview('a').attr('href'))

                data_detail = {
                    'galleries': {
                        'name': self.webParser.utils.format_name(name),
                        'url': item.get('brief').get('url'),
                        'board': item.get('brief').get('board'),
                        'stills': stills,
                    }
                }

                data = deepcopy(item)
                data['detail'] = data_detail
                break
        return data

    #     def process_data(self, data):


#         result = True
#         sub_dir_name = "%s\\galleries\\%s" %(data.get('modelName'), data.get('productName'))
#        
#         dir_name = self.webParser.savePath.format(filePath=sub_dir_name)
#         if not os.path.exists(dir_name):
#             os.makedirs(dir_name)
#         
#         with open(dir_name + '\\info.json', 'w') as f:    
#             json.dump(data, f)
#             
#         board = data.get('board')
#         if board:
#             result &=  self.webParser.utils.download_file(board,
#                                 '%s\\%s' % (sub_dir_name, data.get('productName')),
#                                 headers={'Referer':'https://www.babehub.com/'}
#                                  )  
#      
#         stills = data.get('stills')
#         for i, val in enumerate(stills, start=1): 
#             for subVal in val:
#                 if subVal:
#                     result &= self.webParser.utils.download_file(subVal,
#                                      '%s\\%s' % (sub_dir_name, str(i)),
#                                      headers={'Referer':data.get('url')}
#                              )   
#                     break        
#  
#         return result      


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
                    items = a('div.thumbs a')

                    for item in items.items():
                        data_p = self.common.parse_item(item)
                        data_t = {
                            'name': 'TheEroticBeauties',
                            'url': data_p.get('brief').get('url'),
                            #                             'board':  data_p.get('brief').get('board'),
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
        'savePath': 'TheEroticBeauties\\{filePath}',
        'url': 'http://theeroticbeauties.com/category/0/All/ctr/{page}/',
        'database': 'TheEroticBeauties',
        'start': 1,
        'end': 75
    }

    job = CWebParserSite(**para_args)
    job.call_process()


if __name__ == '__main__':
    job_start()
