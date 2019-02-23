#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: hejob<hejob.moyase@gmail.com>
# Created on 2019-02-23

import os
 
## default path
DIR_PATH = os.getcwd() + '/data'

class SaveImage(object):
    def __init__(self, path = None):
        if path:
            self.path = path
        else:
            self.path = DIR_PATH
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)
 
    def make_dir(self, path):
        path = path.strip()
        dir_path = self.path + path
        exists = os.path.exists(dir_path)
        if not exists:
            os.makedirs(dir_path)
            return dir_path
        else:
            return dir_path
 
    def save_image(self, content, file_path):
        # make dir first
        file_path = file_path.strip()
        index = file_path.rfind('/')
        if (index > 0):
            file_dir_path = file_path[:index]
            file_name = file_path[index + 1:]
            dir_path = self.make_dir(file_dir_path)
            full_path = dir_path + '/' + file_name
        else:
            full_path = self.path + file_path #already has '/'
        f = open(full_path, 'wb')
        f.write(content)
        f.close()

    def save_brief(self, content, dir_path, name):
        file_name = dir_path + "/" + name + ".txt"
        f = open(file_name, "w+")
        f.write(content.encode('utf-8'))
 
    def get_extension(self, url):
        index = url.find('.')
        if index < 0:
            return ''
        extension = url.split('.')[-1]
        #extension = url.split('/')[-1] # in case no . exists
        return extension


# test
if __name__ == "__main__":
    sv = SaveImage()
    content = b'ssstxt'
    sv.save_image(content, 'a.txt')
    sv.save_image(content, 'a.b/c.d/a.txt')

    sv2 = SaveImage('a/b')
    sv2.save_image(content, 'a.txt')
    sv2.save_image(content, 'a.b/c.d/a.txt')