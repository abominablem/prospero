# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 23:40:24 2021

@author: marcu
"""

from datetime import datetime

class Logging:
    def __init__(self, log = True, trace = None):
        self.log = log
        self.log_trace(self, "__init__", trace)

    def __call__(self, *args, **kwargs):
        self.log_trace(*args, **kwargs)

    def log_trace(self, parent, function, trace, add = ""):
        if self.log:
            trace = {"source": None, "widget": None, "parent": None
                     } if trace is None else trace
            
            if parent is None:
                trace["function"] = function
            if type(parent) is str:
                trace["function"] = parent + "." + function
            else:
                trace["function"] = parent.__class__.__name__ + "." + function
            
            if trace["source"] == "bound event":
                trace_tuple = (datetime.now(), trace["function"], 
                               trace["widget"], trace["event"])
                prnt = "%s Called %s from widget %s and event %s." % trace_tuple
                
            elif trace["source"] == "function call":
                trace_tuple = (datetime.now(), trace["function"], 
                               trace["parent"])
                prnt = "%s Called %s from within %s." % trace_tuple
                
            elif trace["source"] == "initialise class":
                trace_tuple = (datetime.now(), parent.__class__.__name__, 
                               trace["parent"])
                prnt = "%s Initialised class %s from within %s." % trace_tuple
                
            else:
                trace_tuple = (datetime.now(), trace["function"])
                prnt = "%s Called %s without trace." % trace_tuple
                
            prnt += " %s" % add
            print(prnt)

    def get_trace(self, parent = None, source = None,
                  function = None, add = ""):
        if source is None: raise ValueError("Trace source must be specified")

        if parent is None:
            parent_name = "__main__"
        else:
            parent_name = parent.__class__.__name__

        if function is None:
            function = ""
        else:
            function = ".%s" % function

        if "function" in source:
            source = "function call"
        elif "bound" in source:
            source = "bound event"
        elif "init" in source and "class" in source:
            source = "initialise class"
            if function == "" or function is None:
                function = "__init__"

        return {"trace": {"source": source,
                          "parent": parent_name + function,
                          "add": add}
                }

if __name__ == "__main__":
    log = Logging(__name__, log = False,
                   trace = {"source": "initialise class",
                            "parent": __name__})