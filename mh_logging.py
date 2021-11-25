# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 23:40:24 2021

@author: marcu
"""

from datetime import datetime
import inspect
import os

class Logging:
    def __init__(self, log = True):
        self.log = log

    def __call__(self, *args, **kwargs):
        self.log_trace(*args, **kwargs)

    def log_trace(self, parent, function, trace, add = ""):
        if self.log:
            if isinstance(trace, dict):
                try:
                    trace = trace["trace"]
                except KeyError:
                    pass
            else:
                trace = {"source": None, "widget": None, "parent": None
                         } if trace is None else trace

            if parent is None:
                trace["function"] = function
            elif isinstance(parent, str):
                trace["function"] = parent + "." + function
            else:
                trace["function"] = parent.__class__.__name__ + "." + function

            if trace["source"] == "bound event":
                trace_tuple = (datetime.now(), trace["function"],
                               trace["widget"], trace["event"])
                prnt = "%s Called %s from widget %s and event %s" % trace_tuple

            elif trace["source"] == "function call":
                trace_tuple = (datetime.now(), trace["function"],
                               trace["parent"])
                prnt = "%s Called %s from within %s" % trace_tuple

            elif trace["source"] == "initialise class":
                trace_tuple = (datetime.now(), parent.__class__.__name__,
                               trace["parent"])
                prnt = "%s Initialised class %s from within %s" % trace_tuple

            else:
                trace_tuple = (datetime.now(), trace["function"])
                prnt = "%s Called %s without trace" % trace_tuple

            prnt += " %s" % add
            print(prnt)

    def get_trace(self, parent = None, source = None,
                  function = None, add = ""):
        if source is None: raise ValueError("Trace source must be specified")

        if parent is None:
            parent_name = "__main__"
        elif isinstance(parent, str):
            parent_name = parent
        else:
            parent_name = parent.__class__.__name__

        if function is None or function == "<module>":
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

_log_instance = Logging()

def log(func):
    """ Decorator to add simple logging to non-class function """
    def _func_with_log(*args, **kwargs):
        stack_level = inspect.stack()[1]
        try:
            parent = os.path.basename(stack_level[0].f_locals["__file__"])
        except KeyError:
            parent = inspect.getmodule(stack_level[0]).__name__

        trace = _log_instance.get_trace(
            parent = parent,
            source = "function call",
            function = stack_level[3]
            )
        _log_instance(None, func.__name__, **trace)
        return func(*args, **kwargs)
    return _func_with_log

def try_iterate(f_dict, keys, err):
    for key in keys:
        try:
            return (key, f_dict[key])
        except err:
            continue

def log_class(func):
    """ Decorator to add simple logging to class function """
    def _func_with_log(self, *args, **kwargs):
        stack_level = inspect.stack()[1]
        parent, key = try_iterate(
            stack_level[0].f_locals,
            ["__class__", "__file__", "self", "event"],
            KeyError
            )
        if key == "__file__":
            parent = os.path.basename(parent)

        trace = _log_instance.get_trace(
            parent = parent,
            source = "function call",
            function = stack_level[3]
            )
        _log_instance(self, func.__name__, **trace)
        return func(self, *args, **kwargs)
    return _func_with_log