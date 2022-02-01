# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 22:09:37 2021

@author: marcu
"""
import os
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
from mh_logging import log_class
from global_vars import LOG_LEVEL
log_class = log_class(LOG_LEVEL)
from sqlite_tablecon import TableCon

class Insight(TableCon):
    """
    This class wraps functions that allow prediction of values from an input
    string. These predictions are based on database of past values entered.
    """
    @log_class
    def __init__(self, type, debug = False):
        self.type = type
        self._debug = debug

        super(Insight, self).__init__(
            db = os.path.abspath('.\sqlite_db\insight.db'),
            table = type,
            debug = debug,
            check_same_thread = False
            )

    @log_class
    def get_insight(self, values, column, **f_kwargs):
        del_list = []
        for k, v in values.items():
            if k.lower() == column or v == '' or v is None:
                del_list.append(k)

        for k in del_list:
            del values[k]
        try:
            filtered = self.filter(values, column, **f_kwargs)
        except:
            filtered = {}
        for k, v in filtered.items():
            filtered[k] = [t for t in v if t != "" and not t is None]
        return filtered

insight = Insight("renames", debug = True)
# print(insight.filter({"Composer": "Schein, Johann Hermann"}, "album"))