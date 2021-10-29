# -*- coding: utf-8 -*-
"""
Created on Sun May  9 12:34:15 2021

@author: marcu
"""

import tkinter as tk
import os
from datetime import datetime

class SearchBox:
    def __init__(self, parent, trace = None):
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab
        
        self.pr.f._log_trace(self, "__init__", trace)
        
        self.base_frame = None
        self._last_destroyed = datetime.min
        self._last_button_pressed = datetime.min
        return
    
    def maintain(self, trace = None):
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".maintain"}
        if self.base_frame is None:
            self.pr.f._log_trace(self, "maintain", trace)
            self.create(trace = inf_trace)
        return
    
    def create(self, trace = None):
        self.pr.f._log_trace(self, "create", trace)
        """
        Create the search box GUI
        """
        
        # do not re-create if the search box was destroyed by a button press 
        # less than 1 second ago
        seconds_elapsed_destroyed = (datetime.now() 
                                     - self._last_destroyed).total_seconds()
        seconds_elapsed_button = (datetime.now() 
                                  - self._last_button_pressed).total_seconds()
        if seconds_elapsed_destroyed < 1 and seconds_elapsed_button < 1: return
            
        self.base_frame = tk.Frame(self.parent.tab, 
                                   background = self.pr.c.colour_background)
        self.grid(**self.base_frame_kwargs)
        
        self.search_box_label = tk.Label(self.base_frame, 
                                         text="Search text:",
                                         background = self.pr.c.colour_background, 
                                         font = self.pr.c.font_prospero_label_bold, 
                                         anchor = "e")
        self.search_box = tk.Entry(self.base_frame, 
                                   **self.pr.c.entry_medium_args)
        self.google_button = tk.Button(self.base_frame, 
                                       text = "Google", 
                                       **self.pr.c.button_light_standard_args, 
                                       width = 15, 
                                       command = self.pr.f.null_function)
        self.imslp_button = tk.Button(self.base_frame, 
                                      text = "IMSLP", 
                                      **self.pr.c.button_light_standard_args, 
                                      width = 15, 
                                      command = self.pr.f.null_function)
        self.go_to_url_button = tk.Button(self.base_frame, 
                                          text = "Go to URL", 
                                          **self.pr.c.button_light_standard_args, 
                                          width = 15, 
                                          command = self.pr.f.null_function)
        
        self.search_box_label.grid(row = 0, column = 0, sticky = "nesw", 
                                   padx = self.pr.c.padding_small, 
                                   pady = self.pr.c.padding_small)
        self.search_box.grid(row = 0, column = 1, sticky = "nesw", 
                             padx = self.pr.c.padding_small, 
                             pady = self.pr.c.padding_small)
        self.google_button.grid(row = 0, column = 2, sticky = "nesw", 
                                padx = self.pr.c.padding_small_left_only, 
                                pady = self.pr.c.padding_small)
        self.imslp_button.grid(row = 0, column = 3, sticky = "nesw", 
                               pady = self.pr.c.padding_small)
        self.go_to_url_button.grid(row = 0, column = 4, sticky = "nesw", 
                                   padx = self.pr.c.padding_small_right_only, 
                                   pady = self.pr.c.padding_small)
        
        self.google_button.bind("<Alt-1>", lambda event: self.search(event, "google", trace = {"source": "bound event", "widget": "SearchBox.create", "event": "<Alt-1>"}))
        self.imslp_button.bind("<Alt-1>", lambda event: self.search(event, "imslp", trace = {"source": "bound event", "widget": "SearchBox.create", "event": "<Alt-1>"}))
        self.go_to_url_button.bind("<Alt-1>", lambda event: self.search(event, "go_to_url", trace = {"source": "bound event", "widget": "SearchBox.create", "event": "<Alt-1>"}))
        
        #weight the label and textbox equally so the textbox always takes up half the window, minus the fixed width buttons
        self.base_frame.columnconfigure(0, weight=1)
        self.base_frame.columnconfigure(1, weight=1)
        self.base_frame.columnconfigure(2, weight=0)
        self.base_frame.columnconfigure(3, weight=0)
        self.base_frame.columnconfigure(4, weight=0)
        return

    def grid(self, **kwargs):
        """
        Place the search box in the grid
        """
        self.base_frame_kwargs = kwargs
        if not self.base_frame is None:
            self.base_frame.grid(**kwargs)

    def destroy(self, trace = None):
        self.pr.f._log_trace(self, "destroy", trace)
        """
        Destroy the search box GUI
        """
        if not self.base_frame is None:
            self.search_box.destroy()
            self.search_box_label.destroy()
            self.google_button.destroy()
            self.imslp_button.destroy()
            self.base_frame.destroy()
            self.go_to_url_button.destroy()
            
            self.search_box = None
            self.search_box_label = None
            self.google_button = None
            self.imslp_button = None
            self.base_frame = None
            self.go_to_url_button = None
            
            self._last_destroyed = datetime.now()
        return
    
    def search(self, event, site, trace = None):
        self.pr.f._log_trace(self, "search", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".search"}
        
        self._last_button_pressed = datetime.now()
        
        site = site.lower()
        if site == "google":
            url_prefix = "http://google.com/search?q="
            phrase = self.search_box.get().strip().replace(" ", "+")
        elif site == "imslp":
            url_prefix = "http://google.com/search?q=site:imslp.org+"
            phrase = self.search_box.get().strip().replace(" ", "+")
        elif site == "go_to_url":
            url_prefix = ""
            phrase = self.search_box.get().strip()
            
        phrase = self.search_box.get().strip().replace(" ", "+")
        self.destroy(trace = inf_trace)
        command = 'start "" %s%s' % (url_prefix, phrase)
        os.system(command)
        return event

    def add(self, text, trace = None):
        self.pr.f._log_trace(self, "add", trace)
        
        if self.base_frame is None:
            raise Exception("Object %s.search_box not initialised" 
                            % self.__class__.__name__)
            return
        
        if text != "":
            self.search_box.insert("end", " " + text)
        return