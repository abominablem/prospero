# -*- coding: utf-8 -*-
"""
Created on Sun May  9 12:34:15 2021

@author: marcu
"""

import tkinter as tk
import os
from datetime import datetime

class SearchBox:
    def __init__(self, parent, master, trace = None):
        self.pr = parent.pr
        self.parent = parent
        self.master = master

        self.pr.f._log_trace(self, "__init__", trace)

        self._last_destroyed = datetime.min
        self._last_button_pressed = datetime.min
        self.active = False

    def maintain(self, trace = None):
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".maintain"}
        if not self.active:
            self.pr.f._log_trace(self, "maintain", trace)
            self.create(trace = inf_trace)

    def create(self, trace = None):
        self.pr.f._log_trace(self, "create", trace)
        """
        Create the search box GUI
        """
        # do not re-create if the search box was destroyed by a button press
        # less than 1 second ago
        seconds_elapsed_destroyed = (
            datetime.now() - self._last_destroyed).total_seconds()
        seconds_elapsed_button = (
            datetime.now() - self._last_button_pressed).total_seconds()
        if seconds_elapsed_destroyed < 1 and seconds_elapsed_button < 1:
            return
            
        self.active = True

        self.frame = tk.Frame(self.master,
                              background = self.pr.c.colour_background)
        self.grid(**self.frame_kwargs)

        self.search_box_label = tk.Label(
            self.frame,
            text="Search text:",
            background = self.pr.c.colour_background,
            font = self.pr.c.font_prospero_label_bold,
            anchor = "e"
            )
        self.search_box = tk.Entry(
            self.frame,
            **self.pr.c.entry_medium_args
            )
        self.google_button = tk.Button(
            self.frame,
            text = "Google",
            **self.pr.c.button_light_standard_args,
            width = 15,
            command = self.pr.f.null_function
            )
        self.imslp_button = tk.Button(
            self.frame,
            text = "IMSLP",
            **self.pr.c.button_light_standard_args,
            width = 15,
            command = self.pr.f.null_function
            )
        self.go_to_url_button = tk.Button(
            self.frame,
            text = "Go to URL",
            **self.pr.c.button_light_standard_args,
            width = 15,
            command = self.pr.f.null_function
            )
        
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
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=0)
        self.frame.columnconfigure(3, weight=0)
        self.frame.columnconfigure(4, weight=0)


    def grid(self, **kwargs):
        """
        Place the search box in the grid
        """
        self.frame_kwargs = kwargs
        if self.active:
            self.frame.grid(**kwargs)

    def destroy(self, trace = None):
        self.pr.f._log_trace(self, "destroy", trace)
        """
        Destroy the search box GUI
        """
        if self.active:
            self.search_box.destroy()
            self.search_box_label.destroy()
            self.google_button.destroy()
            self.imslp_button.destroy()
            self.frame.destroy()
            self.go_to_url_button.destroy()
            
            self._last_destroyed = datetime.now()
            self.active = False

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
        
        if not self.active:
            raise Exception("Object %s.search_box not active"
                            % self.__class__.__name__)
            return
        
        if text != "":
            self.search_box.insert("end", " " + text)