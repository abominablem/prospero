# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 21:59:50 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")

import config

import prospero_constants as prc
import prospero_functions as prf
import prospero_resources as prr

from global_vars import LOG_LEVEL
from mh_logging import Logging, log_class
from tk_arrange import WidgetSet
log = Logging()

class SettingsWidget:
    """
    Wraps a tkinter widget and provides generic getter/setter methods.
    Must explicitly support a given tkinter widget type.
    """
    @log_class(LOG_LEVEL)
    def __init__(self, root, type, datatype = str, **kwargs):
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

    @log_class(LOG_LEVEL)
    def get_value(self):
        if self.type == "entry":
            v = self.widget.get()
        elif self.type == "checkbutton":
            v = (self.var.get() == 1)
        return self.datatype(v)

    @log_class(LOG_LEVEL)
    def set_value(self, value):
        if self.type == "entry":
            self.widget.delete(0, "end")
            self.widget.insert(0, value)
        elif self.type == "checkbutton":
            value = 1 if value == True else 0
            self.var.set(value)

    @log_class(LOG_LEVEL)
    def grid(self, **kwargs):
        self.widget.grid(**kwargs)



class SettingsTab:
    """
    Given a structured list of dictionaries describing a set of widgets,
    arranges the label/widget pairs in a frame. Provides methods to populate
    widgets based on specified value locations in the config, and save the
    updated values back to the config.
    """
    @log_class(LOG_LEVEL)
    def __init__(self, root, tab_list, kwargs_dict = None):
        self.name = self.__class__.__name__
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
            wrow = self.create_row(**row,
                                   frame = self.frame)
            wrow["label"].grid(row = i, column = 0,
                               **self.kwargs_dict["grid"])
            wrow["widget"].grid(row = i, column = 1,
                                **self.kwargs_dict["grid"])

        self.populate()

    @log_class(LOG_LEVEL)
    def create_row(self, label, type, location, datatype = str, frame = None):
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

    @log_class(LOG_LEVEL)
    def get_config_value(self, location):
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

    @log_class(LOG_LEVEL)
    def set_config_value(self, value, location):
        """
        Set the value at a given location in the config.
        """
        log.log_trace(self, "set_config_value", None,
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

    @log_class(LOG_LEVEL)
    def save(self):
        """
        Save all updated values in the widgets to the config file.
        """
        for label, widget in self.widgets.items():
            value = widget.get_value()
            location = self.locations[label]
            self.set_config_value(value, location)

    @log_class(LOG_LEVEL)
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
    @log_class(LOG_LEVEL)
    def __init__(self, parent, run_on_destroy = None):
        self.parent = parent
        self.root = parent.root
        self.pr = parent.pr
        self.name = self.__class__.__name__

        self.run_on_destroy = run_on_destroy

        self.window = tk.Toplevel(self.root,
                                  background = self.pr.c.colour_background)
        self.window.title("Prospero - Settings and config")

        frame_kwargs = {"bg": self.pr.c.colour_background}
        self.widget_frame = tk.Frame(self.window, **frame_kwargs)

        self.settings_icon = tk.Label(
            self.window, image = self.pr.r.icon_settings_image,
            background = self.pr.c.colour_prospero_blue, anchor = "e",
            padx = self.pr.c.padding_large, pady = self.pr.c.padding_small)

        #Add the title next to it
        self.title_label = tk.Label(
            self.window, text = "Settings",
            background = self.pr.c.colour_prospero_blue,
            foreground = self.pr.c.colour_offwhite_text,
            padx = 20, pady = 10, font = self.pr.c.font_prospero_title,
            anchor = "w")

        self.selection_treeview = ttk.Treeview(self.window, show = "tree")

        self.selection_separator = ttk.Separator(self.window, orient = "vertical")
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

        self.cancel_button = tk.Button(
            self.footer_frame,
            text = "Cancel",
            **self.pr.c.button_light_standard_args,
            command = self.destroy,
            width = 8
            )

        self.ok_button = tk.Button(
            self.footer_frame,
            text = "OK",
            **self.pr.c.button_light_standard_args,
            command = self.apply_and_exit,
            width = 8
            )

        widgets = {
            1: {'widget': self.settings_icon,
                'grid_kwargs': self.pr.c.grid_sticky},
            2: {'widget': self.title_label,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            3: {'widget': self.selection_treeview,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_height': True},
            4: {'widget': self.selection_separator,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_height': True},
            5: {'widget': self.settings_tabs,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True, 'stretch_height': True},
            6: {'widget': self.footer_frame,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            }

        self.widget_set = WidgetSet(self.widget_frame, widgets,
                                    layout = [[1, 2], [3, 4, 5], [6]])
        self.widget_set.grid(row = 0, column = 0, **self.pr.c.grid_sticky)
        self.window.rowconfigure(index = 0, weight = 1)
        self.window.columnconfigure(index = 0, weight = 1)

        """ ### POPULATE VALUES ### """
        self.populate_settings_list()
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)

    @log_class(LOG_LEVEL)
    def apply_settings(self, *args):
        for tab in self.SettingsTab_dict.values():
            tab.save()

    @log_class(LOG_LEVEL)
    def apply_and_exit(self, *args):
        self.apply_settings(*args)
        self.destroy(*args)

    @log_class(LOG_LEVEL)
    def populate_settings_list(self):
        for txt in self.tabs_dict:
            self.selection_treeview.insert("", index = "end",
                                           text = txt, iid = txt)

    @log_class(LOG_LEVEL)
    def start(self):
        self.root.eval('tk::PlaceWindow %s center' % str(self.window))
        self.window.attributes('-topmost', 'true')
        self.window.transient(self.root)
        self.window.grab_set()
        self.window.mainloop()

    @log_class(LOG_LEVEL)
    def destroy(self, *args):
        if not self.run_on_destroy is None:
            self.run_on_destroy()
        self.window.destroy()


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