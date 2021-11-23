# -*- coding: utf-8 -*-
"""
Created on Sat May 15 16:35:32 2021

@author: marcu
"""
from pydub import AudioSegment
import tkinter as tk
from datetime import datetime
import threading
import os
import copy
import re

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from io_directory import IODirectory
from value_from_filename import ValueFromFilename
from audio_interface import AudioInterface, ProgressBar
from search_box import SearchBox
from arrange_widgets import WidgetSet
import config
import described_widgets as dw
from mh_logging import Logging

# #### REQUIRED ####
# conda install ffmpeg

class AudioFunctions():
    def __init__(self, parent, trace = None):
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab_audio_functions
        self.name = self.__class__.__name__

        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".__init__"}

        self.executing = False

        frame_kwargs = {"bg": self.pr.c.colour_background}
        self.widget_frame = tk.Frame(self.tab, **frame_kwargs)

        self.io_directory = IODirectory(
            parent = self,
            master = self.widget_frame,
            trace = inf_trace,
            call_after_input = self.populate_input_files
            )

        self._colour_breakpoint = "#bfb598"

        self.visual_frame = tk.Frame(
            self.widget_frame,
            bg = self.pr.c.colour_background,
            highlightthickness = 1,
            highlightcolor = self.pr.c.colour_selection_background)

        self.visual_frame.rowconfigure(0, weight = 1)
        self.visual_frame.columnconfigure(0, weight = 1)

        self.audio_canvas = AudioCanvas(
            self.visual_frame,
            waveform_colour = self.pr.c.colour_prospero_blue_pastel,
            background_colour = self.pr.c.colour_background
            )

        self.audio_interface = AudioInterface(
            parent = self,
            master = self.widget_frame,
            audio_breakpoints = self.audio_canvas.breakpoints,
            trace = {"source": "initialise class", "parent": self.name}
            )

        self.search_box = SearchBox(
            parent = self,
            master = self.widget_frame,
            trace = inf_trace
            )

        self.waveform = None
        self._control_pressed = False
        self._shift_pressed = False
        self._alt_pressed = False
        self.playback_bar = None

        self._configure_last_called = datetime.min
        self._initialise_canvas(trace = inf_trace)

        self.treeview_input_files = dw.SimpleTreeview(
            self.widget_frame, {1: {"header": "Filename",
                                    "width": self.pr.c.width_text_long,
                                    "stretch": False,
                                    "anchor": "center"}
                                }
            )

        btn_import_files = tk.Button(
            self.io_directory.frame,
            text = "Import Files",
            background = self.pr.c.colour_interface_button,
            command = self._btn_import_files_click
            )
        self.io_directory.add_widget(
            widget = btn_import_files,
            fixed_width = True,
            trace = inf_trace,
            row = "input",
            column = "end"
            )

        btn_execute_breakpoints = tk.Button(
            self.io_directory.frame,
            text="Execute Breakpoints",
            background = self.pr.c.colour_interface_button,
            command = self._btn_execute_breakpoints_click
            )

        self.io_directory.add_widget(
            widget = btn_execute_breakpoints,
            fixed_width = True,
            trace = inf_trace,
            row = "output",
            column = btn_import_files
            )

        self.btn_display_waveform = tk.Button(
            self.widget_frame,
            text="Display Waveform",
            background = self.pr.c.colour_interface_button,
            command = self._btn_display_waveform_click
            )

        self.btn_import_breakpoints = tk.Button(
            self.widget_frame,
            text="Import Breakpoints",
            background = self.pr.c.colour_interface_button,
            command = self._btn_import_breakpoints_click
            )

        self.treeview_info = {
            1: {"header": "", "width": self.pr.c.width_text_tiny,
                "stretch": False, "anchor": "center", "copy_from_above": True},
            2: {"header": "Composer", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w", "copy_from_above": True},
            3: {"header": "Album", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w", "copy_from_above": True},
            4: {"header": "#", "width": self.pr.c.width_text_tiny,
                "stretch": False, "anchor": "center", "copy_from_above": False},
            5: {"header": "Track", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w", "copy_from_above": False},
            6: {"header": "Performer(s)", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w", "copy_from_above": True},
            7: {"header": "Year", "width": self.pr.c.width_text_tiny,
                "stretch": False, "anchor": "center", "copy_from_above": True},
            8: {"header": "Genre", "width": self.pr.c.width_text_veryshort,
                "stretch": True, "anchor": "w", "copy_from_above": True},
            9: {"header": "URL", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w", "copy_from_above": True},
            10: {"header": "Final name", "width": self.pr.c.width_text_long,
                 "stretch": True, "anchor": "w", "copy_from_above": False},
            11: {"header": "Done", "width": self.pr.c.width_text_tiny,
                 "stretch": True, "anchor": "center", "copy_from_above": False},
            }

        self.treeview_file_names = dw.SimpleTreeview(
            self.widget_frame, self.treeview_info)

        widgets = {
            1: {'widget': self.io_directory.frame,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            2: {'widget': self.treeview_input_files,
                'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                'stretch_height': True
                },
            3: {'widget': self.btn_display_waveform,
                'grid_kwargs': {
                    **self.pr.c.grid_sticky,
                    "padx": self.pr.c.padding_small,
                    "pady": self.pr.c.padding_small_bottom_only
                    }
                },
            4: {'widget': self.btn_import_breakpoints,
                'grid_kwargs': {
                    **self.pr.c.grid_sticky,
                    "padx": self.pr.c.padding_small
                    }
                },
            5: {'widget': self.visual_frame,
                'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                'stretch_width': True,
                'stretch_height': True
                },
            6: {'widget': self.audio_interface,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True
                },
            7: {'widget': self.treeview_file_names,
                'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                'stretch_width': True,
                'stretch_height': True
                },
            8: {'widget': self.search_box,
                'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                'stretch_width': True
                },
            -1: {'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                 'widget_kwargs': {'bg': self.pr.c.colour_background}
                },
            }
        self.widget_set = WidgetSet(self.widget_frame,
                                    widgets,
                                    layout = [[1],
                                              [2, 5],
                                              [3, 6],
                                              [4, 6],
                                              [7],
                                              [8]]
                                    )

        self.widget_set.grid(row = 0, column = 0, **self.pr.c.grid_sticky,
                             trace = inf_trace)

        self.tab.columnconfigure(index = 0, weight = 1)
        self.tab.rowconfigure(index = 0, weight = 1)

        """
        ### BOUND FUNCTIONS ###
        """
        self.treeview_input_files.bind("<1>", lambda event: self._treeview_mouse1_click(event, trace = {"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<1>"}))
        self.treeview_file_names.bind("<1>", lambda event: self._treeview_mouse1_click(event, trace = {"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<1>"}))
        self.treeview_file_names.bind("<Double-1>", lambda event: self.edit_value_via_interface(event, trace = {"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<Double-1>"}))
        self.treeview_file_names.bind("<Control-d>", lambda event: self.copy_from_above(event, trace = {"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<Control-d>"}))

        #search box
        self.treeview_file_names.bind("<KeyPress-Alt_L>", lambda event: self._key_press_alt(event, trace = {"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<KeyPress-Alt_L>"}))
        self.treeview_file_names.bind("<KeyRelease-Alt_L>", lambda event: self._key_release_alt(event, trace = {"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<KeyRelease-Alt_L>"}))
        self.treeview_file_names.bind("<Alt-1>", lambda event: self._alt_mouse_1(event, trace = {"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<Alt-1>"}))

        self.treeview_input_files.bind("<KeyPress-Alt_L>", lambda event: self._key_press_alt(event, trace = {"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<KeyPress-Alt_L>"}))
        self.treeview_input_files.bind("<KeyRelease-Alt_L>", lambda event: self._key_release_alt(event, trace = {"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<KeyRelease-Alt_L>"}))
        self.treeview_input_files.bind("<Alt-1>", lambda event: self._alt_mouse_1(event, trace = {"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<Alt-1>"}))

        self.load_from_config(trace = inf_trace)
        self.populate_input_files(trace = inf_trace)

    def _btn_import_files_click(self, trace = None):
        self.pr.f._log_trace(self, "_btn_import_files_click", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._btn_import_files_click"}

        self.populate_input_files(trace = inf_trace)

    def populate_input_files(self, trace = None):
        self.pr.f._log_trace(self, "populate_treeview", trace)
        """
        Populate the treeview with file names
        """
        self.treeview_input_files.delete(
            *self.treeview_input_files.get_children())
        try:
            file_list = os.listdir(self.io_directory.input_directory)
        except FileNotFoundError:
            return
        for file in file_list:
            if file[-4:] == self.pr.c.file_extension:
                filename = file[:-4]
                self.treeview_input_files.insert("",
                                                 index="end",
                                                 text = filename,
                                                 iid = filename)

    def _btn_execute_breakpoints_click(self, trace = None):
        self.pr.f._log_trace(self, "_btn_execute_breakpoints_click", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._btn_execute_breakpoints_click"}

        if self.executing: return

        func = lambda: self.execute_breakpoints(trace = inf_trace)

        self.execute_breakpoints(trace = inf_trace)
        self.executing = True
        self.execution_process = threading.Thread(target = func, daemon = True)
        self.execution_process.start()
        self.executing = False

    def execute_breakpoints(self, trace = None):
        self.pr.f._log_trace(self, "execute_breakpoints", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".execute_breakpoints"}

        true_breakpoints = self._true_breakpoints(scale_to_sound = True,
                                                  trace = inf_trace)

        for k in range(len(true_breakpoints) - 1):
            try:
                exception = False
                text = None
                start = true_breakpoints[k]
                end = true_breakpoints[k+1]
                iid = str(k+1)
                filename = (
                    self.treeview_file_names.set_translate(iid, "Final name")
                    + self.pr.c.file_extension
                            )

                #Write audio to file
                try:
                    self.write_audio(self.sound[start:end], filename,
                                     trace = inf_trace)
                except:
                    text = "Failed to write audio"
                    raise

                #tag file
                try:
                    self.tag_file(iid = iid, filename = filename,
                                  trace = inf_trace)
                except ValueError as e:
                    text = str(e)
                    raise
                except:
                    exception = True
                    text = "Failed to tag file and add keyword matching"
                    raise

                #add to insight
                try:
                    self.add_insight(iid, inf_trace)
                except:
                    text = "Failed to add to Insight"
                    raise

            except Exception as err:
                exception = True
                error = err
                """ All errors not handled elsewhere """
                raise #TODO
                pass

            if exception:
                if text is None: text = "An unexpected error occurred"
                done_text = "✘ - %s (%s)" % (text, error)
            else:
                done_text = "✓"
            self.treeview_file_names.set_translate(str(k+1), "Done", done_text)


        original_files_dir = os.path.join(self.io_directory.output_directory,
                                          "Original files")
        if not os.path.exists(original_files_dir):
            os.makedirs(original_files_dir)
        self.pr.f.rename_file(
            old_directory = self.io_directory.input_directory,
            old_name = self.filename + self.pr.c.file_extension,
            new_directory = original_files_dir,
            new_name = self.filename + self.pr.c.file_extension,
            trace = inf_trace
            )
        self.treeview_input_files.delete(self.filename)

    def write_audio(self, audio, name, trace = None):
        self.pr.f._log_trace(self, "write_audio", trace)
        audio.export(os.path.join(self.io_directory.output_directory, name),
                     format = "mp3")

    def _btn_display_waveform_click(self, trace = None):
        self.pr.f._log_trace(self, "_btn_display_waveform_click", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._btn_display_waveform_click"}

        if self.executing: return
        if len(self.treeview_input_files.selection()) == 0: return
        self.filename = self.treeview_input_files.selection()[0]
        self.display_waveform(
            filepath = os.path.join(self.io_directory.input_directory,
                                    self.filename + self.pr.c.file_extension),
            trace = inf_trace)

        self.audio_interface.end_audio_process(trace = inf_trace)
        self.audio_interface.load_audio(self.sound, trace = inf_trace)

    def _btn_import_breakpoints_click(self, trace = None):
        """
        Open a text input for the user to input either a list of timecodes
        of the format XX:XX or XX:XX:XX separated by commas, or a block of
        text to parse for timecodes in that format.

        Add breakpoints to the audio track at the specified timecodes. If the
        input is a block of parsed text, attempt to also parse it for track
        names.
        """
        if self.executing: return

        self.pr.f._log_trace(self, "_btn_import_breakpoints", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._btn_import_breakpoints"}
        if self.waveform is None: return
        timecodes = tk.simpledialog.askstring(title = "Import Breakpoints",
                                              prompt = "Enter a list of "
                                              "timecodes separated by commas,"
                                              " or text to parse for "
                                              "timecodes.",
                                              )
        # First try to parse as a list of timecodes 12:34 separated by commas
        # Failing that, parse directly using RegEx, matching XX:XX:XX or XX:XX
        # where X are numbers.
        track_dict = {}
        try:
            tc_no_space = ''.join(timecodes.split()) #remove whitespace
            tc_list = tc_no_space.split(",")
            tc_list = [self.pr.f.timecode_to_seconds(t)*1000 for t in tc_list]
            tc_list = list(set(tc_list))
            try: tc_list.remove(0)
            except ValueError: pass
        except ValueError:
            tc_pattern = re.compile(r"\b\d{1,2}(?::\d{2}){1,2}\b")

            tc_list = re.findall(tc_pattern, timecodes)

            tc_list = [self.pr.f.timecode_to_seconds(t)*1000 for t in tc_list]
            tc_list = list(set(tc_list))
            try: tc_list.remove(0)
            except ValueError: pass

            # Assume that the space in between the timecodes is a list of
            # tracks split based on the timecode pattern
            track_list = re.split(tc_pattern, timecodes)
            track_list = [trk for trk in track_list if trk.strip() != ""]
            for trk in track_list:
                for regex in config.numerals_dict.regex_dict:
                    match = re.search(regex, trk, re.IGNORECASE)
                    if match:
                        #exclude matched string
                        trk_num = str(config.numerals_dict.regex_dict[regex])
                        trk_name = trk[:match.start()] + trk[match.end():]
                        trk_name = self.pr.f.clean_track_string(
                            trk_name, trace = inf_trace)
                        track_dict[trk_num] = trk_name

            track_list = [self.pr.f.clean_track_string(trk, trace = inf_trace)
                          for trk in track_list]
            track_list = [trk for trk in track_list if trk.strip() != ""]

            for i, trk in enumerate(track_list):
                if str(i+1) not in track_dict:
                    track_dict[str(i+1)] = trk

        tc_list = [t*self.sound_subsample_length/self.sound_length
                   for t in tc_list]

        # loop through and add breakpoints at specified points
        for tc in set(tc_list):
            self._add_breakpoint_x(tc, inf_trace)

        # Loop through the track_dict and set track names accordingly
        if track_dict != {}:
            for i, trk in track_dict.items():
                if trk.strip() != "":
                    self.treeview_file_names.set_translate(i, "Track", trk)

    def _initialise_canvas(self, trace = None):
        self.pr.f._log_trace(self, "_initialise_canvas", trace)
        """
        Initialise the canvas used to draw the audio waveform
        """
        key_trace = {"source": "bound event",
                     "widget": self.name + ".canvas", "event": "<event.key>"}
        self.audio_canvas.mpl_connect("key_press_event", lambda event:
                                self._on_key_press(event, trace = key_trace))
        self.audio_canvas.mpl_connect("button_press_event", lambda event:
                                self._on_button_press(event, trace = key_trace))
        self.audio_canvas.mpl_connect("key_release_event", lambda event:
                                self._on_key_release(event, trace = key_trace))

    def waveform_from_path(self, filepath, trace = None):
        self.pr.f._log_trace(self, "display_waveform", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".display_waveform"}
        """
        Displays the waveform of the specified file in a matplotlib window with
        navigation toolbar.
        """
        sound = AudioSegment.from_mp3(filepath)
        #TODO
        # self.audio_canvas.display_waveform(sound)
        self.treeview_file_names.delete(
            *self.treeview_file_names.get_children())
        self.update_treeview_numbers(trace = inf_trace)

    def _on_key_press(self, event, trace = None):
        trace["event"] = "<%s>" % event.key
        self.pr.f._log_trace(self, "_on_key_press", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._on_key_press"}
        """
        This contains all the key press handling events
        Replaces bound functions usually in __init__
        """
        key_press_handler(event, self.canvas, self.toolbar)

        if event.key == 'enter':
            self._add_breakpoint(event, trace = inf_trace)
        elif event.key == ' ': #space key
            self._add_breakpoint(event, trace = inf_trace)
        elif event.key == 'ctrl+z':
            self._undo_breakpoint(event, trace = inf_trace)
        elif event.key == "control":
            self._control_pressed = True
        elif event.key == "shift":
            self._shift_pressed = True
            self.tab.after(500, self._depress_key, event.key, inf_trace)
        elif event.key == "alt":
            self._alt_pressed = True
            self.tab.after(500, self._depress_key, event.key, inf_trace)

    def _on_key_release(self, event, trace = None):
        trace["event"] = "<%s>" % event.key
        self.pr.f._log_trace(self, "_on_key_release", trace)
        """
        This contains all the key release handling events
        Replaces bound functions usually in __init__
        """
        if event.key == "control":
            self._control_pressed = False
        elif event.key == "shift":
            self._shift_pressed = False
        elif event.key == "alt":
            self._alt_pressed = False

    def _on_button_press(self, event, trace = None):
        trace["event"] = "<%s>" % event.button
        self.pr.f._log_trace(self, "_on_button_press", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._on_button_press"}
        """
        This contains all the button press handling events (e.g. mouse)
        Replaces bound functions usually in __init__
        """
        # left clicking the canvas forces the focus to it
        if event.button == 1:
            self.canvas.get_tk_widget().focus_force()
        if event.button == 1 and self._control_pressed:
            self._change_outside_breakpoint(event, trace = inf_trace)
        if event.button == 1 and self._shift_pressed:
            bp = self.get_closest_breakpoint(event, trace = inf_trace)
            self.remove_breakpoint(bp, trace = inf_trace)
        if event.button == 1 and self._alt_pressed:
            bp = self.get_closest_breakpoint(event, trace = inf_trace)
            self.move_breakpoint(bp, x = event.xdata, trace = inf_trace)
            #move breakpoint
            pass

    def _depress_key(self, key, trace = None):
        self.pr.f._log_trace(self, "_on_button_press", trace)
        """
        Force the relevant _<key>_pressed to False, for use in cases where
        the _on_key_release method is inconsistently triggered.
        """
        if key == "control":
            self._control_pressed = False
        elif key == "shift":
            self._shift_pressed = False
        elif key == "alt":
            self._alt_pressed = False

    def _add_breakpoint(self, event, trace = None):
        self.pr.f._log_trace(self, "_add_breakpoint", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._add_breakpoint"}
        """
        Handle the event to add a new breakpoint to the waveform
        """
        self._add_breakpoint_x(event.xdata, trace = inf_trace)


    def _undo_breakpoint(self, event, trace = None):
        self.pr.f._log_trace(self, "_undo_breakpoint", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._undo_breakpoint"}
        """
        Undoes the most recent breakpoint action.
        """
        self.audio_canvas.breakpoints.undo()

    def load_from_config(self, trace = None):
        self.pr.f._log_trace(self, "load_from_config", trace)
        self.subsampling_rate = 1000

    def _treeview_mouse1_click(self, event, trace = None):
        self.pr.f._log_trace(self, "_treeview_mouse1_click", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._treeview_mouse1_click"}

        treeview_list = [self.treeview_file_names, self.treeview_input_files]
        x,y = self.root.winfo_pointerxy()

        for widget in treeview_list:
            if self.pr.f.point_is_inside_widget(x, y, widget,
                                                trace = inf_trace):
                self._treeview_mouse1_click_column = widget.identify_column(event.x)
                self._treeview_mouse1_click_row = widget.identify_row(event.y)
                self._treeview_mouse1_click_cell = (
                    self._treeview_mouse1_click_row
                    if self._treeview_mouse1_click_column == "#0"
                    else widget.set(self._treeview_mouse1_click_row,
                                    self._treeview_mouse1_click_column)
                    )
                return event
        return event

    def edit_value_via_interface(self, event, trace = None):
        self.pr.f._log_trace(self, "edit_value_via_interface", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".edit_value_via_interface"}
        """
        Open a window with the selected filename where a value can be
        specified for the selected cell
        """
        if self.executing: return
        #Identify the column clicked
        clicked_column_id = self._treeview_mouse1_click_column

        if clicked_column_id == "#0":
        #exit if the first column (filename) is clicked
            return event

        #Identify the filename of the row clicked
        clicked_row = self._treeview_mouse1_click_row
        if clicked_row is None or clicked_row == "":
            return event # exit if an empty row is clicked

        ValueFromFilename(
            parent = self,
            filename = self.filename,
            columnString = self.treeview_file_names.translate_column(
                clicked_column_id
                ),
            columnId = clicked_column_id,
            treeview = self.treeview_file_names,
            row_iid = clicked_row,
            trace = inf_trace
            )
        return event

    def update_treeview_numbers(self, trace = None):
        self.pr.f._log_trace(self, "update_treeview_numbers", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".update_treeview_numbers"}

        treeview_count = len(self.treeview_file_names.get_children())
        breakpoint_count = len(self._true_breakpoints(
            scale_to_sound = False, trace = inf_trace)) - 1

        while treeview_count < breakpoint_count:
            _id = treeview_count + 1
            num_index = self.treeview_file_names.get_columns().index("#")
            if self.fresh_waveform == True:
                values = [self.pr.f.suggest_value(self.filename, field,
                                                  trace = inf_trace)
                          for field in self.treeview_file_names.get_columns()]
                values[num_index] = 1
            else:
                # Get values of row above
                values = list(self.treeview_file_names.item(
                    self.treeview_file_names.get_children()[-1], "values"))
                if values[num_index] == "":
                    values[num_index] = ""
                else:
                    values[num_index] = int(values[num_index]) + 1

            self.treeview_file_names.insert("", index="end", text = str(_id),
                                            iid = str(_id), values = values)
            self.treeview_file_names.set_translate(str(_id), "Track", "")
            self.set_final_name(str(_id), trace = inf_trace)
            treeview_count = len(self.treeview_file_names.get_children())

        while treeview_count > breakpoint_count:
            self.treeview_file_names.delete(
                self.treeview_file_names.get_children()[-1])
            treeview_count = len(self.treeview_file_names.get_children())

    def copy_from_above(self, event, trace = None):
        self.pr.f._log_trace(self, "copy_from_above", trace)
        """
        Copies a value down to all selected rows in certain column
        """
        if self.executing: return
        selected_items = self.treeview_file_names.selection()
        selection_iter = range(len(selected_items))
        clicked_column_id = self._treeview_mouse1_click_column
        if clicked_column_id == "#0":
            #cancel if the filename ID column was the last column clicked
            return event

        #get the value to copy down. If one row is selected, this is the value in
        #the row above. If multiple values are selected, this is the value in the
        #first selected row
        if self.treeview_file_names.translate_column(clicked_column_id) == "#":
            #number column case
            if len(selected_items) == 1:
                #increment from row above
                value_to_copy = int(self.treeview_file_names.set(
                    self.treeview_file_names.prev(selected_items[0]),
                    clicked_column_id)
                    ) + 1
            else:
                #list of incrementing values starting from first row
                start_value = self.treeview_file_names.set(selected_items[0],
                                                           clicked_column_id)
                try:
                    start_int = int(start_value)
                    value_to_copy = list(range(start_int,
                                               start_int+len(selected_items)+1))
                except ValueError:
                    value_to_copy = ["" for i in selection_iter]
        else:
            if len(selected_items) == 1:
                value_to_copy = self.treeview_file_names.set(
                    self.treeview_file_names.prev(selected_items[0]),
                    clicked_column_id)
            else:
                value_to_copy = self.treeview_file_names.set(
                    selected_items[0], clicked_column_id)
            value_to_copy = [value_to_copy for i in selection_iter]

        #update the value of all cells in the selected rows and column
        for i in selection_iter:
            item = selected_items[i]
            value = value_to_copy[i]
            self.treeview_file_names.set(item, clicked_column_id, value)
            self.set_final_name(item)
        return event

    def set_final_name(self, filename, trace = None):
        self.pr.f._log_trace(self, "set_final_name", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".set_final_name"}

        if self.executing: return

        self.treeview_file_names.set_translate(
            filename,
            "Final name",
            self.pr.f.filename_from_dict(
                parts_dict = self.pr.f.get_values_dict(
                    self.treeview_file_names,
                    filename,
                    self.treeview_file_names.get_columns(include_key = True)
                    ),
                trace = inf_trace
                )
            )

    def match_keywords(self, filename, overwrite = False, trace = None):
        self.pr.f._log_trace(self, "match_keywords", trace)

        values_dict = {}
        for field in ["Composer", "Album", "#", "Genre", "Year", "Track"]:
            values_dict[field] = self.treeview_file_names.set_translate(
                filename, field)

        keyword_dicts = config.keyword_dict.regex_dict

        for compare_dict in keyword_dicts.values():
            #run through all available keyword mapping dictionaries, overlaying
            #to get the best output
            for key in compare_dict['key']:
                invalid_match = False
                try:
                    if not re.match(compare_dict['key'][key],
                                    values_dict[key], re.IGNORECASE):
                        invalid_match = True
                        break
                except:
                    break
            if invalid_match: continue
            #run only once a full set of valid pattern matches has been made
            for field in compare_dict['value']:
                if values_dict[field] == "" or overwrite:
                    self.treeview_file_names.set_translate(
                        filename, field, compare_dict['value'][field])
                    values_dict[field] = compare_dict['value'][field]
        return values_dict

    def tag_file(self, iid, filename, trace = None):
        self.pr.f._log_trace(self, "tag_file", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".tag_file"}

        tags = {"composer": self.treeview_file_names.set(iid, "Composer"),
                "album": self.treeview_file_names.set(iid, "Album"),
                "track": self.treeview_file_names.set(iid, "Track"),
                "number": self.treeview_file_names.set(iid, "#"),
                "performer(s)": self.treeview_file_names.set(iid, "Performer(s)"),
                "year": self.treeview_file_names.set(iid, "Year"),
                "genre": self.treeview_file_names.set(iid, "Genre"),
                "url": self.treeview_file_names.set(iid, "URL"),
                }
        self.pr.f.tag_file(directory = self.io_directory.output_directory,
                           filename = filename,
                           tags = tags,
                           trace = inf_trace)
        self.pr.f.add_keyword_pattern(tags, trace = inf_trace)

    def add_insight(self, filename, trace = None):
        self.pr.f._log_trace(self, "add_insight", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".add_insight"}

        values = self.pr.f.get_values_dict(
            self.treeview_file_names,
            filename,
            self.treeview_file_names.get_columns(include_key = True)
            )
        del values["Done"]
        del values[""]

        values["original_name"] = self.filename
        values["original_path"] = self.io_directory.input_directory
        values["final_path"] = self.io_directory.output_directory
        filepath = os.path.join(self.io_directory.input_directory,
                                self.filename + self.pr.c.file_extension)
        ctime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
        values["date_created"] = ctime
        self.pr.insight_rn.add_row(**values, trace = inf_trace)

    def _key_press_alt(self, event, trace = None):
        inf_trace = {"source": "function call",
                     "parent": self.name + "._key_press_alt"}
        """
        Create the search box GUI and maintain it while the bound key is
        held down
        """
        self.search_box.maintain(trace = inf_trace)
        return event

    def _key_release_alt(self, event, trace = None):
        self.pr.f._log_trace(self, "_key_release_alt", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._key_release_alt"}
        """
        Destroy the search box GUI when the bound key is released
        """
        self.search_box.destroy(trace = inf_trace)
        return event

    def _alt_mouse_1(self, event, trace = None):
        self.pr.f._log_trace(self, "_alt_mouse_1", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + "._alt_mouse_1"}

        if self.search_box is None:
            return event

        self._treeview_mouse1_click(event = event, trace = inf_trace)
        self.search_box.add(self._treeview_mouse1_click_cell,
                            trace = inf_trace)
        return event

    def get_closest_breakpoint(self, event, only_visible = True,
                               use_tolerance = True, sensitivity = 1,
                               trace = None):
        self.pr.f._log_trace(self, "get_closest_breakpoint", trace)
        """
        Return the closest breakpoint to the given x coordinate. If there are
        no breakpoints within the tolerance, return None.
        """
        if self.breakpoints_x is None or self.breakpoints_x == []:
            return
        elif event.xdata is None:
            return

        min_graph_xdata, max_graph_xdata = self.figure.get_xbound()
        bp_dist = {abs(bp.get_xdata()[0] - event.xdata): bp
                   for bp in self.breakpoints
                   if (min_graph_xdata < bp.get_xdata()[0] < max_graph_xdata)
                   or not(only_visible)
                   }
        #closest visible breakpoint
        #return if none visible
        if bp_dist == {}: return

        #Percentage of self.visual_frame.winfo_width() given over to blank
        #space before the start of the waveform
        left_pad = self.visual_frame.winfo_width()*0.125
        figure_start_x = self.visual_frame.winfo_rootx()
        try:
            closest_brkpt = bp_dist[min(bp_dist)]
        except ValueError: #bp_dist is empty, but not handled earlier
            return
        brkpt_xdata = closest_brkpt.get_xdata()[0]
        clicked_pixel_x = event.x + figure_start_x

        #The pixel location of the breakpoint is interpolated based on the
        #known event pixel x and data x, the known data minimum and
        #assumed pixel x at that minimum, and the data x of the breakpoint.
        interpolated_pixel = (clicked_pixel_x - figure_start_x - left_pad)
        interpolated_pixel = interpolated_pixel * (brkpt_xdata
                                                   - min_graph_xdata)
        interpolated_pixel = interpolated_pixel/(event.xdata - min_graph_xdata)
        interpolated_pixel = interpolated_pixel + left_pad + figure_start_x
        breakpoint_pixel_x = round(interpolated_pixel)

        #calculate the tolerance level
        if use_tolerance:
            tolerance = 20
            min_data_x = self.figure.dataLim.x0
            max_data_x = self.figure.dataLim.x1
            visible_ratio = ((max_graph_xdata - min_graph_xdata)/
                             (max_data_x - min_data_x))

            #config options
            min_pixels = 20 * 1/sensitivity
            max_pixels = 50 * sensitivity
            min_px_ratio = 0.8
            max_px_ratio = 0.2

            """
            Pixel tolerance curve is shaped like this:
                ______
                      \
                       \
                        \_______
            """

            if visible_ratio > min_px_ratio:
                tolerance = min_pixels
            elif visible_ratio <= max_px_ratio:
                tolerance = max_pixels
            else:
                mult = ((visible_ratio - min_px_ratio)/
                        (max_px_ratio - min_px_ratio))
                tolerance = (max_pixels - min_pixels)*mult + min_pixels

            if abs(clicked_pixel_x - breakpoint_pixel_x) <= tolerance:
                return closest_brkpt
        else:
            return closest_brkpt

    def move_breakpoint(self, brkpt, x, trace = None):
        self.pr.f._log_trace(self, "move_breakpoint", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".move_breakpoint"}
        """
        Return the closest breakpoint to the given x coordinate. If there are
        no breakpoints within the tolerance, return None.

        Tolerance is in terms of actual screen pixels.
        """
        if self.executing: return
        if brkpt is None: return
        self.remove_breakpoint(brkpt, refresh_treeview = False,
                               trace = inf_trace)
        self._add_breakpoint_x(x, trace = inf_trace)

class AudioBreakpoint:
    def __init__(self, parent, x, figure = None, **kwargs):
        self.parent = parent
        self.figure = figure
        self.first, self.last = False, False
        self.__dict__.update(kwargs)
        if not figure is None:
            self.line = self.figure.axvline(
                x = x, color = kwargs.get("color", "black")
                )
            return self.line

    def remove(self):
        self.x = None
        if not self.figure is None:
            self.line.remove()

    def move(self, x):
        self.x = x
        if not self.figure is None:
            self.line.set_xdata([x, x])

def locked_function(func):
    """
    Decorator for functions which should not be run if self.locked is True
    """
    def _func_with_lock_check(self, *args, **kwargs):
        if self.locked: return
        return func(*args, **kwargs)
    return _func_with_lock_check

def draw_function(func):
    """ Decorator for functions which affect the canvas """
    def _func_with_draw(self, *args, **kwargs):
        func_return = func(*args, **kwargs)
        if self.draw: self.draw_func()
        return func_return
    return _func_with_draw

class AudioBreakpoints:
    def __init__(self, draw = False, figure = None, draw_func = None):
        if draw and (figure is None or draw_func is None):
            raise ValueError(
                "Figure to draw on and update function must be provided")
        self.draw = draw
        self.figure = figure
        self.draw_func = draw_func
        self.locked = False

        self.breakpoints = []
        self.figure_numbers = []

    def __getitem__(self, index):
        return self.breakpoints[index]

    def __iter__(self):
        self._i = -1
        return self

    def __next__(self):
        if self._i < len(self.breakpoints) - 1:
            self._i += 1
            return self.breakpoints[self._i]
        else:
            raise StopIteration

    @locked_function
    @draw_function
    def add(self, x, **kwargs):
        """ Add a breakpoint at the x coordinate """
        if not self.x_in_bounds(x): return
        new_brkpt = AudioBreakpoint(self, x, **kwargs)
        self.breakpoints.append(new_brkpt)

    def x_in_bounds(self, x, minmax = None, inclusive = False):
        xmin, xmax = minmax if not minmax is None else self.minmax()
        if inclusive:
            return xmin <= x <= xmax
        else:
            return xmin < x < xmax

    def minmax(self):
        """ Return x coordinates of first and last breakpoint """
        return (self.first.x, self.last.x)

    @locked_function
    @draw_function
    def remove(self, brkpt):
        """ Remove a given breakpoint from the figure and internal memory """
        index = self.breakpoints.index(brkpt)
        self.breakpoints.pop(index)
        brkpt.remove()

        if self.draw: self.reset_numbers()

    @locked_function
    @draw_function
    def move(self, brkpt, x):
        """ Move a given breakpoint to a given x coordinate """
        brkpt.move(x)
        # remove newly out of bounds breakpoints
        minmax = self.minmax()
        for other_brkpt in self:
            if not self.x_in_bounds(other_brkpt.x, minmax, inclusive = True):
                self.remove(other_brkpt)

    def count(self):
        return len(self.breakpoints)

    @locked_function
    def undo(self):
        if self.count() == 0: return
        self.remove(self[-1])

    def first(self):
        for brkpt in self:
            if brkpt.first: return brkpt

    def last(self):
        for brkpt in self:
            if brkpt.last: return brkpt

    @draw_function
    def draw_numbers(self):
        """ Draw numbers at the midpoint between breakpoints corresponding to
        each audio segment"""
        brkpts = self.truebreakpoints(scale_to_sound = False)
        txt_kwargs = {"fontfamily": "Palatino Linotype",
                      "fontsize": 10, "color": "black"}
        for k in range(len(brkpts) - 1):
            #add halfway between breakpoints
            x = (brkpts[k+1] + brkpts[k])/2
            y = self.figure_ylim[0]*0.97 #add to bottom of plot
            text = str(k+1)
            fig_num = self.figure.text(x=x, y=y, s=text, **txt_kwargs)
            self.figure_numbers.append(fig_num)
        return

    @draw_function
    def remove_numbers(self):
        """ Remove all numbers from the canvas """
        for fig_num in self.figure_numbers:
            fig_num.remove()
        self.figure_numbers = []
        return

    @draw_function
    def reset_numbers(self):
        """ Remove all numbers from the canvas and redraw them """
        self.remove_numbers()
        self.draw_numbers()

    @locked_function
    @draw_function
    def reset(self):
        """ Remove all breakpoints """
        for brkpt in self: brkpt.remove()
        self.breakpoints = []

    def get_x(self, sort = True, include_ends = True):
        breakpoints_x = []
        for brkpt in self:
            if include_ends or (not self.first and not self.last):
                breakpoints_x.append(brkpt.x)
        if sort:
            return sorted(breakpoints_x)
        else:
            return breakpoints_x

    def get_closest(x, xmin = None, xmax = None):
        return

    def get_scale(self):
        try:
            return self.scale
        except AttributeError:
            return 1

    def truebreakpoints(self, scale_to_sound = True):
        brkpts_x = self.get_x(sort = True, include_ends = True)
        scale = self.get_scale()
        if scale_to_sound:
            for i, x in enumerate(brkpts_x):
                brkpts_x[i] *= scale
        return

class AudioCanvas:
    def __init__(self, master, **kwargs):
        self.master = master
        self.waveform_colour = "black"
        self.background_colour = "white"
        self.__dict__.update(kwargs)

        self.visual_figure = Figure(figsize=(10, 5), dpi=100)
        self.visual_figure.subplots_adjust(
            left = 0.03, right = 0.97, top = 0.95, bottom = 0.05)

        self.figure = self.visual_figure.add_subplot(111)
        self.figure.axes.get_yaxis().set_visible(False)
        self.figure.axis("off")
        self.figure.set(facecolor = self.waveform_colour)
        self.figure.margins(x = 0, y = 0)

        self.canvas = FigureCanvasTkAgg(self.visual_figure,
                                        master = self.master)
        self.canvas.draw()

        #add toolbar below plot
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.config(background = self.background_colour)
        self.toolbar._message_label.config(background = self.background_colour)
        self.toolbar.update()

        #must use .pack() here to avoid conflict with matplotlib backend
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill = tk.BOTH, expand = 1)

        self.breakpoints = AudioBreakpoints()
        self.locked = False

    def config(self, **kwargs):
        return

    def mpl_connect(self, s, func):
        self.canvas.mpl_connect(s, func)

    @locked_function
    def clear(self):
        self.toolbar.home()
        if not self.waveform is None:
            self.waveform.remove()
            self.waveform = None
        if not self.breakpoints.first is None:
            self.breakpoints.first.remove()
            self.breakpoints.first = None
        if not self.end_breakpoint is None:
            self.end_breakpoint.remove()
        self.breakpoints.reset()
        self.draw()
        self.canvas.get_tk_widget().focus_force()

    @locked_function
    def display_waveform(self, audio):
        subsampling_rate = self.__dict__.get("subsampling_rate", 1000)
        self.sound = audio
        self.sound_length = len(audio)
        self.sound_subsample = self.sound.get_array_of_samples()[0::subsampling_rate]
        self.sound_subsample_length = len(self.sound_subsample)
        plot_config = {"color": self._colour_waveform}
        self.waveform, = self.figure.plot(self.sound_subsample, **plot_config)

        self.clear()

        # add breakpoints at start and end
        self.breakpoints.scale = self.get_scale()
        self.breakpoints.add(x = 0, first = True, color = "black",
                             figure = self.figure)

        self.breakpoints.add(x = self.sound_subsample_length - 1, last = True,
                             color = "black", figure = self.figure)

        self.breakpoints.reset_numbers()

        self.draw()
        self.scale()
        self.toolbar.update()
        self.fresh = True

    @locked_function
    def scale(self):
        self.figure.set_autoscalex_on(True)

        self.figure.set_ylim(ymin = self.figure.get_ylim[0],
                             ymax = self.figure.get_ylim[1])
        self.figure.set_xlim(xmin=0, xmax=self.sound_subsample_length)

    def draw(self):
        self.canvas.draw()

    def get_closest_breakpoint(self, x, only_visible = True,
                               use_tolerance = True, exclude_ends = True):
        return

    def tune_get_closest(self, **kwargs):
        return

    def get_scale(self):
        return self.sound_length/self.sound_subsample_length

if __name__ == "__main__":
    pass
    import prospero_constants as prc
    import prospero_functions as prf
    import prospero_resources as prr
    from tkinter import ttk

    class Prospero:
        def __init__(self, trace):
            self.pr = self
            self.root = tk.Tk()

            self.testing_mode = True
            self.running = True
            self.start_time = datetime.now()

            self.f = prf.Functions(parent = self)

            self.c = prc.Constants(parent = self)

            self.r = prr.Resources(parent = self)

            self.widget_frame = tk.Frame(self.root,
                                         bg = self.pr.c.colour_background)

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

            self.audio_functions = AudioFunctions(parent = self)

            widgets = {1: {'widget': self.notebook,
                           'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                           'stretch_width': True, 'stretch_height': True},
                       }
            self.widget_set = WidgetSet(self.widget_frame,
                                        widgets,
                                        layout = [[4]]
                                        )
            self.widget_frame.grid(row = 0, column = 0, **self.pr.c.grid_sticky)
            self.root.rowconfigure(0, weight = 1)
            self.root.columnconfigure(0, weight = 1)

            #handles the window close event
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)

        def start(self, trace = None):
            self.pr.f._log_trace(self, "start", trace)

            self.root.eval('tk::PlaceWindow . center')
            self.root.mainloop()

        def destroy(self, event = None, trace = None):
            self.pr.f._log_trace(self, "destroy", trace)

            self.running = False
            self.audio_functions.audio_interface.end_audio_process()
            self.root.quit()
            self.root.destroy()
            return event

    prospero = Prospero(trace = {"source": "initialise class",
                                 "parent": __name__})
    prospero.start()