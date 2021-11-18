# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 15:30:08 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk

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

    def set_translate(self, item, column = None, value = None):
        """
        Equivalent to the parent set method except the column is translated
        to the equivalent ttk treeview id first.
        """
        if not column is None:
            column = self.translate_column(
                column, to_id = not self.is_id(column))

        return super().set(item, column, value)

    def set(self, item, column = None, value = None):
        try:
            return super().set(item, column, value)
        except tk.TclError:
            return self.set_translate(item, column, value)

    def clear(self):
        self.delete(*self.get_children())

    def has_selection(self):
        return len(self.selection_get()) > 0

    def bind(self, sequence = None, func = None, add = None):
        self.events.add_event(sequence)
        func = self.events._add_log_call(sequence = sequence, func = func)
        super().bind(sequence, func, add)

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

    def add_event(self, sequence):
        """ Add an event for reference later """
        self._edict[sequence] = {"column": None, "row": None, "cell": None}

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

    treeview.bind("<a>")
    treeview.bind("<Button-1>")

    treeview.grid(row = 0, column = 0)
    root.rowconfigure(0, weight = 1)
    root.columnconfigure(0, weight = 1)

    root.mainloop()