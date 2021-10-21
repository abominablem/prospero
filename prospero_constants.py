# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 11:27:16 2021

@author: marcu
"""

import tkinter as tk
from tkinter import font

class Constants:
    def __init__(self, parent, trace = None):
        self.class_name = "Constants"
        self.pr = parent.pr
        self.root = parent.root
        self.pr.f._log_trace(self, "__init__", trace)
        
        """
        ### Constant definitions ###
        """
        self.padding_small = 5
        self.padding_medium = 8
        self.padding_large = 20
        
        self.columnspan_all = 100
        
        self.padding_small_top_only = (self.padding_small, 0)
        self.padding_small_bottom_only = (0, self.padding_small)
        self.padding_medium_top_only = (self.padding_medium, 0)
        self.padding_medium_bottom_only = (0, self.padding_medium)
        self.padding_large_top_only = (self.padding_large, 0)
        self.padding_large_bottom_only = (0, self.padding_large)
        
        self.padding_small_left_only = (self.padding_small, 0)
        self.padding_small_right_only = (0, self.padding_small)
        self.padding_medium_left_only = (self.padding_medium, 0)
        self.padding_medium_right_only = (0, self.padding_medium)
        self.padding_large_left_only = (self.padding_large, 0)
        self.padding_large_right_only = (0, self.padding_large)
        
        self.width_text_long = 400
        self.width_text_medium = 300
        self.width_text_short = 150
        self.width_text_veryshort = 100
        self.width_text_tiny = 50
        
        self.width_button_small = 5
        self.width_button_large = 35
        
        self.treeview_item_height = 20
        self.treeview_header_height = 20
        
        self.file_extension = ".mp3"
        # self.tag_list_alias = ["Album artist", "Album", "Track Number", 
        #                        "Track Title", "Recording artists", 
        #                        "Year", "Genre", "URL"]
        
        self.max_refresh_frequency_seconds = 0.15
        
        """
        ### COLOURS ###
        """        
        self.colour_background = "#fdfcf3"
        self.colour_offwhite_text = "#fefefe"
        self.colour_interface_button = "#baccbe"
        self.colour_prospero_blue = "#1c5689"
        self.colour_prospero_blue_pastel = "#5c86a0"
        self.colour_selection_background = "#225b8f"
        self.colour_box_interior = self.colour_offwhite_text
        self.colour_box_header = "#9ab2b0"
        self.colour_interest_point_light = "#d5e3cc"
        self.colour_prospero_secondary_dark = "#8d8c81"
        
        """
        ### FONTS ###
        """           
        self.font_prospero_title = tk.font.Font(self.root, family="Palatino Linotype", size=32, weight="bold")
        self.font_prospero_label_bold = tk.font.Font(self.root, family="Helvetica", size=16, weight="bold")
        self.font_prospero_text = tk.font.Font(self.root, family="Helvetica", size=10)
        self.font_prospero_box_header = tk.font.Font(self.root, family="Helvetica", size=12, weight="bold")
        self.font_prospero_interface_button = tk.font.Font(self.root, family="Helvetica", size=16, weight="bold")
        self.font_prospero_interface_button_light = tk.font.Font(self.root, family="Helvetica", size=10)

        """
        ### KWARGS ###
        """        
        self.label_standard_args = {"background" : self.colour_background,
                                    "font" : self.font_prospero_label_bold,
                                    "anchor" : "w"
                                    }
            
        self.grid_sticky_padding_small = {"sticky" : "nesw", 
                                         "pady" : self.padding_small,
                                         "padx" : self.padding_small
                                         }
                                     
        self.grid_sticky = {"sticky" : "nesw"}
        
        self.button_standard_args = {"background" : self.colour_interface_button, 
                                    "font" : self.font_prospero_interface_button
                                    }
        
        self.button_light_standard_args = {"background" : self.colour_interface_button, 
                                            "font" : self.font_prospero_interface_button_light
                                            }
        
        self.entry_medium_args = {"width" : 100, 
                                  "borderwidth" : 2,
                                  "background" : self.colour_box_interior
                                  }
        
        self.entry_large_args = {"width" : 150, 
                                "borderwidth" : 2, 
                                "background" : self.colour_box_interior
                                }