# -*- coding:utf8 -*-
'''
Created on 2018年6月1日

@author: chenzf
'''
import os


class CWebParserProcess(object):
    def __init__(self, webParser):
        self.webParser = webParser


    def format_save_name(self, name):
        name = name.strip()
        patterns = [('\"', '_'),
                    (',', '_'),
                    (':', '_'),
                    ('!', '_'),
                    ('?', '_'),
                    ('/', '_'),
                    ('|', '_'),
                    ('#', '_'),
                    ('[', '_'),
                    (']', '_'),
                    ('\r', '_'),
                    ('\n', '_'),
                    ('*', '_'),
                    ('.', '_'),
                    ('\\', '_'),
                    ('\'', '_'),
                    ]
        for pattern in patterns:
            name = name.replace(pattern[0], pattern[1])
        return name

    def parse_item(self, item):
        pass

    def parse_detail_fr_brief(self, item):
        pass

    def get_sub_dir_name(self, data):
        sub_dir_name = "%s" % self.format_save_name(data.get('name'))
        return sub_dir_name

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
                                                         os.path.join('%s', '%s') % (sub_dir_name, self.format_save_name(data.get('name'))),
                                                         headers={'Referer': data.get('url')}
                                                         )

            # galleries
        galleries = data.get('detail').get('galleries')
        if galleries:
            board = galleries.get('board')
            if board:
                result &= self.webParser.utils.download_file(board,
                                                             os.path.join('%s', 'galleries', '%s', '%s') % (
                                                                 sub_dir_name, self.format_save_name(galleries.get('name')),
                                                                 self.format_save_name(galleries.get('name'))),
                                                             headers={'Referer': galleries.get('url')}
                                                             )

            stills = galleries.get('stills')
            if stills:
                for i, subVal in enumerate(stills, start=1):
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                                                     os.path.join('%s', 'galleries', '%s', '%s') % (
                                                                         sub_dir_name, self.format_save_name(galleries.get('name')), str(i)),
                                                                     headers={'Referer': galleries.get('url')}
                                                                     )

    # videos
        videos = data.get('detail').get('videos')
        if videos:
            board = videos.get('board')
            if board:
                result &= self.webParser.utils.download_file(board,
                                                             os.path.join('%s', 'videos', '%s', '%s') % (
                                                                 sub_dir_name, self.format_save_name(videos.get('name')), self.format_save_name(videos.get('name'))),
                                                             headers={'Referer': videos.get('url')}
                                                             )

            stills = videos.get('stills')
            if stills:
                for i, subVal in enumerate(stills, start=1):
                    if subVal:
                        result &= self.webParser.utils.download_file(subVal,
                                                                     os.path.join('%s', 'videos', '%s', '%s') % (
                                                                         sub_dir_name, self.format_save_name(videos.get('name')), str(i)),
                                                                     headers={'Referer': videos.get('url')}
                                                                     )

            video = videos.get('video')
            if video:
                if type(video) is list:
                    video = video[0]
                result &= self.webParser.utils.download_file(video,
                                                             os.path.join('%s', 'videos', '%s', '%s') % (
                                                                 sub_dir_name, self.format_save_name(videos.get('name')), self.format_save_name(videos.get('name'))),
                                                             headers={'Referer': videos.get('url')}
                                                             )

        return result
