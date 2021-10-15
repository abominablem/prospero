# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 21:59:50 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk
import re

import config

import prospero_constants as prc
import prospero_functions as prf
import prospero_resources as prr

class Settings:
    def __init__(self, parent, trace = None):
        self.parent = parent
        self.root = parent.root
        self.pr = parent.pr
        self.pr.f._log_trace(self, "__init__", trace)
        
        self.window = tk.Toplevel(self.root, 
                                  background = self.pr.c.colour_background)
        self.window.title("Prospero - Settings and config")
        
        self.title_frame = tk.Frame(
            self.window, 
            background = self.pr.c.colour_prospero_blue
            )
        TitleFrameGridRow = 0
        TitleFrameGridColumn = 0
        TitleFrameColumnSpan = self.pr.c.columnspan_all
        TitleFrameRowSpan = 1
        self.title_frame.grid(row = TitleFrameGridRow,
                              column = TitleFrameGridColumn,
                              columnspan = TitleFrameColumnSpan,
                              rowspan = TitleFrameRowSpan,
                              sticky = "nesw"
                              )
        
        self.selection_frame = tk.Frame(
            self.window, 
            background = self.pr.c.colour_background
            )
        SelectionFrameGridRow = TitleFrameGridRow + TitleFrameRowSpan
        SelectionFrameGridColumn = TitleFrameGridColumn
        SelectionFrameColumnSpan = 1
        SelectionFrameRowSpan = 1
        self.selection_frame.grid(row = SelectionFrameGridRow,
                              column = SelectionFrameGridColumn,
                              columnspan = SelectionFrameColumnSpan,
                              rowspan = SelectionFrameRowSpan,
                              sticky = "nesw"
                              )
        
        self.settings_frame = tk.Frame(
            self.window, 
            background = self.pr.c.colour_background
            )
        SettingsFrameGridRow = SelectionFrameGridRow
        SettingsFrameGridColumn = (SelectionFrameGridColumn 
                                   + SelectionFrameColumnSpan)
        SettingsFrameColumnSpan = 1
        SettingsFrameRowSpan = SelectionFrameRowSpan
        self.settings_frame.grid(row = SettingsFrameGridRow,
                              column = SettingsFrameGridColumn,
                              columnspan = SettingsFrameColumnSpan,
                              rowspan = SettingsFrameRowSpan,
                              sticky = "nesw"
                              )
        # self.window.columnconfigure(TitleFrameGridColumn, weight=1)
        self.window.columnconfigure(SelectionFrameGridColumn, weight=1)
        self.window.columnconfigure(SettingsFrameGridColumn, weight=4)
        """
        #######################################################################
        ############################ TITLE BAR ################################
        #######################################################################
        """
        
        SettingsIconGridRow = 0
        SettingsIconGridColumn = 0
        SettingsIconColumnSpan = 1
        SettingsIconRowSpan = 1
        
        if self.pr.draw_logo:
            self.icon_settings = tk.Label(self.title_frame, 
                                          image = self.pr.r.icon_settings_image, 
                                          background = self.pr.c.colour_prospero_blue, 
                                          anchor = "e", 
                                          padx = self.pr.c.padding_large, 
                                          pady = self.pr.c.padding_small)
            self.icon_settings.grid(row = SettingsIconGridRow,
                                    column = SettingsIconGridColumn,
                                    columnspan = SettingsIconColumnSpan,
                                    rowspan = SettingsIconRowSpan, 
                                    sticky = "nsew")
        
        MainTitleGridRow = SettingsIconGridRow
        MainTitleGridColumn = SettingsIconGridColumn + SettingsIconColumnSpan
        MainTitleColumnSpan = 1
        MainLogoRowSpan = SettingsIconRowSpan
        
        #Add the title next to it
        self.labelTitle = tk.Label(self.title_frame, 
                                   text="Settings",  
                                    background = self.pr.c.colour_prospero_blue, 
                                    foreground = self.pr.c.colour_offwhite_text, 
                                    padx=20, 
                                    pady=10, 
                                    font = self.pr.c.font_prospero_title, 
                                    anchor="w"
                                    ) 
        self.labelTitle.grid(row = MainTitleGridRow,
                            column = MainTitleGridColumn,
                            columnspan = MainTitleColumnSpan,
                            rowspan = MainLogoRowSpan, 
                            sticky = "nsew")
        
        self.title_frame.columnconfigure(MainTitleGridColumn, weight=0)
        """
        #######################################################################
        ########################## SELECTION TREE #############################
        #######################################################################
        """
        
        self.selection_treeview = ttk.Treeview(self.selection_frame, 
                                               show = "tree")
        
        self.selection_treeview.grid(row=0,column=0, columnspan=1, 
                                     rowspan=self.pr.c.columnspan_all, 
                                     **self.pr.c.grid_sticky_padding_small
                                     )
        self.selection_separator = ttk.Separator(self.selection_frame, 
                                                 orient = "vertical")
        self.selection_separator.grid(row=0, column=1, columnspan=1,
                                      rowspan = self.pr.c.columnspan_all,
                                      sticky="nesw")
        
        """
        #######################################################################
        ########################## SETTINGS TABS ##############################
        #######################################################################
        """
        self.settings_tabs = ttk.Notebook(self.window)
        
        nb_kwargs = {"master": self.settings_tabs, 
                     "bg": self.pr.c.colour_background}
        self.naming_settings = tk.Frame(**nb_kwargs)
        self.audio_functions_settings = tk.Frame(**nb_kwargs)
        self.tagging_settings = tk.Frame(**nb_kwargs)
        
        self.settings_tabs.add(self.naming_settings, text = "Naming")
        self.settings_tabs.add(self.audio_functions_settings, 
                               text = "Audio Functions")
        self.settings_tabs.add(self.tagging_settings, text = "Tagging")
        
        self.settings_tabs.grid(row = 1, column = 1, sticky="nesw")
        
    def start(self, trace = None):
        self.pr.f._log_trace(self, "start", trace)
        self.root.eval(f'tk::PlaceWindow {self.window} center')
        self.window.mainloop()
        
    def destroy(self, trace = None):
        self.pr.f._log_trace(self, "destroy", trace)
        self.window.destroy()
        
        

if __name__ == "__main__":
    class App:
        def __init__(self):
            self.pr = self
            self.root = tk.Tk()
            self.root.title("Prospero main window")
            self.testing_mode = True
            self.draw_logo = True
            
            self.f = prf.Functions(parent = self, trace = {"source": "initialise class", "parent": self.__class__.__name__})
            self.c = prc.Constants(parent = self, trace = {"source": "initialise class", "parent": self.__class__.__name__})
            self.r = prr.Resources(parent = self, trace = {"source": "initialise class", "parent": self.__class__.__name__})
            
            self.settings = Settings(self)
            self.settings.start()
    App()
            
            