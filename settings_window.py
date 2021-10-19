# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 21:59:50 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk

import config

import prospero_constants as prc
import prospero_functions as prf
import prospero_resources as prr


class SettingsWidget:
    """
    Wraps a tkinter widget and provides generic getter/setter methods.
    Must explicitly support a given tkinter widget type.
    """
    def __init__(self, root, type, trace = None, **kwargs):
        self.root = root
        self.type = type.lower()

        if self.type == "entry":
            self.widget = tk.Entry(
                self.root,
                **kwargs
                )
        elif self.type == "checkbutton":
            self.var = tk.IntVar()
            self.widget = tk.Checkbutton(
                self.root,
                **kwargs,
                variable = self.var
                )
        else:
            raise ValueError("Unsupported widget type %s" % type)

    def get_value(self):
        if self.type == "entry":
            return self.widget.get()
        elif self.type == "checkbox":
            return (self.var.get() == 1)

    def set_value(self, value):
        if self.type == "entry":
            self.widget.delete(0, "end")
            self.widget.insert(0, value)
        elif self.type == "checkbox":
            value = 1 if value == True else 0
            return self.var.set(value)

    def grid(self, **kwargs):
        self.widget.grid(**kwargs)


class SettingsTab:
    """
    Given a structured list of dictionaries describing a set of widgets,
    arranges the label/widget pairs in a frame. Provides methods to populate
    widgets based on specified value locations in the config, and save the
    updated values back to the config.
    """
    def __init__(self, root, tab_list, kwargs_dict = None, trace = None):
        self.name = self.__class__.__name__
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        self.root = root
        self.tab_list = tab_list
        self.widgets = {}
        self.locations = {}

        for key in ["frame", "entry", "label", "checkbutton", "grid"]:
                kwargs_dict.setdefault(key, {})
        self.kwargs_dict = kwargs_dict

        self.frame = tk.Frame(self.root, **self.kwargs_dict["frame"])
        self.frame.grid(row = 0, column = 0)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.rowconfigure(0, weight = 1)

        for i, row in enumerate(tab_list):
            wrow = self.create_row(**row, trace = inf_trace,
                                   frame = self.frame)
            wrow["label"].grid(row = i, column = 0,
                               **self.kwargs_dict["grid"])
            wrow["widget"].grid(row = i, column = 1,
                                **self.kwargs_dict["grid"])

        self.populate()

    def create_row(self, label, type, location, trace = None,
                   frame = None):
        """
        Create a label and widget pair tied to a specific location in the
        config file and widget type. Optionally, specify a frame to add the
        widget to for alignment purposes.
        """
        if frame is None:
            row_frame = tk.Frame(self.frame, **self.kwargs_dict["frame"])
        else:
            row_frame = frame

        label = tk.Label(row_frame, text = label, **self.kwargs_dict["label"])

        # cur_value = self.get_value(location, trace = inf_trace)

        widget = SettingsWidget(row_frame, type, **self.kwargs_dict[type])

        label.grid(row = 0, column = 0, **self.kwargs_dict["grid"])
        widget.grid(row = 0, column = 1, **self.kwargs_dict["grid"])
        self.widgets[label] = widget
        self.locations[label] = location

        if frame is None:
            row_frame.columnconfigure(0, weight = 0)
            row_frame.columnconfigure(1, weight = 1)
            return row_frame
        else:
            return {"label": label,
                    "widget": widget}

    def get_config_value(self, location, trace = None):
        """
        Get the value at a given location in the config. Location is a list, 
        with the first entry specifying the file, and all others iterating
        through dictionary layers.
        """
        file = location[0]
        if file == "config":
            value = config.config.config_dict
        else:
            raise ValueError("Unknown config location")

        for key in location[1:]:
            value = value[key]

        return value

    def set_config_value(self, value, location, trace = None):
        """
        Set the value at a given location in the config.
        """
        file = location[0]
        if file == "config":
            vdict = config.config.config_dict
        else:
            raise ValueError("Unknown config location")

        last_key = len(location[1:]) - 1
        for i, key in enumerate(location[1:]):
            if i != last_key:
                vdict = vdict[key]
            else:
                vdict[key] = value

    def save(self):
        """
        Save all updated values in the widgets to the config file.
        """
        for label, widget in self.widgets.items():
            value = widget.get_value()
            location = self.locations[label]
            self.set_config_value(value, location)

    def populate(self):
        """
        Populate widgets with the current config values.
        """
        for label, widget in self.widgets.items():
            location = self.locations[label]
            value = self.get_config_value(location)
            widget.set_value(value)


