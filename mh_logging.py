# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 23:40:24 2021

@author: marcu
"""

from datetime import datetime
import inspect
import os
from global_vars import LOG_LEVEL

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

def log_class(log_level = "all"):
    """
    Decorator to add simple logging to class function
    log_levels:
        all : Inspect the stack to determine where function was called from.
              This is the slowest option
        min : Log the function call but do not inspect the stack
        none : No logging.
    """
    # if no log_level provided, assume log_level is "all" and the argument
    # is in fact the function itself.
    inferred_func = None
    if not log_level in ["all", "min", "none"]:
        inferred_func = log_level
        log_level = "all"

    def decorator_creator(func):
        def _log_all(self, *args, **kwargs):
            try:
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
            except:
                trace = {"trace": None}
            _log_instance(self, func.__name__, **trace)
            return func(self, *args, **kwargs)

        def _log_min(self, *args, **kwargs):
            _log_instance(self, func.__name__, trace = None)
            return func(self, *args, **kwargs)

        def _log_none(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        if log_level == "all": return _log_all
        elif log_level == "min": return _log_min
        else: return _log_none

    if inferred_func is not None:
        return decorator_creator(inferred_func)
    else:
        return decorator_creator