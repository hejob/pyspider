#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-23
# Project: timeline_t1

from pyspider.libs.base_handler import *
from pyspider.util import SaveImage
from pyquery import PyQuery

URL = 'https://app.anitama.net'
DIR_PATH = "./data/timeline"

class Handler(BaseHandler):
    crawl_config = {
    }
    
    ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

    def __init__(self):
        self.saver = SaveImage(DIR_PATH)

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl_timeline(1)

    """ crawl timeline with pageNo """
    def crawl_timeline(self, pageNo = 1):
        self.crawl(URL + '/timeline?pageNo=' + str(pageNo), callback=self.timeline, user_agent=self.ua)

    @config(priority=99, age=10 * 24 * 60 * 60)
    def timeline(self, response):
        if response.json.get('data') and response.json['data'].get('page'):
            page_info = response.json['data']['page']

            # check next page
            page_no = page_info['pageNo']
            page_size = page_info['pageSize']
            total_count = page_info['totalCount']
            index_start = page_info['start']
            if index_start + page_size < total_count:
                self.crawl_timeline(page_no + 1)

            # process with list
            for item in page_info['list']:
                entry_type = item['entryType']

                # !other types
                if not entry_type == 'article':
                    continue
                
                if item.get('cover'):
                    #! ['cover']['origin']?
                    self.crawl(item['cover']['cover'], callback=self.save_image, user_agent=self.ua, save={'aid': item['aid']})
                    self.crawl(item['cover']['url'], callback=self.save_image, user_agent=self.ua, save={'aid': item['aid']})
                
                # ?process info here, or just in crawl_article?

                # article type
                aid = item['aid']
                self.crawl(URL + '/article/' + str(aid), callback=self.save_article, user_agent=self.ua, save={'aid': item['aid']})
                
            # return [
            #     {
            #         'aid': slide['aid'],
            #         'recommendId': slide['recommendId'],
            #         'sortDate': slide['sortDate'],
            #         'status': slide['status'],
            #         'subtitle': slide['subtitle'],
            #         'title': slide['title'],
            #         'typeId': slide['typeId'],
            #         'url': slide['url'],
            #     } for slide in slides
            # ]

    @config(priority=80, age=10 * 24 * 60 * 60)
    def save_article(self, response):
        url = response.url
        if response.json.get('data') and response.json['data'].get('article'):
            article = response.json['data']['article']

            if article.get('channel'):
                #! crawl channel, or use channel extry page
                pass
            
            if article.get('cover'):
                if article['cover'].get('thumb'):
                   self.crawl(article['cover']['thumb'], callback=self.save_image, user_agent=self.ua, save={'aid': article['aid']})
                if article['cover'].get('url'):
                   self.crawl(article['cover']['url'], callback=self.save_image, user_agent=self.ua, save={'aid': article['aid']})
            
            # in html content
            content = article['html']
            query = PyQuery(content)
            imgs = query('img')
            for img in imgs:
                img_url = PyQuery(img).attr('src')
                self.crawl(img_url, callback=self.save_image, user_agent=self.ua, save={'aid': article['aid']})
                # if preview, crawl origin
                if img_url.endswith('-preview'):
                    img_url_origin = img_url[:-8] + '-origin'
                    self.crawl(img_url_origin, callback=self.save_image, user_agent=self.ua, save={'aid': article['aid']})

            # comments
            self.crawl_comments(article['aid'], 1)

            return {
                **article,
                "entryType": "article",
            }

    """ crawl timeline with pageNo """
    def crawl_comments(self, aid, pageNo = 1):
        self.crawl(URL + '/comment/' + aid + '?type=article&pageNo=' + str(pageNo), callback=self.comments, user_agent=self.ua, save={'aid': aid})
    
    @config(priority=60, age=10 * 24 * 60 * 60)
    def comments(self, response):
        url = response.url
        aid = response.save['aid']
        if not (response.json.get('data')):
            return

        page_no = response.json['data']['pageNo']
        page_size = response.json['data']['pageSize']
        total_count = response.json['data']['totalCount']

        if total_count < 1 or len(response.json['data']['html']) < 1:
            return

        if (page_no + 1) * page_size < total_count:
            self.crawl_comments(aid, page_no + 1)

        return {
            'html': response.json['data']['html'],
            'entryType': 'comment',
            'aid': response.save['aid'],
            'page_no': response.json['data']['pageNo'],
            'page_size': response.json['data']['pageSize'],
            'total_count': response.json['data']['totalCount'],
        }

    @config(priority=70)
    def save_image(self, response):
        url = response.url
        
        # strip xxx://
        url = url.split('://')[-1]

        content = response.content
        self.saver.save_image(content, url)



# problems:
# no article type save
# empty comment is saved
