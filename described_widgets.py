# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 15:30:08 2021

@author: marcu
"""
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from mh_logging import log_class
from global_vars import LOG_LEVEL

def test_not_none(val):
    return not val is None

def __func_arg_dict__(func, args, kwargs, exclude_self = True):
    """ Return a dictionary of all named function arguments and their values """
    sig = inspect.signature(func)
    pars = sig.parameters.items()
    par_names = [k for k, v in pars]
    args_dict = {k: "__placeholder__" for k, v in pars}
    if exclude_self:
        del args_dict["self"]
        par_names.remove("self")

    # update with default argument values
    args_dict.update({k: v.default for k, v in pars
                      if v.default is not inspect.Parameter.empty})
    # update with arg values aligned to the list of arg names
    infer_args = {k: v for k, v in zip(par_names, args)}
    args_dict.update(infer_args)
    # update with kwargs
    args_dict.update(kwargs)
    return args_dict

def __generate_event__(_events, _test_arg = [], _cond = "or"):
    """
    Generate a list of events after the decorated function has been called

    _events is the list of event strings to generate. A string may be passed
    to generate a single event.

    _test_arg must be a list of tuples (kw, func) where kw is a keyword
    argument of the decorated function, and func is a function evaluating to
    True or False depending on if the event should be generated or not.

    _cond must be either "or" or "and". If "or", the event is generated if at
    least one test succeeds. If "and", the event is generated only if all tests
    succeed.
    """
    if isinstance(_events, str):
        _events = [_events]
    def event_decorator(func):
        def func_with_events(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            # get effective kwarg dict including args and default values
            arg_dict = __func_arg_dict__(func, args, kwargs)
            # test using the tuples of arg keywords and functions
            arg_test_bool = []
            for _arg in _test_arg:
                try: arg_test_bool.append(_arg[1](arg_dict[_arg[0]]))
                except: arg_test_bool.append(False)
            arg_test_res = sum(arg_test_bool)

            if ((_cond == "or" and arg_test_res > 0) or
                (_cond == "and" and arg_test_res == len(arg_test_bool) - 1) or
                _test_arg == []):
                event_args = {
                    "x": self.winfo_pointerx(), "y": self.winfo_pointery(),
                    "rootx": self.winfo_pointerx() - self.winfo_rootx(),
                    "rooty": self.winfo_pointery() - self.winfo_rooty()
                    }
                for _event in _events:
                    self.event_generate(_event, when = "tail", **event_args)
            return res
        return func_with_events
    return event_decorator

class WidgetEvents:
    @log_class(LOG_LEVEL)
    def __init__(self, widget):
        self.widget = widget
        self._edict = {}
        self._log_dict = {}
        self.last = {}

    @log_class(LOG_LEVEL)
    def null_function(self, *args, **kwargs):
        return

    @log_class(LOG_LEVEL)
    def log_event(self, sequence, event, **kwargs):
        """
        This method should be overwritten with the logic for any specific event
        attributes to be logged
        """
        raise NotImplementedError
        event_dict = {}
        self.log_event_dict(sequence, event_dict)

    @log_class(LOG_LEVEL)
    def log_event_dict(self, sequence, event_dict):
        """ Log the event using provided dict """
        event_dict["time"] = datetime.now()
        event_dict["sequence"] = sequence
        self._edict[sequence] = event_dict
        self.last = event_dict

    @log_class(LOG_LEVEL)
    def add(self, sequence, bind = True, log = True):
        """ Add an event for reference later """
        if not isinstance(sequence, str):
            for seq in sequence: self.add(seq)
        self._edict[sequence] = {"column": None, "row": None, "cell": None}

        if sequence in self._log_dict:
            log = self._log_dict[sequence]
        else:
            self._log_dict[sequence] = log

        if bind:
            func = (self._add_log_call(sequence, self.null_function)
                    if log else self.null_function)
            self.widget.bind(sequence, func)

    @log_class(LOG_LEVEL)
    def _add_log_call(self, sequence, func = None):
        log_event = lambda event: self.log_event(sequence, event)
        if func is None:
            return log_event
        else:
            def _log_call_with_func(event):
                log_event(event)
                return func(event)
            return _log_call_with_func

    def __getitem__(self, arg):
        if arg[0] != "<" and arg[-1] != ">":
            arg = "<%s>" % arg
        return self._edict[arg]


class SimpleTreeview(ttk.Treeview):
    def __init__(self, master, colsdict, **kwargs):
        super().__init__(master = master, **kwargs)
        self.colsdict = colsdict

        # Rebuild keys with tk column names
        self.columns = {"#%s" % i: cdict
                        for i, cdict in enumerate(colsdict.values())}

        for col, cdict in self.columns.items():
            self.columns[col] = SimpleTreeviewColumn(self, col, cdict)

        self.create_columns()
        self.events = SimpleTreeviewEvents(self)
        """ custom event triggered when a value in the treeview is updated. In
        practice this means whenever the set function is called with value not
        None, or the item values are set """
        self.events.add("<<ValueChange>>", log = False)

    def create_columns(self):
        self['columns'] = [col for col in self.columns if col != "#0"]
        for col in self.columns.values():
            col.create()

    def get_columns(self, ids = False, include_key = False):
        if ids:
            if include_key:
                return ['#0'] + list(self['columns'])
            else:
                return list(self['columns'])
        else:
            return [col.header for col in self.columns.values()
                    if (col.column != "#0" or include_key)]

    def translate_column(self, column, to_id = False):
        if to_id:
            if self.is_id(column):
                return column

            for col in self.columns.values():
                if col.header == column:
                    return col.column
        else:
            try:
                return self.columns[column].header
            except KeyError:
                return column

    def is_id(self, field):
        try:
            self.columns[field]
            return True
        except KeyError:
            return False

    def set_translate(self, item, column = None, value = None):
        """
        Equivalent to the parent set method except the column is translated
        to the equivalent ttk treeview id first.
        """
        if not column is None:
            column = self.translate_column(
                column, to_id = not self.is_id(column))
        res = super().set(item, column, value)

        if value is not None:
            self.events.log_event_dict("<<ValueChange>>", {
                "row": item, "column": self.translate_column(column),
                "cell": self.set(item, column)
                })
            self.event_generate("<<ValueChange>>", when = "tail")
        return res

    def set(self, item, column = None, value = None):
        try:
            res = super().set(item, column, value)
        except tk.TclError:
            res = self.set_translate(item, column, value)

        if value is not None:
            self.events.log_event_dict("<<ValueChange>>", {
                "row": item, "column": self.translate_column(column),
                "cell": self.set(item, column)
                })
            self.event_generate("<<ValueChange>>", when = "tail")
        return res

    def insert(self, parent, index, iid = None, **kw):
        res = super().insert(parent, index, iid, **kw)

        self.events.log_event_dict("<<ValueChange>>", {
            "row": iid, "column": "#0", "cell": None})
        self.event_generate("<<ValueChange>>", when = "tail")
        return res

    def item(self, item, option = None, **kw):
        res = super().item(item, option, **kw)

        if "values" in kw and kw["values"] is not None:
            self.events.log_event_dict("<<ValueChange>>", {
                "row": item, "column": "#0", "cell": None})
            self.event_generate("<<ValueChange>>", when = "tail")
        return res

    def clear(self):
        self.delete(*self.get_children())

    def has_selection(self):
        return len(self.selection()) > 0

    def _col_offset(self, col, offset, ids = True):
        cols_id = self.get_columns(ids = True, include_key = True)
        cols_head = self.get_columns(ids = False, include_key = True)

        cols = cols_id if self.is_id(col) else cols_head
        col_index = cols.index(col) + offset

        # check offset column is stil within the treeview
        if 0 <= col_index < len(cols):
            if ids:
                return cols_id[col_index]
            else:
                return cols_head[col_index]

    def prev_column(self, col, ids = True):
        return self._col_offset(col, -1, ids)

    def next_column(self, col, ids = True):
        return self._col_offset(col, 1, ids)

    def bind(self, sequence = None, func = None, add = None):
        self.events.add(sequence, bind = False)

        if self.events._log_dict[sequence]:
            func = self.events._add_log_call(sequence = sequence, func = func)

        super().bind(sequence, func, add)

    def to_json(self):
        json_dict = {}
        for child in self.get_children():
            json_dict[child] = self.item(child, 'values')
        return json_dict

    def from_json(self, json_dict):
        if not isinstance(json_dict, dict): raise TypeError
        for key, value in json_dict.items():
            self.insert("", index = "end", text = key, iid = key,
                        values = value)

    def get_dict(self, iid = None, include_key = False):
        if isinstance(iid, str):
            iid = [iid]
        elif iid is None:
            iid = self.get_children()

        columns = self.get_columns(ids = False, include_key = include_key)
        if include_key:
            key_col = columns[0]
            columns = columns[1:]

        treeview_dict = {}
        for child in iid:
            values = self.item(child, "values")
            values_dict = {key_col: child} if include_key else {}
            for i, col in enumerate(columns):
                values_dict[col] = values[i]
            treeview_dict[child] = values_dict

        return treeview_dict

    def values_dict(self, iid, include_key = False):
        values = self.item(iid, "values")
        columns = self.get_columns(ids = False, include_key = include_key)

        if include_key:
            values_dict = {columns[0]: iid}
            columns = columns[1:]
        else:
            values_dict = {}
        try:
            for i, col in enumerate(columns):
                values_dict[col] = values[i]
        except IndexError:
            print("iid: %s" % iid) # debug
            raise

        return values_dict

class SimpleTreeviewColumn:
    def __init__(self, treeview, column, cdict):
        self.treeview = treeview
        self.column = column
        self.__dict__.update(cdict)
        self.stretch = cdict.get("stretch", False)
        self.anchor = cdict.get("anchor", "w")

    def create(self):
        self.treeview.column(
            self.column,
            width = self.width,
            stretch = tk.YES if self.stretch else tk.NO,
            anchor = self.anchor
            )
        self.treeview.heading(self.column, text = self.header)

class SimpleTreeviewEvents(WidgetEvents):
    @log_class(LOG_LEVEL)
    def __init__(self, simple_treeview):
        if not isinstance(simple_treeview, SimpleTreeview):
            raise ValueError("Treeview must be instance of SimpleTreeview")
        super().__init__(simple_treeview)
        self.last = {"column": None, "row": None, "cell": None,
                     "sequence": None, "time": None}

    @log_class(LOG_LEVEL)
    def log_event(self, sequence, event, **kwargs):
        """
        Log the col/row/cell under the cursor when the event is triggered
        """
        event_col = self.widget.identify_column(event.x)
        event_row = self.widget.identify_row(event.y)
        event_cell = (
            event_row if event_col == "#0" else
            self.widget.set(event_row, event_col)
            )
        event_dict = {
            "column": event_col, "row": event_row, "cell": event_cell, **kwargs
            }
        self.log_event_dict(sequence, event_dict)

if __name__ == "__main__":
    columns = {1: {"header": "Column 1", "width": 400,
                    "stretch": True, "anchor": "w"},
               2: {"header": "Column 2", "width": 200,
                   "stretch": False, "anchor": "center"},
               3: {"header": "Column 3", "width": 300,
                   "stretch": True, "anchor": "w"},}

    root = tk.Tk()
    treeview = SimpleTreeview(root, columns)

    def test(event):
        print("<<ValueChange>>")

    def addrow(event):
        print(treeview.events["<<ValueChange>>"])
        try:
            treeview.insert('', 'end', iid = 'thing',
                            text = 'thing%s' % event.serial)
        except:
            treeview.item('thing', values = ["abc", "def"])

    treeview.bind("<1>", addrow)
    treeview.bind("<<ValueChange>>", test)

    # treeview.insert('', 'end', iid = 'thing', text = 'thing')

    treeview.grid(row = 0, column = 0)
    root.rowconfigure(0, weight = 1)
    root.columnconfigure(0, weight = 1)

    root.mainloop()