# -*- coding: utf-8 -*-
"""
Created on Sat May 15 20:26:47 2021

@author: marcu
"""

import tkinter as tk
import config

class IODirectory():
    def __init__(self, parent,
                 call_after_input = None,
                 call_after_input_kwargs = None,
                 call_after_output = None,
                 call_after_output_kwargs = None,
                 trace = None):
        """
        Creates a frame with user editable input/output directories. If
        specified, the methods "call_after_input" and "call_after_output" will
        be called after the user changes the input/output directory
        respectively.
        """
        self.class_name = self.__class__.__name__
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent

        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call",
                     "parent": self.class_name + ".__init__"}

        self.call_after_input = call_after_input
        self.call_after_input_kwargs = call_after_input_kwargs
        self.call_after_output = call_after_output
        self.call_after_output_kwargs = call_after_output_kwargs

        self.frame = tk.Frame(self.parent.tab,
                              background = self.pr.c.colour_background)

        self.place_widgets(trace = inf_trace)
        self.load_from_config(trace= inf_trace)

    def place_widgets(self, trace = None):
        self.pr.f._log_trace(self, "place_widgets", trace)

        self.label_input = tk.Label(self.frame, text="Input Directory",
                                    **self.pr.c.label_standard_args)

        self.label_output = tk.Label(self.frame, text="Output Directory",
                                     **self.pr.c.label_standard_args)

        self.txt_input = tk.Entry(self.frame, **self.pr.c.entry_large_args)
        self.txt_output = tk.Entry(self.frame, **self.pr.c.entry_large_args)
        self.btn_input = tk.Button(self.frame,
                                   text="Change input directory",
                                   command = self._btnInputDirectory_Click,
                                   **self.pr.c.button_light_standard_args)

        self.btn_output = tk.Button(self.frame,
                                    text="Change output directory",
                                    command = self._btnOutputDirectory_Click,
                                    **self.pr.c.button_light_standard_args)

        self.grid_rc = {"label_input": {"row": 0, "column": 0},
                        "label_output": {"row": 1, "column": 0},
                        "txt_input": {"row": 0, "column": 1},
                        "txt_output": {"row": 1, "column": 1},
                        "btn_input": {"row": 0, "column": 2},
                        "btn_output": {"row": 1, "column": 2}
                        }

        self.max_row = max([self.grid_rc[key]["row"] 
                            for key in self.grid_rc.keys()])
        
        self.max_column = max([self.grid_rc[key]["column"] 
                               for key in self.grid_rc.keys()])

        self.label_input.grid(**self.grid_rc["label_input"],
                              **self.pr.c.grid_sticky_padding_small)

        self.label_output.grid(**self.grid_rc["label_output"],
                               **self.pr.c.grid_sticky_padding_small)

        self.txt_input.grid(**self.grid_rc["txt_input"],
                            **self.pr.c.grid_sticky_padding_small)

        self.txt_output.grid(**self.grid_rc["txt_output"],
                             **self.pr.c.grid_sticky_padding_small)

        self.btn_input.grid(**self.grid_rc["btn_input"],
                            **self.pr.c.grid_sticky_padding_small)

        self.btn_output.grid(**self.grid_rc["btn_output"],
                             **self.pr.c.grid_sticky_padding_small)

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=0)

    def _btnInputDirectory_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnInputDirectory_Click", trace)
        inf_trace = {"source": "function call",
                     "parent": self.class_name + "._btnInputDirectory_Click"}

        #Ask for the input directory and populate the textbox. Then pull the file list
        self.input_directory = tk.filedialog.askdirectory(initialdir="../../../../Music",
                                                          title='Select the input directory')
        self.txt_input.delete(0, "end")
        self.txt_input.insert(0, self.input_directory)
        # self.populate_file_list(event = None)
        config.config.config_dict[self.parent.__class__.__name__]['input_directory'] = self.input_directory

        if not self.call_after_input is None:
            if self.call_after_input_kwargs is None:
                self.call_after_input(trace = inf_trace)
            else:
                self.call_after_input(**self.call_after_input_kwargs,
                                      trace = inf_trace)

    def _btnOutputDirectory_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnOutputDirectory_Click", trace)
        inf_trace = {"source": "function call",
                     "parent": self.class_name + "._btnOutputDirectory_Click"}

        #Ask for the output directory and populate the textbox
        self.output_directory = tk.filedialog.askdirectory(initialdir="../../../../Music",  
                                                           title='Select the output directory')
        self.txt_output.delete(0, "end")
        self.txt_output.insert(0, self.output_directory)
        config.config.config_dict[self.parent.__class__.__name__]['output_directory'] = self.output_directory

        if not self.call_after_output is None:
            if self.call_after_output_kwargs is None:
                self.call_after_output(trace = inf_trace)
            else:
                self.call_after_output(**self.call_after_output_kwargs,
                                       trace = inf_trace)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def load_from_config(self, trace = None):
        self.pr.f._log_trace(self, "load_from_config", trace)
        self.input_directory = config.config.config_dict[self.parent.__class__.__name__]['input_directory']
        self.output_directory = config.config.config_dict[self.parent.__class__.__name__]['output_directory']
        
        self.txt_input.delete(0, "end")
        self.txt_output.delete(0, "end")

        self.txt_input.insert(0, self.input_directory)
        self.txt_output.insert(0, self.output_directory)

    def add_widget(self, widget, fixed_width = False, trace = None, **grid_kwargs):
        #options other than integers are "end" (current max + 1), input/output
        #for the row, and a previously added widget. Inputting a previously
        #added widget to the grid_kwargs uses up the value for that argument as
        #given when creating that widget.

        row = grid_kwargs["row"]
        column = grid_kwargs["column"]

        if row == "end":
            grid_kwargs["row"] = self.max_row + 1
        elif row in ["input", "output"]:
            grid_kwargs["row"] = self.grid_rc["label_%s" % row]["row"]
        elif type(row) != str and type(row) != int:
            #treat as previously added widget and get its row
            try:
                grid_kwargs["row"] = self.grid_rc[row]["row"]
            except KeyError:
                pass

        if column == "end":
            grid_kwargs["column"] = self.max_column + 1
        elif type(column) != str and type(column) != int:
            #treat as previously added widget and get its row
            try:
                grid_kwargs["column"] = self.grid_rc[column]["column"]
            except KeyError:
                pass

        row = grid_kwargs["row"]
        column = grid_kwargs["column"]

        widget.grid(**grid_kwargs, **self.pr.c.grid_sticky_padding_small)

        if not fixed_width: self.frame.columnconfigure(column, weight=1)

        #Add the widget grid references to the dictionary for later use
        self.grid_rc[widget] = {"row": row, "column": column}

        self.max_row = max(self.max_row, row)
        self.max_column = max(self.max_column, column)