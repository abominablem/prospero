# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 15:30:08 2021

@author: marcu
"""
import inspect
import tkinter as tk
from tkinter import ttk

def null_function(self, *args, **kwargs):
    return

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
                for _event in _events:
                    self.event_generate(_event, when = "tail")
            return res
        return func_with_events
    return event_decorator

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
        self.events.add("<<ValueChange>>")

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
            for col in self.columns.values():
                if col.header == column:
                    return col.column
        else:
            return self.columns[column].header

    def is_id(self, field):
        try:
            self.columns[field]
            return True
        except KeyError:
            return False

    @__generate_event__("<<ValueChange>>", _test_arg = [("value", test_not_none)])
    def set_translate(self, item, column = None, value = None):
        """
        Equivalent to the parent set method except the column is translated
        to the equivalent ttk treeview id first.
        """
        if not column is None:
            column = self.translate_column(
                column, to_id = not self.is_id(column))
        return super().set(item, column, value)

    @__generate_event__("<<ValueChange>>", _test_arg = [("value", test_not_none)])
    def set(self, item, column = None, value = None):
        try:
            return super().set(item, column, value)
        except tk.TclError:
            return self.set_translate(item, column, value)


    @__generate_event__("<<ValueChange>>")
    def insert(self, parent, index, iid = None, **kw):
        return super().insert(parent, index, iid, **kw)

    @__generate_event__("<<ValueChange>>", _test_arg = [("values", test_not_none)])
    def item(self, item, option = None, **kw):
        return super().item(item, option, **kw)

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
        single_iid = False
        if isinstance(iid, str):
            single_iid = True
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

        for i, col in enumerate(columns):
            values_dict[col] = values[i]

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

class SimpleTreeviewEvents:
    def __init__(self, simple_treeview):
        if not isinstance(simple_treeview, SimpleTreeview):
            raise ValueError("Treeview must be instance of SimpleTreeview")
        self._treeview = simple_treeview
        self._edict = {}
        self.last = {"column": None, "row": None, "cell": None}

    def log_event(self, sequence, event, *args, **kwargs):
        """
        Log the col/row/cell under the cursor when the event is triggered
        """
        event_col = self._treeview.identify_column(event.x)
        event_row = self._treeview.identify_row(event.y)
        event_cell = (
            event_row if event_col == "#0" else
            self._treeview.set(event_row, event_col)
            )
        self.last = {"column": event_col, "row": event_row, "cell": event_cell}
        self._edict[sequence] = {
            "column": event_col, "row": event_row, "cell": event_cell
            }

    def add(self, sequence, bind = True):
        """ Add an event for reference later """
        if not isinstance(sequence, str):
            for seq in sequence: self.add(seq)
        self._edict[sequence] = {"column": None, "row": None, "cell": None}
        if bind:
            self._treeview.bind(
                sequence,
                self._add_log_call(sequence, null_function)
                )

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