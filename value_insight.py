# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 22:09:37 2021

@author: marcu
"""

from mh_logging import Logging
from sqlite_database import TableCon

Logging

class Insight(TableCon):
    """
    This class wraps functions that allow prediction of values from an input
    string. These predictions are based on database of past values entered.
    """
    def __init__(self, type, debug = False, trace = None):
        self.name = self.__class__.__name__
        
        super(Insight, self).__init__(db = '.\sqlite_db\insight', 
                                      table = type, 
                                      debug = debug)
        
        inf_trace = {"source": "function call", 
                     "parent": self.name +".__init__"}
        
        self.logging = Logging(parent = self, testing_mode = True, 
                               trace = inf_trace)
        self.logging.log_trace(self, "__init__", 
                               trace = {"source": "initialise class", 
                                        "parent": self.name})
        self.type = type
        
    def get_insight(self, values, column, trace = None):
        self.logging.log_trace(self, "get_insight", trace)
        
        del_list = []
        for k, v in values.items():
            if k.lower() == column or v == '' or v is None:
                del_list.append(k)
                
        for k in del_list:
                del values[k]
        
        filtered = self.filter(values, column)
        for k, v in filtered.items():
            filtered[k] = [t for t in v if t != "" and not t is None]
        return filtered
        
    def close(self, trace = None):
        self.logging.log_trace(self, "close", trace)
        super().close()
        
        
        
insight = Insight("renames", debug = True)
print(insight.filter({"Composer": "Schein, Johann Hermann"}, "album"))
        
        
        
