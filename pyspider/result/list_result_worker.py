#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: hejob.moyase@gmail.com
# Created on 2019-02-23

import time
import json
import logging
from .result_worker import ResultWorker
logger = logging.getLogger("result")


class ListResultWorker(ResultWorker):

    """
    do with a list of result
    """

    def on_result(self, task, result):
        '''If list, call on_result on every item, but change key(taskid)'''
        if not result:
            return
        if isinstance(result, list):
            index = 0
            for item in result:
                item_task = {**task}
                # use sub taskid to distingush every item (or will save to the same item row)
                item_task['taskid'] = task['taskid'] + '#' + str(index)
                super().on_result(item_task, item)
                index = index + 1
            return
        super().on_result(task, result)
