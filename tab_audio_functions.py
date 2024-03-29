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
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
import re

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from io_directory import IODirectory
from value_from_filename import ValueFromFilename
from audio_interface import AudioInterface
from search_box import SearchBox
from tk_arrange import WidgetSet
import config
import described_widgets as dw
from mh_logging import log_class
from global_vars import LOG_LEVEL

# #### REQUIRED ####
# conda install ffmpeg

class AudioFunctions():
    @log_class(LOG_LEVEL)
    def __init__(self, parent):
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab_audio_functions
        self.name = self.__class__.__name__

        self.executing = False

        frame_kwargs = {"bg": self.pr.c.colour_background}
        self.widget_frame = tk.Frame(self.tab, **frame_kwargs)

        self.io_directory = IODirectory(
            parent = self,
            master = self.widget_frame,
            call_after_input = self.populate_input_files
            )

        self._colour_breakpoint = "#bfb598"

        self.visual_frame = tk.Frame(
            self.widget_frame,
            bg = self.pr.c.colour_background,
            highlightthickness = 1,
            highlightcolor = self.pr.c.colour_selection_background
            )

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
            audio_canvas = self.audio_canvas
            )
        self.search_box = SearchBox(parent = self, master = self.widget_frame)

        self.waveform = None
        self._control_pressed = False
        self._shift_pressed = False
        self._alt_pressed = False
        self.playback_bar = None

        self._configure_last_called = datetime.min

        self.treeview_input_files = dw.SimpleTreeview(
            self.widget_frame, {
                1: {"header": "Filename",
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
                             )

        self.tab.columnconfigure(index = 0, weight = 1)
        self.tab.rowconfigure(index = 0, weight = 1)

        """
        ### BOUND FUNCTIONS ###
        """
        self.treeview_input_files.bind("<1>", self._treeview_mouse1_click)
        self.treeview_file_names.bind("<1>", self._treeview_mouse1_click)
        self.treeview_file_names.bind("<Double-1>", self.edit_value_via_interface)
        self.treeview_file_names.bind("<Control-d>", self.copy_from_above)

        #search box
        self.treeview_file_names.bind("<KeyPress-Alt_L>", self._key_press_alt)
        self.treeview_file_names.bind("<KeyRelease-Alt_L>", self._key_release_alt)
        self.treeview_file_names.bind("<Alt-1>", self._alt_mouse_1)

        self.treeview_input_files.bind("<KeyPress-Alt_L>", self._key_press_alt)
        self.treeview_input_files.bind("<KeyRelease-Alt_L>", self._key_release_alt)
        self.treeview_input_files.bind("<Alt-1>", self._alt_mouse_1)

        self.load_from_config()
        self.populate_input_files()
        self.mpl_connect_canvas()
        self.treeview_file_names.bind("<<ValueChange>>", self.update_final_name)
        self.audio_canvas.bind("<<BreakpointAdd>>", self.update_treeview)

    @log_class(LOG_LEVEL)
    def _btn_import_files_click(self):
        self.populate_input_files()

    @log_class(LOG_LEVEL)
    def populate_input_files(self):
        """
        Populate the treeview with file names
        """
        self.treeview_input_files.clear()
        try:
            file_list = os.listdir(self.io_directory.input_directory)
        except FileNotFoundError:
            return
        for file in file_list:
            if file[-4:] == self.pr.c.file_extension:
                filename = file[:-4]
                self.treeview_input_files.insert(
                    "", index="end", text = filename, iid = filename)

    @log_class(LOG_LEVEL)
    def _btn_execute_breakpoints_click(self):
        if self.executing: return

        func = lambda: self.execute_breakpoints()

        # self.execute_breakpoints()
        self.executing = True
        self.audio_canvas.locked = True
        self.audio_canvas.locked = True
        self.execution_process = threading.Thread(target = func, daemon = True)
        self.execution_process.start()
        self.executing = False

    @log_class(LOG_LEVEL)
    def execute_breakpoints(self):
        true_breakpoints = self.audio_canvas.breakpoints.true_breakpoints(
            scale_to_sound = True)

        for k in range(len(true_breakpoints) - 1):
            try:
                exception = False
                text = None
                start = true_breakpoints[k]
                end = true_breakpoints[k+1]
                iid = str(k+1)
                filename = (self.treeview_file_names.set(iid, "Final name")
                            + self.pr.c.file_extension)

                #Write audio to file
                try:
                    self.write_audio(self.audio_canvas.sound[start:end], filename)
                except:
                    text = "Failed to write audio"
                    raise

                #tag file
                try:
                    self.tag_file(iid = iid, filename = filename)
                except ValueError as e:
                    text = str(e)
                    raise
                except:
                    exception = True
                    text = "Failed to tag file and add keyword matching"
                    raise

                #add to insight
                try:
                    self.add_insight(iid)
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

            )
        self.treeview_input_files.delete(self.filename)

    @log_class(LOG_LEVEL)
    def write_audio(self, audio, name):
        audio.export(os.path.join(self.io_directory.output_directory, name),
                     format = "mp3")

    @log_class(LOG_LEVEL)
    def _btn_display_waveform_click(self):
        if self.executing: return
        if len(self.treeview_input_files.selection()) == 0: return
        self.filename = self.treeview_input_files.selection()[0]
        self.waveform_from_path(
            filepath = os.path.join(self.io_directory.input_directory,
                                    self.filename + self.pr.c.file_extension)
            )
        self.audio_interface.end_audio_process()
        self.treeview_file_names.clear()
        self.audio_interface.load_audio(self.audio_canvas.sound)

    @log_class(LOG_LEVEL)
    def _btn_import_breakpoints_click(self):
        """
        Open a text input for the user to input either a list of timecodes
        of the format XX:XX or XX:XX:XX separated by commas, or a block of
        text to parse for timecodes in that format.

        Add breakpoints to the audio track at the specified timecodes. If the
        input is a block of parsed text, attempt to also parse it for track
        names.
        """
        if self.audio_canvas.locked: return
        if self.audio_canvas.waveform is None: return
        timecodes = tk.simpledialog.askstring(
            title = "Import Breakpoints",
            prompt = "Enter a list of timecodes separated by commas,"
            " or text to parse for timecodes."
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
                            trk_name)
                        track_dict[trk_num] = trk_name

            track_list = [self.pr.f.clean_track_string(trk)
                          for trk in track_list]
            track_list = [trk for trk in track_list if trk.strip() != ""]

            for i, trk in enumerate(track_list):
                if str(i+1) not in track_dict:
                    track_dict[str(i+1)] = trk

        tc_list = [t*self.audio_canvas.get_scale(scale_up = True)
                   for t in tc_list]

        # loop through and add breakpoints at specified points
        for tc in tc_list:
            self.audio_canvas.breakpoints.add(tc)

        self.update_treeview()

        # Loop through the track_dict and set track names accordingly
        if track_dict != {}:
            for i, trk in track_dict.items():
                if trk.strip() != "":
                    self.treeview_file_names.set(i, "Track", trk)

    @log_class(LOG_LEVEL)
    def waveform_from_path(self, filepath):
        """ Displays the waveform of the specified file in the canvas """
        sound = AudioSegment.from_mp3(filepath)
        self.audio_canvas.display_waveform(sound)
        self.update_treeview()

    @log_class(LOG_LEVEL)
    def _add_breakpoint(self, event):
        """ Handle the event to add a new breakpoint to the waveform """
        self.audio_canvas.breakpoints.add(event.xdata)

    @log_class(LOG_LEVEL)
    def _undo_breakpoint(self, event):
        """ Undo the most recent breakpoint action. """
        self.audio_canvas.breakpoints.undo()

    @log_class(LOG_LEVEL)
    def load_from_config(self):
        self.subsampling_rate = 1000

    @log_class(LOG_LEVEL)
    def _treeview_mouse1_click(self, event):
        treeview_list = [self.treeview_file_names, self.treeview_input_files]
        x,y = self.root.winfo_pointerxy()

        for widget in treeview_list:
            if self.pr.f.point_is_inside_widget(x, y, widget,
                                                ):
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

    @log_class(LOG_LEVEL)
    def edit_value_via_interface(self, event):
        """
        Open a window with the selected filename where a value can be
        specified for the selected cell
        """
        if self.executing: return
        #Identify the column clicked
        clicked_column = self.treeview_file_names.events["<1>"]["column"]
        clicked_row = self.treeview_file_names.events["<1>"]["row"]

        if clicked_column == "#0":
        #exit if the first column (filename) is clicked
            return event

        #Identify the filename of the row clicked
        if clicked_row is None or clicked_row == "":
            return event # exit if an empty row is clicked

        ValueFromFilename(
            parent = self,
            filename = self.filename,
            columnString = self.treeview_file_names.translate_column(
                clicked_column
                ),
            columnId = clicked_column,
            treeview = self.treeview_file_names,
            row_iid = clicked_row,

            )
        return event

    @log_class(LOG_LEVEL)
    def update_treeview(self, *args):
        """ Update the number of rows in the file list treeview based on the
        number of breakpoints on the canvas """
        treeview_count = len(self.treeview_file_names.get_children())
        true_breakpoints = self.audio_canvas.breakpoints.true_breakpoints(
            scale_to_sound = False)
        breakpoint_count = len(true_breakpoints) - 1

        while treeview_count < breakpoint_count:
            _id = treeview_count + 1
            num_index = self.treeview_file_names.get_columns().index("#")
            if treeview_count == 0:
                values = [self.pr.f.suggest_value(self.filename, field)
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
            treeview_count = len(self.treeview_file_names.get_children())

        while treeview_count > breakpoint_count:
            self.treeview_file_names.delete(
                self.treeview_file_names.get_children()[-1])
            treeview_count = len(self.treeview_file_names.get_children())

    @log_class(LOG_LEVEL)
    def mpl_connect_canvas(self):
        self.audio_canvas.mpl_connect("key_press_event", self._on_key_press)
        self.audio_canvas.mpl_connect("button_press_event", self._on_button_press)
        self.audio_canvas.mpl_connect("key_release_event", self._on_key_release)

    @log_class(LOG_LEVEL)
    def _on_key_press(self, event):
        if event.key in ['enter', ' ']:
            self.update_treeview()
        elif event.key == 'ctrl+z':
            self.update_treeview()

    @log_class(LOG_LEVEL)
    def _on_button_press(self, event):
        if event.button == 1 and self.audio_canvas._shift_pressed:
            self.update_treeview()
        elif event.button == 1 and self.audio_canvas._control_pressed:
            self.update_treeview() #TODO


    @log_class(LOG_LEVEL)
    def _on_key_release(self, event):
        return

    @log_class(LOG_LEVEL)
    def copy_from_above(self, event):
        """
        Copies a value down to all selected rows in certain column
        """
        if self.audio_canvas.locked:
            return

        selected_items = self.treeview_file_names.selection()
        selection_iter = range(len(selected_items))
        clicked_col = self.treeview_file_names.events["<1>"]["column"]
        # cancel if the filename ID column was the last column clicked
        if clicked_col == "#0":
            return

        """ get the value to copy down. If one row is selected, this is the
        value in the row above. If multiple values are selected, this is the
        value in the first selected row """
        if self.treeview_file_names.translate_column(clicked_col) == "#":
            #number column case
            start_value = self.treeview_file_names.set(
                selected_items[0], clicked_col)
            if len(selected_items) == 1:
                #increment from row above
                value_to_copy = int(start_value) + 1
            else:
                #list of incrementing values starting from first row
                try:
                    start_int = int(start_value)
                    value_to_copy = list(range(
                        start_int, start_int + len(selected_items) + 1
                        ))
                except ValueError:
                    value_to_copy = ["" for i in selection_iter]
        else:
            if len(selected_items) == 1:
                value_to_copy = self.treeview_file_names.set(
                    self.treeview_file_names.prev(selected_items[0]),
                    clicked_col)
            else:
                value_to_copy = self.treeview_file_names.set(
                    selected_items[0], clicked_col)
            value_to_copy = [value_to_copy for i in selection_iter]

        #update the value of all cells in the selected rows and column
        for i in selection_iter:
            item = selected_items[i]
            value = value_to_copy[i]
            self.treeview_file_names.set(item, clicked_col, value)
        return event

    @log_class(LOG_LEVEL)
    def update_final_name(self, event):
        """
        Update the final name of the last updated file names treeview row
        """
        if self.executing: return
        vc_event = self.treeview_file_names.events["<<ValueChange>>"]
        updated_col = vc_event["column"]
        updated_row = vc_event["row"]
        if updated_col == "Final name": return
        elif updated_row is None: return
        try:
            new_filename = self.pr.f.filename_from_dict(
                parts_dict = self.treeview_file_names.values_dict(updated_row)
                )
        except tk.TclError:
            return # if iid doesn't exist yet
        self.treeview_file_names.set(updated_row, "Final name", new_filename)

    @log_class(LOG_LEVEL)
    def match_keywords(self, filename, overwrite = False):
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

    @log_class(LOG_LEVEL)
    def tag_file(self, iid, filename):
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
                           tags = tags)
        self.pr.f.add_keyword_pattern(tags)

    @log_class(LOG_LEVEL)
    def add_insight(self, filename):
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
        self.pr.insight_rn.add_row(**values)

    @log_class(LOG_LEVEL)
    def _key_press_alt(self, event):
        """
        Create the search box GUI and maintain it while the bound key is
        held down
        """
        self.search_box.maintain()

    @log_class(LOG_LEVEL)
    def _key_release_alt(self, event):
        """ Destroy the search box GUI when the bound key is released """
        self.search_box.destroy()

    @log_class(LOG_LEVEL)
    def _alt_mouse_1(self, event):
        if self.search_box is None: return
        self._treeview_mouse1_click(event = event)
        self.search_box.add(self._treeview_mouse1_click_cell)


def locked_function(func):
    """
    Decorator for functions which should not be run if self.locked is True
    """
    def _func_with_lock_check(self, *args, **kwargs):
        if self.locked: return
        return func(self, *args, **kwargs)
    return _func_with_lock_check

def draw_function(func):
    """ Decorator for functions which affect the canvas """
    def _func_with_draw(self, *args, **kwargs):
        func_return = func(self, *args, **kwargs)
        if self.draw: self.draw_func()
        return func_return
    return _func_with_draw

class AudioBreakpoint:
    @log_class(LOG_LEVEL)
    def __init__(self, parent, x, **kwargs):
        self.parent = parent
        self.x = x
        self.figure = parent.figure
        self.draw, self.draw_func = parent.draw, parent.draw_func
        self.first, self.last = False, False
        self.__dict__.update(kwargs)
        if not self.figure is None:
            self.line = self.figure.axvline(
                x = x, color = kwargs.get("color", "black")
                )
    @log_class(LOG_LEVEL)
    def _remove(self):
        """ Private remove method. Remove method in AudioBreakpoints should be
        called instead of this """
        self.x = None
        if not self.figure is None:
            self.line.remove()

    @log_class(LOG_LEVEL)
    @draw_function
    def move(self, x):
        self.x = x
        if not self.figure is None:
            self.line.set_xdata([x, x])

class AudioBreakpoints:
    @log_class(LOG_LEVEL)
    def __init__(self, draw = False, figure = None, audio_canvas = None,
                 draw_func = None):
        if draw and (figure is None or draw_func is None):
            raise ValueError(
                "Figure to draw on and update function must be provided")
        self.draw = draw
        self.figure = figure
        self.draw_func = draw_func
        self.locked = False
        if not audio_canvas is None:
            self.widget = audio_canvas.get_widget()
        else:
            self.widget = None
        self.breakpoints = []
        self.figure_numbers = []

    def __getitem__(self, index):
        return self.breakpoints[index]

    def __iter__(self):
        self._i = -1
        return self

    def __next__(self):
        if self._i < self.count() - 1:
            self._i += 1
            return self.breakpoints[self._i]
        else:
            self._i = None
            raise StopIteration

    @log_class(LOG_LEVEL)
    @locked_function
    @draw_function
    def add(self, x, **kwargs):
        """ Add a breakpoint at the x coordinate """
        if not self.x_in_bounds(x): return
        new_brkpt = AudioBreakpoint(self, x, **kwargs)
        self.breakpoints.append(new_brkpt)
        try: self.widget.event_generate("<<BreakpointAdd>>", x = x)
        except AttributeError: pass
        self.reset_numbers()

    @log_class(LOG_LEVEL)
    def x_in_bounds(self, x, minmax = None, inclusive = False):
        xmin, xmax = minmax if not minmax is None else self.minmax()
        if xmin is None or xmax is None:
            return True
        elif inclusive:
            return xmin <= x <= xmax
        else:
            return xmin < x < xmax

    @log_class(LOG_LEVEL)
    def minmax(self):
        """ Return x coordinates of first and last breakpoint """
        try:
            return (self.first().x, self.last().x)
        except AttributeError:
            return (None, None)

    @log_class(LOG_LEVEL)
    @locked_function
    @draw_function
    def remove(self, brkpt, redraw = True):
        """ Remove a given breakpoint from the figure and internal memory """
        if brkpt is None: return
        index = self.breakpoints.index(brkpt)
        self.breakpoints.pop(index)
        brkpt._remove()

        if self.draw and redraw: self.reset_numbers()

    @log_class(LOG_LEVEL)
    @locked_function
    @draw_function
    def move(self, brkpt, x):
        """ Move a given breakpoint to a given x coordinate """
        brkpt.move(x)

    @log_class(LOG_LEVEL)
    def count(self):
        return len(self.breakpoints)

    @log_class(LOG_LEVEL)
    @locked_function
    def undo(self):
        if self.count() == 0: return
        self.remove(self[-1])

    @log_class(LOG_LEVEL)
    def first(self):
        for brkpt in self:
            if brkpt.first: return brkpt

    @log_class(LOG_LEVEL)
    def last(self):
        for brkpt in self:
            if brkpt.last: return brkpt

    def internal(self):
        brkpts = []
        for brkpt in self:
            if not brkpt.last and not brkpt.first:
                brkpts.append(brkpt)
        return brkpts

    def ends(self):
        return [self.first(), self.last()]

    def enforce_ends(self):
        """ Remove breakpoints not between the first and last """
        minmax = self.minmax()
        # avoid changing the thing we're looping through as we loop through it
        brkpt_to_remove = []
        for brkpt in self:
            if not self.x_in_bounds(brkpt.x, minmax, inclusive = True):
                brkpt_to_remove.append(brkpt)

        for brkpt in brkpt_to_remove:
            self.remove(brkpt)

    @log_class(LOG_LEVEL)
    @draw_function
    def draw_numbers(self):
        """ Draw numbers at the midpoint between breakpoints corresponding to
        each audio segment """
        brkpts = self.true_breakpoints(scale_to_sound = False)
        txt_kwargs = {"fontfamily": "Palatino Linotype",
                      "fontsize": 10, "color": "black"}
        if brkpts is None or len(brkpts) < 2: return
        for k in range(len(brkpts) - 1):
            #add halfway between breakpoints
            x = (brkpts[k+1] + brkpts[k])/2
            y = self.figure.get_ylim()[0]*0.97 #add to bottom of plot
            text = str(k+1)
            fig_num = self.figure.text(x=x, y=y, s=text, **txt_kwargs)
            self.figure_numbers.append(fig_num)

    @log_class(LOG_LEVEL)
    @draw_function
    def remove_numbers(self):
        """ Remove all numbers from the canvas """
        for fig_num in self.figure_numbers:
            fig_num.remove()
        self.figure_numbers = []

    @log_class(LOG_LEVEL)
    @draw_function
    def reset_numbers(self):
        """ Remove all numbers from the canvas and redraw them """
        self.remove_numbers()
        self.draw_numbers()

    @log_class(LOG_LEVEL)
    @locked_function
    @draw_function
    def reset(self):
        """ Remove all breakpoints """
        for brkpt in self:
            self.remove(brkpt, redraw = False)
        self.breakpoints = []

    @log_class(LOG_LEVEL)
    def get_x(self, sort = True, include_ends = True):
        breakpoints_x = []
        for brkpt in self:
            if include_ends or (not self.first and not self.last):
                breakpoints_x.append(brkpt.x)
        if sort:
            return sorted(breakpoints_x)
        else:
            return breakpoints_x

    @log_class(LOG_LEVEL)
    def get_closest(self, x, xmin = None, xmax = None, brkpts = None):
        xmin_default, xmax_default = self.minmax()
        xmax = xmax_default if xmax is None else xmax
        xmin = xmin_default if xmin is None else xmin

        brkpt_distance = abs(xmin) + abs(xmax)
        closest_brkpt = None

        if brkpts is None: brkpts = self.breakpoints
        for brkpt in brkpts:
            dist = abs(brkpt.x - x)
            if (dist < brkpt_distance and brkpt.x <= xmax and xmin <= brkpt.x):
                brkpt_distance = dist
                closest_brkpt = brkpt
        return closest_brkpt

    @log_class(LOG_LEVEL)
    def true_breakpoints(self, scale_to_sound = True):
        brkpts_x = self.get_x(sort = True, include_ends = True)
        scale = self.get_scale()
        if scale_to_sound:
            for i, x in enumerate(brkpts_x):
                brkpts_x[i] *= scale
        return brkpts_x

    @log_class(LOG_LEVEL)
    def get_scale(self):
        return self.scale

class AudioCanvasEvents(dw.WidgetEvents):
    def log_event(self, sequence, event, **kwargs):
        event_dict = {
            "x": event.x, "y": event.x,
            "ydata": event.__dict__.get("ydata", None),
            "xdata": event.__dict__.get("xdata", None),
            **kwargs
            }
        self.last = {**event_dict, "sequence": sequence}
        self._edict[sequence] = event_dict

class AudioCanvas:
    @log_class(LOG_LEVEL)
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
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.breakpoints = AudioBreakpoints(
            draw = True, figure = self.figure,
            draw_func = self.draw, audio_canvas = self)
        self.locked = False
        self.waveform = None

        self._mpl_connect("key_press_event", self._on_key_press)
        self._mpl_connect("button_press_event", self._on_button_press)
        self._mpl_connect("key_release_event", self._on_key_release)

        # dictionary of functions to run in each event.
        self.mpl_connections = {
            "key_press_event": [],
            "button_press_event": [],
            "key_release_event": []
            }
        self.mpl_connect("key_press_event", self._on_key_press_default)
        self.mpl_connect("button_press_event", self._on_button_press_default)
        self.mpl_connect("key_release_event", self._on_key_release_default)

        self._control_pressed = False
        self._shift_pressed = False
        self._alt_pressed = False

        self.events = AudioCanvasEvents(self.canvas.get_tk_widget())
        self.events.add("<1>")
        self.events.add("<<BreakpointAdd>>")
        self.events.add("<<BreakpointRemove>>") #TODO
        self.events.add("<<BreakpointMove>>") #TODO
        self.events.add("<<WaveformDisplay>>") #TODO

    @log_class(LOG_LEVEL)
    def config(self, **kwargs):
        #TODO
        return

    @log_class(LOG_LEVEL)
    def _mpl_connect(self, s, func):
        """ Bind the default functions which handle future calls with additional
        bound functions """
        self.canvas.mpl_connect(s, func)

    @log_class(LOG_LEVEL)
    def mpl_connect(self, s, func):
        """ Bind a canvas event to a particular function. Can be run multiple
        times to bind multiple functions """
        if not s in self.mpl_connections:
            raise ValueError(f"{s} is not a valid event string")
        self.mpl_connections[s] += [func]

    @log_class(LOG_LEVEL)
    def bind(self, sequence = None, func = None, add = None):
        self.get_widget().bind(sequence = sequence, func = func, add = add)

    @log_class(LOG_LEVEL)
    @locked_function
    def clear(self):
        self.toolbar.home()
        if not self.waveform is None:
            self.waveform.remove()
            self.waveform = None
        self.breakpoints.reset()
        self.draw()
        self.focus()

    @log_class(LOG_LEVEL)
    @locked_function
    def display_waveform(self, audio):
        subsampling_rate = self.__dict__.get("subsampling_rate", 1000)

        self.clear()

        self.sound = audio
        self.sound_length = len(audio)
        self.sound_subsample = self.sound.get_array_of_samples()[0::subsampling_rate]
        self.sound_subsample_length = len(self.sound_subsample)
        plot_config = {"color": self.waveform_colour}
        self.waveform, = self.figure.plot(self.sound_subsample, **plot_config)

        # add breakpoints at start and end
        self.breakpoints.scale = self.get_scale()
        self.breakpoints.add(x = 0, first = True, color = "black",
                             figure = self.figure)

        self.breakpoints.add(x = self.sound_subsample_length - 1, last = True,
                             color = "black", figure = self.figure)

        self.breakpoints.reset_numbers()
        self.scale_canvas()
        self.draw()
        self.toolbar.update()

    @log_class(LOG_LEVEL)
    @locked_function
    def scale_canvas(self):
        self.figure.set_autoscalex_on(True)
        self.figure.set_autoscaley_on(True)
        self.figure.set_xlim(xmin = 0, xmax = self.sound_subsample_length)
        self.figure.set_ylim(ymin = min(self.sound_subsample),
                             ymax = max(self.sound_subsample))

    @log_class(LOG_LEVEL)
    def draw(self):
        self.canvas.draw()

    @log_class(LOG_LEVEL)
    def get_closest_breakpoint(
            self, event, only_visible = True, only_ends = False,
            exclude_ends = True, sensitivity = 2, trace = None
            ):
        """
        Return the closest breakpoint to the given x coordinate. If there are
        no breakpoints within the tolerance, return None.
        """
        if event.xdata is None: return

        if only_ends: exclude_ends = False

        if only_ends:
            brkpts = self.breakpoints.ends()
        elif exclude_ends:
            brkpts = self.breakpoints.internal()
        else:
            brkpts = self.breakpoints

        min_graph_xdata,max_graph_xdata = self.figure.get_xbound()

        if only_visible:
            closest_brkpt = self.breakpoints.get_closest(
                event.xdata, min_graph_xdata, max_graph_xdata, brkpts)
        else:
            closest_brkpt = self.breakpoints.get_closest(
                event.xdata, brkpts = brkpts)

        #calculate the tolerance level
        if sensitivity > 0:
            if closest_brkpt is None: return

            # Percentage of self.visual_frame.winfo_width() given over to blank
            # space before the start of the waveform
            # left_pad = self.visual_frame.winfo_width()*0.125
            left_pad = self.master.winfo_width()*0.03
            figure_start_x = self.master.winfo_rootx()

            brkpt_xdata = closest_brkpt.x
            clicked_pixel_x = event.x + figure_start_x

            # The pixel location of the breakpoint is interpolated based on the
            # known event pixel x and data x, the known data minimum and
            # assumed pixel x at that minimum, and the data x of the breakpoint
            interpolated_pixel = (clicked_pixel_x - figure_start_x - left_pad)
            interpolated_pixel = interpolated_pixel*(brkpt_xdata - min_graph_xdata)
            interpolated_pixel = interpolated_pixel/(event.xdata - min_graph_xdata)
            interpolated_pixel = interpolated_pixel + left_pad + figure_start_x
            breakpoint_pixel_x = round(interpolated_pixel)
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

    @log_class(LOG_LEVEL)
    def tune_get_closest(self, **kwargs):
        return

    @log_class(LOG_LEVEL)
    def lock(self):
        self.locked = True
        self.breakpoints.locked = True

    @log_class(LOG_LEVEL)
    def unlock(self):
        self.locked = False
        self.breakpoints.locked = False

    @log_class(LOG_LEVEL)
    def get_scale(self, scale_up = False):
        if scale_up:
            return self.sound_subsample_length/self.sound_length
        else:
            return self.sound_length/self.sound_subsample_length

    @log_class(LOG_LEVEL)
    def get_widget(self):
        return self.canvas.get_tk_widget()

    @log_class(LOG_LEVEL)
    def focus(self):
        self.canvas.get_tk_widget().focus_force()

    @log_class(LOG_LEVEL)
    def _call_mpl_connections(self, s, event):
        for func in self.mpl_connections[s]:
            func(event = event)

    @log_class(LOG_LEVEL)
    def _on_key_press(self, event):
        self._call_mpl_connections("key_press_event", event)

    @log_class(LOG_LEVEL)
    def _on_button_press(self, event):
        self._call_mpl_connections("button_press_event", event)

    @log_class(LOG_LEVEL)
    def _on_key_release(self, event):
        self._call_mpl_connections("key_release_event", event)

    @log_class(LOG_LEVEL)
    def _on_button_press_default(self, event):
        if event.button == 1:
            self.focus()
        if event.button == 1 and self._control_pressed:
            bp = self.get_closest_breakpoint(
                event = event,
                only_ends = True,
                exclude_ends = False,
                sensitivity = 0,
                only_visible = False
                )
            if bp is None: return
            bp.move(x = event.xdata)
            self.breakpoints.enforce_ends()
        elif event.button == 1 and self._shift_pressed:
            bp = self.get_closest_breakpoint(event)
            self.breakpoints.remove(bp)
        elif event.button == 1 and self._alt_pressed:
            bp = self.get_closest_breakpoint(event)
            if bp is None: return
            bp.move(x = event.xdata)
            self.breakpoints.enforce_ends()

    @log_class(LOG_LEVEL)
    def _on_key_press_default(self, event):
        key_press_handler(event, self.canvas, self.toolbar)

        if event.key == 'enter':
            self.breakpoints.add(event.xdata)
        elif event.key == ' ': #space key
            self.breakpoints.add(event.xdata)
        elif event.key == 'ctrl+z':
            self.breakpoints.undo()
        elif event.key == "control":
            self._control_pressed = True
        elif event.key == "shift":
            self._shift_pressed = True
            self.master.after(500, self._depress_key, event.key)
        elif event.key == "alt":
            self._alt_pressed = True
            self.master.after(500, self._depress_key, event.key)

    @log_class(LOG_LEVEL)
    def _on_key_release_default(self, event):
        if event.key == "control":
            self._control_pressed = False
        elif event.key == "shift":
            self._shift_pressed = False
        elif event.key == "alt":
            self._alt_pressed = False

    @log_class(LOG_LEVEL)
    def _depress_key(self, key):
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


if __name__ == "__main__":
    pass
    import prospero_constants as prc
    import prospero_functions as prf
    import prospero_resources as prr

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

            self.tab_audio_functions = tk.Frame(
                self.root, bg = self.c.colour_background)

            self.audio_functions = AudioFunctions(parent = self)

            self.tab_audio_functions.grid(row = 0, column = 0,
                                      **self.pr.c.grid_sticky)
            self.root.rowconfigure(0, weight = 1)
            self.root.columnconfigure(0, weight = 1)

            #handles the window close event
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)

        def start(self):
            self.root.eval('tk::PlaceWindow . center')
            self.root.mainloop()

        def destroy(self, event = None):
            self.running = False
            self.audio_functions.audio_interface.end_audio_process()
            self.root.quit()
            self.root.destroy()
            return event

    prospero = Prospero(trace = {"source": "initialise class",
                                  "parent": __name__})
    prospero.start()