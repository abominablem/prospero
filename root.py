# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 23:22:23 2021

@author: marcu
"""
# package imports
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")

# custom imports
import prospero_constants as prc
import prospero_functions as prf
import prospero_resources as prr
from tab_tagging import Tagging
from tab_naming import Naming
from tab_audio_functions import AudioFunctions
from value_insight import Insight
from settings_window import Settings
from tk_arrange import WidgetSet
import config
from mh_logging import log_class
from global_vars import LOG_LEVEL

class Prospero:
    @log_class(LOG_LEVEL)
    def __init__(self):
        self.pr = self
        self.root = tk.Tk()

        self.testing_mode = True
        self.running = True
        self.start_time = datetime.now()

        self.f = prf.Functions(parent = self)
        self.c = prc.Constants(parent = self)
        self.r = prr.Resources(parent = self)

        self.insight_rn = Insight(type = "renames", debug = self.testing_mode)

        self.insight_rn.define_field_map({
            "Original name": "original_name",
            "#0": "original_name",
            "Composer": "composer",
            "Album": "album",
            "#": "number",
            "Track": "track",
            "Performer(s)": "performers",
            "Year": "year",
            "Genre": "genre",
            "URL": "url",
            "Final name": "final_name"}
            )

        self.root.title("Prospero - MP3 file handling and ID3v2 tagging")
        self.root.configure(bg = self.c.colour_background,
                            padx = 0,
                            pady = 0)

        self.widget_frame = tk.Frame(self.root,
                                     bg = self.pr.c.colour_background)
        self._style()

        self.root.iconphoto(True, self.r.logo_circular_small)
        #Add the logo in the top left position
        self.logo_image = tk.Label(
            self.widget_frame,
            image = self.r.logo_circular_small_padded,
            background = self.c.colour_prospero_blue,
            anchor="w",
            padx = self.c.padding_large,
            pady = self.c.padding_small
            )
        self.title = tk.Label(
            self.widget_frame,
            text = "Prospero",
            background = self.c.colour_prospero_blue,
            foreground = self.c.colour_offwhite_text,
            padx = 20,
            pady = 10,
            font = self.c.font_prospero_title,
            anchor = "w"
            )
        self.icon_settings = tk.Label(
            self.widget_frame,
            image = self.r.icon_settings_image,
            background = self.c.colour_prospero_blue,
            anchor = "e",
            padx = self.c.padding_large,
            pady = self.c.padding_small
            )
        self.icon_settings.bind("<1>", self.open_settings)

        self.notebook = ttk.Notebook(self.widget_frame)

        self.tab_naming = tk.Frame(
            self.notebook, bg = self.c.colour_background)
        self.tab_audio_functions = tk.Frame(
            self.notebook, bg = self.c.colour_background)
        self.tab_tagging = tk.Frame(
            self.notebook, bg = self.c.colour_background)

        self.notebook.add(self.tab_naming, text = "Naming")
        self.notebook.add(self.tab_audio_functions, text = "Audio Functions")
        self.notebook.add(self.tab_tagging, text = "Tagging")

        self.tagging = Tagging(parent = self)
        self.naming = Naming(parent = self)
        self.audio_functions = AudioFunctions(parent = self)

        widgets = {1: {'widget': self.logo_image,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   2: {'widget': self.title,
                       'grid_kwargs': self.pr.c.grid_sticky,
                       'stretch_width': True},
                   3: {'widget': self.icon_settings,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   4: {'widget': self.notebook,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                       'stretch_width': True, 'stretch_height': True},
                   }
        self.widget_set = WidgetSet(self.widget_frame,
                                    widgets,
                                    layout = [[1, 2, 3],
                                              [4]]
                                    )
        self.widget_set.grid(row = 0, column = 0, **self.pr.c.grid_sticky)
        self.root.rowconfigure(0, weight = 1)
        self.root.columnconfigure(0, weight = 1)

        #handles the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)

    @log_class(LOG_LEVEL)
    def _style(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        #This handles the styling for the Treeview HEADER
        self.style.configure("TTreeview.Header",
                             background = self.c.colour_box_header,
                             rowheight = self.c.treeview_header_height,
                             font = self.c.font_prospero_box_header)
        #This handles the styling for the Treeview BODY
        self.style.configure("TTreeview",
                             background = self.c.colour_box_interior,
                             fieldbackground = self.c.colour_box_interior,
                             rowheight = self.c.treeview_item_height,
                             font = self.c.font_prospero_text)
        #This handles the styling for Frames
        self.style.configure("TFrame", background = self.c.colour_background)
        #This handles the styling for Labels
        self.style.configure("TLabel", background = self.c.colour_background)
        #This handles the styling for the Notebook tabs
        self.style.configure("TNotebook.Tab",
                             background = self.c.colour_interest_point_light,
                             font = self.c.font_prospero_text)
        #This handles the styling for the Notebook background
        self.style.configure("TNotebook",
                             background = self.c.colour_background,
                             font = self.c.font_prospero_text)
        #Change the coloure of the selected item
        self.style.map("TTreeview", background = [('selected', self.c.colour_selection_background)])
        self.style.map("TNotebook.Tab", background = [('selected', self.c.colour_prospero_blue_pastel)])
        self.style.map("TNotebook.Tab", foreground = [('selected', self.c.colour_offwhite_text)])

    @log_class(LOG_LEVEL)
    def start(self):
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

    @log_class(LOG_LEVEL)
    def destroy(self, event = None):
        self.running = False
        self.audio_functions.audio_interface.end_audio_process()
        self.insight_rn.close()
        self.root.quit()
        self.root.destroy()
        # dump config values for next time
        config.config.dump_values()
        config.composers_dict.dump_values()
        config.keyword_dict.dump_values()
        config.genres_dict.dump_values()
        config.numerals_dict.dump_values()
        return event

    @log_class(LOG_LEVEL)
    def open_settings(self, event = None):
        self.settings = Settings(self, run_on_destroy = self.apply_settings)
        self.settings.start()

    @log_class(LOG_LEVEL)
    def apply_settings(self, event = None):
        # Update the settings changed for each tab
        self.audio_functions.load_from_config()
        self.audio_functions.audio_interface.load_from_config()
        self.naming.load_from_config()
        self.tagging.load_from_config()

        self.audio_functions.io_directory.load_from_config()
        self.naming.io_directory.load_from_config()
        self.tagging.io_directory.load_from_config()

prospero = Prospero()
prospero.start()