class Settings:
    """
    Toplevel class wrapping the Settings window. This allows interaction with
    the underlying config JSON.
    """
    def __init__(self, parent, trace = None):
        self.parent = parent
        self.root = parent.root
        self.pr = parent.pr
        self.name = self.__class__.__name__
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        
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
        """
        #######################################################################
        ############################ TITLE BAR ################################
        #######################################################################
        """
        
        SettingsIconGridRow = 0
        SettingsIconGridColumn = 0
        SettingsIconColumnSpan = 1
        SettingsIconRowSpan = 1

        try:
            if self.pr.draw_logo:
                self.icon_settings = tk.Label(
                    self.title_frame,
                    image = self.pr.r.icon_settings_image,
                    background = self.pr.c.colour_prospero_blue, 
                    anchor = "e", 
                    padx = self.pr.c.padding_large, 
                    pady = self.pr.c.padding_small
                    )
                self.icon_settings.grid(row = SettingsIconGridRow,
                                        column = SettingsIconGridColumn,
                                        columnspan = SettingsIconColumnSpan,
                                        rowspan = SettingsIconRowSpan, 
                                        sticky = "nsew")
        except tk.TclError:
            pass

        MainTitleGridRow = SettingsIconGridRow
        MainTitleGridColumn = SettingsIconGridColumn + SettingsIconColumnSpan
        MainTitleColumnSpan = 1
        MainLogoRowSpan = SettingsIconRowSpan
        
        #Add the title next to it
        self.labelTitle = tk.Label(
            self.title_frame,
            text = "Settings",
            background = self.pr.c.colour_prospero_blue,
            foreground = self.pr.c.colour_offwhite_text,
            padx = 20,
            pady = 10,
            font = self.pr.c.font_prospero_title, 
            anchor = "w"
            ) 
        self.labelTitle.grid(row = MainTitleGridRow,
                            column = MainTitleGridColumn,
                            columnspan = MainTitleColumnSpan,
                            rowspan = MainLogoRowSpan, 
                            sticky = "nsew")

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

        # tab_kwargs = {"state": "hidden"}
        tab_kwargs = {}

        self.tabs_dict = {"Naming": self.naming_settings,
                          "Audio Functions": self.audio_functions_settings,
                          "Tagging": self.tagging_settings}

        for tab in self.tabs_dict:
            self.settings_tabs.add(self.tabs_dict[tab],
                                   text = tab, **tab_kwargs)

        self.settings_tabs.grid(row = 1, column = 1, sticky = "nesw")


        self.entries = {
            "Naming": [
                {"label": "Base input directory",
                 "type": "entry",
                 "location": ["config", "Naming", "base_input_directory"]},
                {"label": "Base output directory",
                 "type": "entry",
                 "location": ["config", "Naming", "base_output_directory"]},
                {"label": "Save table on close",
                 "type": "checkbutton",
                 "location": ["config", "Naming", "FileListTreeview",
                              "save_on_close"]},
                {"label": "Check if URL is word",
                 "type": "checkbutton",
                 "location": ["config", "Naming", "do_url_word_check"]}
                ],
            "Audio Functions": [
                {"label": "Base input directory",
                 "type": "entry",
                 "location": ["config", "Naming", "base_input_directory"]},
                {"label": "Base output directory",
                 "type": "entry",
                 "location": ["config", "Naming", "base_output_directory"]}
                ],
            "Tagging": [
                {"label": "Base input directory",
                 "type": "entry",
                 "location": ["config", "Naming", "base_input_directory"]},
                {"label": "Base output directory",
                 "type": "entry",
                 "location": ["config", "Naming", "base_output_directory"]}
                ]
            }

        self.SettingsTab_dict = {}

        self.kwargs_dict = {"grid": self.pr.c.grid_sticky_padding_small,
                            "entry": self.pr.c.entry_large_args,
                            "frame": {"bg": self.pr.c.colour_background},
                            "checkbutton": {"bg": self.pr.c.colour_background,
                                            "anchor": "w"},
                            "label": self.pr.c.label_standard_args,
                            "button": self.pr.c.button_standard_args}

        for tab in self.entries:
            self.SettingsTab_dict[tab] = SettingsTab(
                root = self.tabs_dict[tab],
                tab_list = self.entries[tab],
                kwargs_dict = self.kwargs_dict,
                trace = inf_trace
                )


        """
        #######################################################################
        ######################## ALLOCATE SCALING #############################
        #######################################################################
        """
        self.window.columnconfigure(TitleFrameGridColumn, weight=1)
        self.window.columnconfigure(SelectionFrameGridColumn, weight=1)
        self.window.columnconfigure(SettingsFrameGridColumn, weight=4)
        self.selection_frame.columnconfigure(0, weight=1)
        self.selection_frame.columnconfigure(1, weight=0)
        self.title_frame.columnconfigure(MainTitleGridColumn, weight=0)

        """
        #######################################################################
        ######################## POPULATE VALUES ##############################
        #######################################################################
        """
        self.populate_settings_list()
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)

    def populate_settings_list(self, trace = None):
        self.pr.f._log_trace(self, "populate_settings_list", trace)
        for txt in self.tabs_dict:
            self.selection_treeview.insert("", index = "end",
                                           text = txt, iid = txt)

    def start(self, trace = None):
        self.pr.f._log_trace(self, "start", trace)
        self.root.eval(f'tk::PlaceWindow {self.window} center')
        self.window.mainloop()
        
    def destroy(self, trace = None):
        self.pr.f._log_trace(self, "destroy", trace)
        self.window.destroy()
        self.root.destroy()


if __name__ == "__main__":
    class App:
        def __init__(self):
            self.pr = self
            self.root = tk.Tk()
            self.root.title("Prospero main window")
            self.testing_mode = True
            self.draw_logo = True
            
            self.f = prf.Functions(parent = self)
            self.c = prc.Constants(parent = self)
            self.r = prr.Resources(parent = self)
            self.settings = Settings(self)
            self.settings.start()
    App()