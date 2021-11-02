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
            col = self.columns[field]
            return True
        except KeyError:
            return False

    def set_translate(self, item, column = None, value = None):
        if not column is None:
            column = self.translate_column(
                column, to_id = not self.is_id(column))

        return self.set(item, column, value)

    def clear(self):
        self.delete(*self.get_children())

    def has_selection(self):
        return len(self.selection_get()) > 0

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

if __name__ == "__main__":
    columns = {
                1: {"header": "Column 1", "width": 400,
                    "stretch": True, "anchor": "w"},
                2: {"header": "Column 2", "width": 200,
                    "stretch": True, "anchor": "center"},
                3: {"header": "Column 3", "width": 300,
                    "stretch": True, "anchor": "w"},}
    
    root = tk.Tk()
    treeview = SimpleTreeview(root, columns)
    
    treeview.grid(row = 0, column = 0)
    treeview.master.rowconfigure(0, weight = 1)
    treeview.master.columnconfigure(0, weight = 1)
    
    print(treeview.get_column_names())