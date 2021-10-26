# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 23:22:23 2021

@author: marcu
"""
# package imports
import tkinter as tk
from tkinter import ttk

# custom imports
import prospero_constants as prc
import prospero_functions as prf
import prospero_resources as prr
from tab_tagging import Tagging
from tab_naming import Naming
from tab_audio_functions import AudioFunctions
from value_insight import Insight
from settings_window import Settings
import config
# function imports

class Prospero:
    def __init__(self, trace):
        self.pr = self
        self.root = tk.Tk()
        self.name = self.__class__.__name__
        
        self.testing_mode = True
        self.draw_logo = True
        self.running = True
        
        self.f = prf.Functions(parent = self, 
                               trace = {"source": "initialise class", 
                                        "parent": self.name})
        
        self.c = prc.Constants(parent = self,
                               trace = {"source": "initialise class", 
                                        "parent": self.name})
        
        self.r = prr.Resources(parent = self, 
                               trace = {"source": "initialise class", 
                                        "parent": self.name})

        self.insight_rn = Insight(type = "renames",
                                  debug = self.testing_mode,
                                  trace = {"source": "initialise class", 
                                           "parent": self.name})
                                           
        self.insight_rn.define_field_map({"Original name": "original_name",
                                          "#0": "original_name",
                                          "Composer": "composer",
                                          "Album": "album",
                                          "#": "number",
                                          "Track": "track",
                                          "Performer(s)": "performers",
                                          "Year": "year",
                                          "Genre": "genre",
                                          "URL": "url",
                                          "Final name": "final_name"})
        
        self.f._log_trace(self, "__init__", trace)
        
        self.root.title("Prospero - MP3 file handling and ID3v2 tagging")
        self.root.configure(background = self.c.colour_background, 
                            padx=15, pady=10)
        
        self._style()
        """
        #######################################################################
        ############################ HEADER BAR ###############################
        #######################################################################
        """
        HeaderFrameGridRow = 0
        HeaderFrameGridColumn = 0
        HeaderFrameColumnSpan = 1 
        HeaderFrameRowSpan = 1
        
        self.header_frame = tk.Frame(self.root, 
                                     bg = self.c.colour_prospero_blue)
        self.header_frame.grid(row = HeaderFrameGridRow,
                               column = HeaderFrameGridColumn,
                               columnspan = HeaderFrameColumnSpan,
                               rowspan = HeaderFrameRowSpan,
                               sticky = "nsew")
        """
        #########################
        ######### LOGOS #########
        #########################
        """
        
        MainLogoGridRow = 0
        MainLogoGridColumn = 0
        MainLogoColumnSpan = 1
        MainLogoRowSpan = 1
        
        if self.draw_logo:
            #errors cause the image import to fail until the kernel is 
            #restarted. For simplicity while testing, disable the logo
            
            self.root.iconphoto(False, self.r.logo_circular_small)
            #Add the logo in the top left position
            imgLogo = tk.Label(self.header_frame, 
                               image = self.r.logo_circular_small_padded, 
                               background = self.c.colour_prospero_blue, 
                               anchor="w", 
                               padx = self.c.padding_large, 
                               pady = self.c.padding_small)
            imgLogo.grid(row = MainLogoGridRow, column = MainLogoGridColumn, 
                         sticky = "nesw")
            
            
        
        """
        #######################################################################
        ############################ TITLE BAR ################################
        #######################################################################
        """
        
        MainTitleGridRow = MainLogoGridRow
        MainTitleGridColumn = MainLogoGridColumn + MainLogoColumnSpan
        MainTitleColumnSpan = 1
        MainTitleRowSpan = MainLogoRowSpan
        
        #Add the title next to it
        labelTitle = tk.Label(self.header_frame, text="Prospero",  
                              background = self.c.colour_prospero_blue, 
                              foreground = self.c.colour_offwhite_text, 
                              padx=20, 
                              pady=10, 
                              font = self.c.font_prospero_title, 
                              anchor="w"
                              ) 
        labelTitle.grid(row = MainTitleGridRow,
                        column = MainTitleGridColumn,
                        columnspan = MainTitleColumnSpan,
                        rowspan = MainTitleRowSpan, 
                        sticky = "nsew")
        
        """
        ############################
        ######### SETTINGS #########
        ############################
        """
        
        SettingsIconGridRow = MainLogoGridRow
        SettingsIconGridColumn = MainTitleGridColumn + MainTitleColumnSpan
        SettingsIconColumnSpan = 1
        SettingsIconRowSpan = MainLogoRowSpan
        
        if self.draw_logo:
            self.icon_settings = tk.Label(
                self.header_frame, 
                image = self.r.icon_settings_image, 
                background = self.c.colour_prospero_blue, 
                anchor = "e", 
                padx = self.c.padding_large, 
                pady = self.c.padding_small
                )
            
            self.icon_settings.grid(row = SettingsIconGridRow,
                                    column = SettingsIconGridColumn,
                                    columnspan = SettingsIconColumnSpan,
                                    rowspan = SettingsIconRowSpan, 
                                    sticky = "nsew")

            self.icon_settings.bind(
                "<1>",
                lambda event: self.open_settings(
                    event,
                    trace = {"source": "bound event",
                             "widget": self.name + ".icon_settings",
                             "event": "<1>"}
                    )
                )
        """
        #######################################################################
        ############################ NOTEBOOK #################################
        #######################################################################
        """
        
        NotebookGridRow = HeaderFrameGridRow + HeaderFrameRowSpan
        NotebookGridColumn = HeaderFrameGridColumn
        NotebookColumnSpan = HeaderFrameColumnSpan
        NotebookRowSpan = 1
        
        notebook = ttk.Notebook(self.root)
        notebook.grid(row = NotebookGridRow,
                      column = NotebookGridColumn,
                      columnspan = NotebookColumnSpan,
                      rowspan = NotebookRowSpan,
                      **self.c.grid_sticky_padding_small
                      )
        
        self.tab_naming = tk.Frame(notebook, bg = self.c.colour_background)
        self.tab_audio_functions = tk.Frame(notebook, 
                                            bg = self.c.colour_background)
        self.tab_tagging = tk.Frame(notebook, bg = self.c.colour_background)
        
        notebook.add(self.tab_naming, text = "Naming")
        notebook.add(self.tab_audio_functions, text = "Audio Functions")
        notebook.add(self.tab_tagging, text = "Tagging")
        
        taggingGridRow = NotebookGridRow + 1
        taggingGridColumn = 0
        self.tagging = Tagging(parent = self, 
                               grid_references = [taggingGridRow, 
                                                  taggingGridColumn
                                                  ], 
                               trace = {"source": "initialise class", 
                                        "parent": self.name})
        
        namingGridRow = NotebookGridRow + 1
        namingGridColumn = taggingGridColumn
        self.naming = Naming(parent = self, 
                             grid_references = [namingGridRow, 
                                                namingGridColumn
                                                ], 
                             trace = {"source": "initialise class", 
                                      "parent": self.name})
        
        AudioFunctionsGridRow = NotebookGridRow + 1
        AudioFunctionsGridColumn = taggingGridColumn
        self.audio_functions = AudioFunctions(
            parent = self, 
            grid_references = [AudioFunctionsGridRow, 
                               AudioFunctionsGridColumn
                               ], 
            trace = {"source": "initialise class", 
                     "parent": self.name}
            )
        """
        #######################################################################
        ################################ RESIZING RATIOS ######################
        #######################################################################
        """
        #keep the logo the same size
        #allocate all extra space to the main title
        self.header_frame.columnconfigure(MainLogoGridColumn, weight=0) 
        self.header_frame.columnconfigure(MainTitleGridColumn, weight=1) 
        self.header_frame.columnconfigure(SettingsIconGridColumn, weight=0)
        
        self.header_frame.rowconfigure(MainLogoGridRow, weight=0)
        self.root.rowconfigure(HeaderFrameGridRow, weight=0)
        self.root.columnconfigure(HeaderFrameGridColumn, weight=1)
        self.root.rowconfigure(NotebookGridRow, weight=1)
        
        #handles the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.destroy) 
        
    def _style(self, trace = None):
        self.pr.f._log_trace(self, "_style", trace)
        
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

    def start(self, trace = None):
        self.pr.f._log_trace(self, "start", trace) 
        
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()
        
    def destroy(self, event = None, trace = None):
        self.pr.f._log_trace(self, "destroy", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".destroy"}
        
        self.running = False
        self.audio_functions.audio_interface.end_audio_process(trace = 
                                                               inf_trace)
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

    def open_settings(self, event = None, trace = None):
        self.pr.f._log_trace(self, "open_settings", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".open_settings"}
        self.settings = Settings(self, trace = inf_trace,
                                 run_on_destroy = self.apply_settings)
        self.settings.start(trace = inf_trace)

    def apply_settings(self, event = None, trace = None):
        self.pr.f._log_trace(self, "apply_settings", trace)
        inf_trace = {"source": "open_settings call",
                     "parent": self.name + ".apply_settings"}
        # Update the settings changed for each tab
        self.audio_functions.load_from_config(trace = inf_trace)
        self.audio_functions.audio_interface.load_from_config(trace = inf_trace)
        self.naming.load_from_config(trace = inf_trace)
        self.tagging.load_from_config(trace = inf_trace)

        self.audio_functions.io_directory.load_from_config(trace = inf_trace)
        self.naming.io_directory.load_from_config(trace = inf_trace)
        self.tagging.io_directory.load_from_config(trace = inf_trace)




prospero = Prospero(trace = {"source": "initialise class",
                             "parent": __name__})
prospero.start()