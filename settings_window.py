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

from mh_logging import Logging

log = Logging()

class SettingsWidget:
    """
    Wraps a tkinter widget and provides generic getter/setter methods.
    Must explicitly support a given tkinter widget type.
    """
    def __init__(self, root, type, trace = None, datatype = str, **kwargs):
        log.log_trace(self, "__init__", trace)
        self.root = root
        self.type = type.lower()
        self.datatype = datatype

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

    def get_value(self, trace = None):
        log.log_trace(self, "get_value", trace)
        if self.type == "entry":
            v = self.widget.get()
        elif self.type == "checkbutton":
            v = (self.var.get() == 1)
        return self.datatype(v)

    def set_value(self, value, trace = None):
        log.log_trace(self, "set_value", trace)
        if self.type == "entry":
            self.widget.delete(0, "end")
            self.widget.insert(0, value)
        elif self.type == "checkbutton":
            value = 1 if value == True else 0
            self.var.set(value)

    def grid(self, trace = None, **kwargs):
        log.log_trace(self, "grid", trace)
        self.widget.grid(**kwargs)


class SettingsTab:
    """
    Given a structured list of dictionaries describing a set of widgets,
    arranges the label/widget pairs in a frame. Provides methods to populate
    widgets based on specified value locations in the config, and save the
    updated values back to the config.
    """
    def __init__(self, root, tab_list, kwargs_dict = None, trace = None):
        log.log_trace(self, "__init__", trace)
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

    def create_row(self, label, type, location, datatype = str, frame = None,
                   trace = None):
        """
        Create a label and widget pair tied to a specific location in the
        config file and widget type. Optionally, specify a frame to add the
        widget to for alignment purposes.
        """
        log.log_trace(self, "create_row", trace)
        if frame is None:
            row_frame = tk.Frame(self.frame, **self.kwargs_dict["frame"])
        else:
            row_frame = frame

        label = tk.Label(row_frame, text = label, **self.kwargs_dict["label"])

        widget = SettingsWidget(row_frame, type, datatype = datatype,
                                **self.kwargs_dict[type])

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
        log.log_trace(self, "get_config_value", trace)

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
        if value == "D:/Users/Marcus/Documents/R Documents/Music/Test":
            print("123")
            pass
        log.log_trace(self, "set_config_value", trace,
                      add = "Updated config value at location %s to %s"
                          % (".".join(location), value)
                      )
        file = location[0]
        if file == "config":
            vdict = config.config.config_dict
        else:
            raise ValueError("Unknown config location")

        for i, key in enumerate(location[1:]):
            if i != len(location) - 2:
                vdict = vdict[key]
            else:
                vdict[key] = value

    def save(self, trace = None):
        """
        Save all updated values in the widgets to the config file.
        """
        log.log_trace(self, "save", trace)

        for label, widget in self.widgets.items():
            value = widget.get_value()
            location = self.locations[label]
            self.set_config_value(value, location)

    def populate(self, trace = None):
        """
        Populate widgets with the current config values.
        """
        log.log_trace(self, "populate", trace)

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

        self.settings_tabs.grid(row = 1, column = 1,
                                columnspan = self.pr.c.columnspan_all,
                                sticky = "nesw")


        self.entries = {
            "Naming": [
                {"label": "Base input directory",
                 "type": "entry",
                 "datatype": str,
                 "location": ["config", "Naming", "base_input_directory"]},
                {"label": "Base output directory",
                 "type": "entry",
                 "datatype": str,
                 "location": ["config", "Naming", "base_output_directory"]},
                {"label": "Save table on close",
                 "type": "checkbutton",
                 "datatype": bool,
                 "location": ["config", "Naming", "FileListTreeview",
                              "save_on_close"]},
                {"label": "Check if URL is word",
                 "type": "checkbutton",
                 "datatype": bool,
                 "location": ["config", "Naming", "do_url_word_check"]}
                ],
            "Audio Functions": [
                {"label": "Base input directory",
                 "type": "entry",
                 "datatype": str,
                 "location": ["config", "AudioFunctions",
                              "base_input_directory"]},
                {"label": "Base output directory",
                 "type": "entry",
                 "datatype": str,
                 "location": ["config", "AudioFunctions",
                              "base_output_directory"]},
                {"label": "Rewind seconds",
                 "type": "entry",
                 "datatype": int,
                 "location": ["config", "AudioFunctions", "AudioInterface",
                              "rewind_seconds"]},
                {"label": "Fast forward seconds",
                 "type": "entry",
                 "datatype": int,
                 "location": ["config", "AudioFunctions", "AudioInterface",
                              "fast_forward_seconds"]},
                {"label": "Breakpoint grace period",
                 "type": "entry",
                 "datatype": int,
                 "location": ["config", "AudioFunctions", "AudioInterface",
                              "breakpoint_grace_period"]}
                ],
            "Tagging": [
                {"label": "Base input directory",
                 "type": "entry",
                 "datatype": str,
                 "location": ["config", "Tagging", "base_input_directory"]},
                {"label": "Base output directory",
                 "type": "entry",
                 "datatype": str,
                 "location": ["config", "Tagging", "base_output_directory"]}
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

        self.footer_frame = tk.Frame(
            self.window,
            background = self.pr.c.colour_prospero_blue
            )

        self.apply_button = tk.Button(
            self.footer_frame,
            text = "Apply",
            **self.pr.c.button_light_standard_args,
            command = self.apply_settings,
            width = 8
            )
        self.apply_button.grid(row = 0, column = 1,
                               **self.pr.c.grid_sticky_padding_small)

        self.cencel_button = tk.Button(
            self.footer_frame,
            text = "Cancel",
            **self.pr.c.button_light_standard_args,
            command = self.destroy,
            width = 8
            )
        self.cencel_button.grid(row = 0, column = 2,
                               **self.pr.c.grid_sticky_padding_small)

        self.ok_button = tk.Button(
            self.footer_frame,
            text = "OK",
            **self.pr.c.button_light_standard_args,
            command = self.apply_and_exit,
            width = 8
            )
        self.ok_button.grid(row = 0, column = 3,
                               **self.pr.c.grid_sticky_padding_small)

        self.footer_frame.grid(row = 2, column = 0,
                               columnspan = self.pr.c.columnspan_all,
                               **self.pr.c.grid_sticky)




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
        self.footer_frame.columnconfigure(0, weight = 1)
        self.footer_frame.columnconfigure(1, weight = 0)
        self.footer_frame.columnconfigure(2, weight = 0)
        self.footer_frame.columnconfigure(3, weight = 0)

        """
        #######################################################################
        ######################## POPULATE VALUES ##############################
        #######################################################################
        """
        self.populate_settings_list()
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)

    def apply_settings(self, *args, trace = None):
        self.pr.f._log_trace(self, "apply_settings", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".apply_settings"}
        for tab in self.SettingsTab_dict.values():
            tab.save(trace = inf_trace)

    def apply_and_exit(self, *args, trace = None):
        self.pr.f._log_trace(self, "apply_and_exit", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".apply_and_exit"}
        self.apply_settings(*args, trace = inf_trace)
        self.destroy(*args, trace = inf_trace)

    def populate_settings_list(self, trace = None):
        self.pr.f._log_trace(self, "populate_settings_list", trace)
        for txt in self.tabs_dict:
            self.selection_treeview.insert("", index = "end",
                                           text = txt, iid = txt)

    def start(self, trace = None):
        self.pr.f._log_trace(self, "start", trace)
        self.root.eval(f'tk::PlaceWindow {self.window} center')
        self.window.mainloop()
        
    def destroy(self, *args, trace = None):
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

            config.config.dump_values()
    App()