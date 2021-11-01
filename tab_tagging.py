# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 19:45:18 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
from io_directory import IODirectory
import described_widgets as dw
from arrange_widgets import WidgetSet


class Tagging :
    def __init__(self, parent, trace = None):
        self.name = "Tagging"
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab_tagging
        
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        """
        ### FRAMES ###
        """
        frame_kwargs = {"bg": self.pr.c.colour_background}
        self.widget_frame = tk.Frame(self.tab, **frame_kwargs)

        self.io_directory = IODirectory(
            parent = self,
            master = self.widget_frame,
            trace = inf_trace,
            call_after_input = self.populate_file_list
            )
        """
        ### TREEVIEW INFO ###
        """
        self.treeview_input_files = ttk.Treeview(self.widget_frame)
        self.treeview_current_tags = ttk.Treeview(self.widget_frame)
        self.treeview_suggested_tags = ttk.Treeview(self.widget_frame)
        self.treeviews = [self.treeview_input_files, 
                          self.treeview_current_tags,
                          self.treeview_suggested_tags]

        self.treeview_info = dw.SimpleTreeview(
            self.widget_frame, {1: {"header": "Filename",
                                    "width": self.pr.c.width_text_long,
                                    "stretch": True}}
            )
        self.treeview_current_tags = dw.SimpleTreeview(
            self.widget_frame, {1: {"header": "Tag",
                                    "width": self.pr.c.width_text_short,
                                    "stretch": False},
                                2: {"header": "Value",
                                    "width": self.pr.c.width_text_medium,
                                    "stretch": True}}
            )
        self.treeview_suggested_tags = dw.SimpleTreeview(
            self.widget_frame, {1: {"header": "Tag",
                                    "width": self.pr.c.width_text_short,
                                    "stretch": False},
                                2: {"header": "Value",
                                    "width": self.pr.c.width_text_medium,
                                    "stretch": True}}
            )

        """
        ### SAVE CHANGES ###
        """
        self.btn_save_changes = tk.Button(
            self.widget_frame,
            text = "Save changes",
            command = self.pr.f.null_function,
            **self.pr.c.button_light_standard_args
            )
        
        """
        ### IMPORT FILES ###
        """
        self.btn_import_files = tk.Button(
            self.widget_frame,
            text="Import Files",
            command = self.populate_file_list,
            **self.pr.c.button_light_standard_args
            )

        """
        ### PREVIOUS FILE ###
        """
        self.btn_previous_filename = tk.Button(
            self.widget_frame,
            text="▲",
            width = self.pr.c.width_button_small,
            command = self.pr.f.null_function,
            **self.pr.c.button_standard_args
            )

        """
        ### NEXT FILE ###
        """
        self.btn_next_filename = tk.Button(
            self.widget_frame,
            text="▼",
            width = self.pr.c.width_button_small,
            command = self.pr.f.null_function,
            **self.pr.c.button_standard_args
            )

        """
        ### COPY SUGGESTED TAGS ###
        """
        self.btn_copy_suggested_tags = tk.Button(
            self.widget_frame,
            text="«",
            width = self.pr.c.width_button_small,
            command = self.pr.f.null_function,
            **self.pr.c.button_standard_args
            )

        widgets = {
            1: {'widget': self.io_directory.frame,
                'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                'stretch_width': True},
            2: {'widget': self.treeview_input_files,
                'grid_kwargs': {"sticky": "nesw",
                                "pady": self.pr.c.padding_large_top_only},
                'stretch_width': True, 'stretch_height': True},
            3: {'widget': self.treeview_current_tags,
                'grid_kwargs': {"sticky": "nesw",
                                "pady": self.pr.c.padding_large_top_only},
                'stretch_width': True, 'stretch_height': True},
            4: {'widget': self.treeview_suggested_tags,
                'grid_kwargs': {"sticky": "nesw",
                                "pady": self.pr.c.padding_large_top_only},
                'stretch_width': True, 'stretch_height': True},
            5: {'widget': self.btn_save_changes,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            6: {'widget': self.btn_import_files,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            7: {'widget': self.btn_previous_filename,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': False},
            8: {'widget': self.btn_next_filename,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': False},
            9: {'widget': self.btn_copy_suggested_tags,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': False},
            -1: {'widget_kwargs': {'bg': self.pr.c.colour_background},
                'stretch_width': True, 'stretch_height': True}
            }
        self.widget_set = WidgetSet(self.widget_frame,
                                    widgets,
                                    layout = [[1],
                                              [2, -1, 3, -1,  4],
                                              [2,  7, 3, -1,  4],
                                              [2,  7, 3,  9,  4],
                                              [2,  8, 3,  9,  4],
                                              [2,  8, 3, -1,  4],
                                              [2, -1, 3, -1,  4],
                                              [6, -1, 5, -1, -1]
                                              ]
                                    )
        self.widget_set.grid(row = 0, column = 0, **self.pr.c.grid_sticky,
                             trace = inf_trace)

        self.tab.columnconfigure(index = 0, weight = 1)
        self.tab.rowconfigure(index = 0, weight = 1)

        self.treeview_input_files.bind("<ButtonRelease-1>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<ButtonRelease-1>"}))
        #refresh tags when moving up and down the file list with the arrow keys
        self.treeview_input_files.bind("<KeyRelease-Up>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<KeyRelease-Up>"}))
        self.treeview_input_files.bind("<KeyRelease-Down>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<KeyRelease-Down>"}))
        
        self.populate_file_list(trace = inf_trace)
        self._configure_last_called = datetime.min

    def populate_file_list(self, event = None, trace = None):
        self.pr.f._log_trace(self, "populate_file_list", trace)
        """
        Clears all treeviews and re-populates the list of filenames
        """
        
        if os.path.isdir(self.io_directory.input_directory):
            #clear all treeviews
            for tv in self.treeviews:
                tv.clear()
               
        #add all files in the specified directory with the correct extension
            for file in os.listdir(self.io_directory.input_directory):
                filename, extension = os.path.splitext(file)
                if extension == self.pr.c.file_extension:  
                    self.treeview_input_files.insert(
                        "", index="end", text = filename, iid = filename)
        return event
    
    def populate_current_tags_box(self, event, trace = None):
        self.pr.f._log_trace(self, "populate_current_tags_box", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".populate_current_tags_box"}
        """
        Updates the current and suggested tags Treeviews for the selected file
        """
        #Remove the current contents of each treeview
        for tv in [self.treeview_suggested_tags, self.treeview_current_tags]:
            tv.clear()
        
        #Get the selected file in the inputs files treeview
        #Exit if nothing is selected
        if len(self.treeview_input_files.selection()) == 0:
            return
        
        filename = self.treeview_input_files.selection()[0]
        
        #Add suggested values to the relevant treeview
        suggested_tag_dict = \
            self.pr.f.parse_tags_from_filename(filename, trace = inf_trace)
        
        #Add current values to the relevant treeview
        current_tag_dict = self.pr.f.get_tags(
            directory = self.io_directory.input_directory, 
            filename = filename + self.pr.c.file_extension, 
            trace = inf_trace
            )
        
        for dct in [suggested_tag_dict, current_tag_dict]:
            for key, value in dct.items():
                if value is None: value = ""
                dct[key] = [value]
        
        self.pr.f.json_to_treeview(treeview = self.treeview_suggested_tags,
                                   json_dict = suggested_tag_dict,
                                   trace = inf_trace)
        
        self.pr.f.json_to_treeview(treeview = self.treeview_current_tags,
                                   json_dict = current_tag_dict,
                                   trace = inf_trace)
        return event
   
    def load_from_config(self, trace = None):
        self.pr.f._log_trace(self, "load_from_config", trace)
    