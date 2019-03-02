#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-23 00:05:09
# Project: slides_t1

from pyspider.libs.base_handler import *
from pyspider.util import SaveImage

URL = 'https://app.anitama.net'
DIR_PATH = "./data/slides"

class Handler(BaseHandler):
    crawl_config = {
    }
    
    ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

    def __init__(self):
        self.saver = SaveImage(DIR_PATH)

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(URL + '/slide', callback=self.index_page, user_agent=self.ua)

    @config(priority=99, age=10 * 24 * 60 * 60)
    def index_page(self, response):
        if response.json.get('data') and response.json['data'].get('slides'):
            slides = response.json['data']['slides']
            for slide in slides:
                if slide.get('cover'):
                    self.crawl(slide['cover']['cover'], callback=self.save_image, user_agent=self.ua, save={'aid': slide['aid']})
                    self.crawl(slide['cover']['url'], callback=self.save_image, user_agent=self.ua, save={'aid': slide['aid']})
            return [
                # {
                #     'aid': slide['aid'],
                #     'recommendId': slide['recommendId'],
                #     'cover': slide['cover'], # is an array
                #     'sortDate': slide['sortDate'],
                #     'status': slide['status'],
                #     'subtitle': slide['subtitle'],
                #     'title': slide['title'],
                #     'typeId': slide['typeId'],
                #     'url': slide['url'],
                # }
                slide for slide in slides
            ]

    @config(priority=80)
    def save_image(self, response):
        url = response.url
        
        # strip xxx://
        url = url.split('://')[-1]

        content = response.content
        self.saver.save_image(content, url)
