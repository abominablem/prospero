# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 20:07:22 2021

@author: marcu
"""

import tkinter as tk
import config
import os
import inspect
from datetime import datetime
from search_box import SearchBox
from io_directory import IODirectory
from arrange_widgets import WidgetSet
from value_from_filename import ValueFromFilename
from global_vars import LOG_LEVEL
import described_widgets as dw
from mh_logging import log_class

class Naming:
    column_map = {'composer': 'Composer',
                  'album': 'Album',
                  'number': '#',
                  '#': '#',
                  'track': 'Track',
                  'performer': 'Performer(s)',
                  'performer(s)': 'Performer(s)',
                  'year': 'Year',
                  'genre': 'genre',
                  'url': 'URL'}

    @log_class(LOG_LEVEL)
    def __init__(self, parent):
        self.root = parent.root
        self.parent = parent
        self.pr = parent.pr
        self.tab = parent.tab_naming
        self.name = self.__class__.__name__

        frame_kwargs = {"bg": self.pr.c.colour_background}
        self.widget_frame = tk.Frame(self.tab, **frame_kwargs)

        self.io_directory = IODirectory(
            parent = self,
            master = self.widget_frame,
            call_after_input = self.populate_treeview,
            call_after_input_kwargs = {"populate_values": False}
            )

        self.search_box = SearchBox(parent = self, master = self.widget_frame)

        self.treeview_info = {
            1: {"header": "Original name", "width": self.pr.c.width_text_long,
                "stretch": True, "anchor": "w"},
            2: {"header": "Composer", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w"},
            3: {"header": "Album", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w"},
            4: {"header": "#", "width": self.pr.c.width_text_tiny,
                "stretch": False, "anchor": "center"},
            5: {"header": "Track", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w"},
            6: {"header": "Performer(s)", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w"},
            7: {"header": "Year", "width": self.pr.c.width_text_tiny,
                "stretch": False, "anchor": "center"},
            8: {"header": "Genre", "width": self.pr.c.width_text_veryshort,
                "stretch": True, "anchor": "w"},
            9: {"header": "URL", "width": self.pr.c.width_text_short,
                "stretch": True, "anchor": "w"},
            10: {"header": "Final name", "width": self.pr.c.width_text_long,
                 "stretch": True, "anchor": "w"},
            11: {"header": "Done", "width": self.pr.c.width_text_tiny,
                 "stretch": False, "anchor": "center"},
            }

        self.file_list_treeview = dw.SimpleTreeview(
            self.widget_frame, self.treeview_info)

        btn_import_files = tk.Button(
            self.io_directory.frame,
            text = "Import Files",
            background = self.pr.c.colour_interface_button,
            command = self._btn_import_files_Click
            )
        self.io_directory.add_widget(
            widget = btn_import_files, fixed_width = True, row = "input",
            column = "end"
            )

        btn_rename_files = tk.Button(
            self.io_directory.frame,
            text="Rename Files",
            background = self.pr.c.colour_interface_button,
            command = self._btn_rename_files_click
            )
        self.io_directory.add_widget(
            widget = btn_rename_files, fixed_width = True, row = "output",
            column = btn_import_files
            )

        #search box
        self.file_list_treeview.bind("<KeyPress-Alt_L>", self._key_press_alt)
        self.file_list_treeview.bind("<KeyRelease-Alt_L>", self._key_release_alt)
        self.file_list_treeview.bind("<Alt-1>", self._alt_mouse_1)

        #treeview values
        self.file_list_treeview.events.add("<1>")
        self.file_list_treeview.bind("<Double-1>", self.edit_value_via_interface)
        self.file_list_treeview.bind("<Control-Shift-D>", lambda event: self.copy_around("up", event))
        self.file_list_treeview.bind("<Control-d>", lambda event: self.copy_around("down", event))
        self.file_list_treeview.bind("<Control-Shift-R>", lambda event: self.copy_around("left", event))
        self.file_list_treeview.bind("<Control-r>", lambda event: self.copy_around("right", event))
        self.file_list_treeview.bind("<Control-s>", self.save_treeview)

        widgets = {
            1: {'widget': self.io_directory,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            2: {'widget': self.file_list_treeview,
                'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                'stretch_width': True, 'stretch_height': True},
            3: {'widget': self.search_box,
                'grid_kwargs': self.pr.c.grid_sticky,
                'stretch_width': True},
            }

        self.widget_set = WidgetSet(self.widget_frame, widgets,
                                    layout = [[1], [2], [3]])
        self.widget_set.grid(row = 0, column = 0, **self.pr.c.grid_sticky)
        self.tab.rowconfigure(index = 0, weight = 1)
        self.tab.columnconfigure(index = 0, weight = 1)

        treeview_config = \
            config.config.config_dict[self.name]["FileListTreeview"]

        if "FileListTreeview" in config.config.config_dict[self.name]:
            if treeview_config["load_from_json"] == True:
                if "treeview_values" in treeview_config.keys():
                    self.file_list_treeview.from_json(
                        treeview_config["treeview_values"])
        else:
            self.populate_treeview(populate_values = False)

        self._configure_last_called = datetime.min
        self.iter_check = 0
        self.file_list_treeview.bind("<<ValueChange>>", self.update_final_name)

    @log_class(LOG_LEVEL)
    def update_final_name(self, event):
        """
        Update the final name of the last updated file names treeview row
        """
        vc_event = self.file_list_treeview.events["<<ValueChange>>"]
        updated_col = vc_event["column"]
        updated_row = vc_event["row"]
        if updated_col == "Final name": return
        elif updated_row is None: return

        new_filename = self.pr.f.filename_from_dict(
            parts_dict = self.file_list_treeview.values_dict(updated_row)
            )
        self.file_list_treeview.set(updated_row, "Final name", new_filename)

    @log_class(LOG_LEVEL)
    def _btn_rename_files_click(self):
        self.rename_valid_files()

    @log_class(LOG_LEVEL)
    def _btn_import_files_Click(self):
        populate_values = tk.messagebox.askquestion(
            "Reset field values?",
            message="Do you want to reset all field values?",
            default='no'
            )
        populate_values = (populate_values == 'yes')
        self.populate_treeview(populate_values = populate_values)

    @log_class(LOG_LEVEL)
    def populate_treeview(self, populate_values = True):
        """
        Populate the treeview with file names, and optionally with
        suggested values
        """
        current_filenames = list(self.file_list_treeview.get_children())
        file_list = os.listdir(self.io_directory.input_directory)
        new_filenames = [file[:-4] for file in file_list
                         if file[-4:] == self.pr.c.file_extension]

        #Update the list of filenames in the treeview, adding new filenames and
        #deleting old ones where appropriate
        #Assumes that the two lists of filenames are sorted in ascending
        #alphabetical order
        i=0 #iterable for current_filenames
        j=0 #iterable for new_filenames
        len_c = len(current_filenames)
        len_n = len(new_filenames)
        while i < len_c or j < len_n:
            if i > len_c-1:
                # Add the rest of the elements of New Filenames as rows
                add, remove = True, False
                new_name = new_filenames[j]

            elif j > len_n-1:
                # Remove the rest of the elements of Current Filenames
                add, remove = False, True
                cur_name = current_filenames[i]

            else:
                cur_name = current_filenames[i]
                new_name = new_filenames[j]
                cur_name_lower = cur_name.lower()
                new_name_lower = new_name.lower()

                if cur_name == new_name:
                    add, remove = False, False

                elif cur_name_lower < new_name_lower:
                    add, remove = False, True

                elif cur_name_lower > new_name_lower:
                    add, remove = True, False

                else:
                    add, remove = False, False

            if add:
                values = self.get_values_from_filename(new_name,
                                                       )
                self.file_list_treeview.insert(
                    "", index = j, text = new_name, iid = new_name,
                    values = values)
                self.match_filename_pattern(new_name)
                self.match_keywords(new_name)
                i+=0
                j+=1
            elif remove:
                self.file_list_treeview.delete(cur_name)
                i+=1
                j+=0
            elif populate_values:
                values = self.get_values_from_filename(new_name,
                                                       )
                self.file_list_treeview.item(new_name, values = values)
                self.match_filename_pattern(new_name)
                self.match_keywords(new_name)
                i+=1
                j+=1
            else:
                pass
                i, j = i+1, j+1
        return

    @log_class(LOG_LEVEL)
    def edit_value_via_interface(self, event):
        """
        Open a window with the selected filename where a value can be specified
        for the selected cell
        """
        #Identify the column clicked
        clicked_column_id = self.file_list_treeview.events.last["column"]

        #exit if the first column (filename) is clicked
        if clicked_column_id == "#0":
            return

        #Identify the filename of the row clicked
        clicked_row = self.file_list_treeview.events.last["row"]

        # exit if an empty row is clicked
        if clicked_row is None or clicked_row == "":
            return

        ValueFromFilename(
            parent = self,
            filename = clicked_row,
            columnString = self.file_list_treeview.translate_column(
                clicked_column_id
                ),
            columnId = clicked_column_id,
            treeview = self.file_list_treeview
            )

    @log_class(LOG_LEVEL)
    def match_keywords(self, filename, overwrite = False):
        """
        Matches filename fields based on already entered keywords.
        Can take any number of Composer/Album/#/Track/Genre/Year and outputs
        some subset of those not taken as inputs.
        """
        values_dict = {}
        for field in ["Composer", "Album", "#", "Genre", "Year", "Track"]:
            values_dict[field] = self.file_list_treeview.set_translate(
                filename, field)

        keyword_dicts = config.keyword_dict.regex_dict

        for keyword_key in keyword_dicts:
            compare_dict = keyword_dicts[keyword_key]
            #run through all available keyword mapping dictionaries, overlaying
            #to get the best output
            invalid_match = False
            for key in compare_dict['key']:
                if compare_dict['key'][key].lower() != values_dict[key].lower():
                    invalid_match = True
                    break
            if invalid_match: continue
            #run only once a full set of valid pattern matches has been made
            for field in compare_dict['value']:
                if values_dict[field] == "" or overwrite:
                    self.file_list_treeview.set(filename, field,
                                              compare_dict['value'][field])
                    values_dict[field] = compare_dict['value'][field]
        return values_dict

    @log_class(LOG_LEVEL)
    def match_filename_pattern(self, filename, overwrite = False):
        match = self.pr.f.match_filename_pattern(filename)
        for k in match:
            coln = self.column_map[k]
            if overwrite:
                self.file_list_treeview.set(filename, coln, match[k])
            else:
                cur_v = self.file_list_treeview.set(filename, coln)
                if cur_v.strip() == "" or cur_v is None:
                    self.file_list_treeview.set(filename, coln, match[k])

    @log_class(LOG_LEVEL)
    def get_values_from_filename(self, filename):
        values = [self.pr.f.suggest_value(filename, field)
                  for field in self.file_list_treeview.get_columns()]
        return values

    @log_class(LOG_LEVEL)
    def copy_around(self, direction, event = None):
        """
        Copy a single value to multiple contiguous rows or an adjacent column.
        """
        if not self.file_list_treeview.has_selection():
            return

        if not direction in ["up", "down", "left", "right"]:
            raise ValueError("Invalid direction %s" % direction)

        selected_items = self.file_list_treeview.selection()
        click_col_id = self.file_list_treeview.events["<1>"]["column"]

        # ignore if key column was the last one clicked
        if click_col_id == "#0":
            return
        # ignore if column clicked is the first column after the key and the
        # value is being taken from the left (copied to right)
        if direction == "right" and click_col_id == "#1":
            return

        single_row = (len(selected_items) == 1)

        index_map = {"up": -1, "down": 0, "left": 0, "right": -1}
        func_map = {
            "up": self.file_list_treeview.next,
            "down": self.file_list_treeview.prev,
            "left": self.file_list_treeview.next_column,
            "right": self.file_list_treeview.prev_column,
            }

        if direction in ["up", "down"]:
            value_row = selected_items[index_map[direction]]
            if single_row:
                copy_value = self.file_list_treeview.set(
                    func_map[direction](value_row), click_col_id)
            else:
                copy_value = self.file_list_treeview.set(
                    value_row, click_col_id)

            for item in selected_items:
                self.set_treeview_value(item, click_col_id, copy_value)
        else:
            value_col = func_map[direction](click_col_id)
            for item in selected_items:
                copy_value = self.file_list_treeview.set(item, value_col)
                self.set_treeview_value(item, click_col_id, copy_value)

    @log_class(LOG_LEVEL)
    def set_treeview_value(self, item, column = None, value = None):
        self.file_list_treeview.set(item, column, value)
        self.match_filename_pattern(item)
        self.match_keywords(item)

    @log_class(LOG_LEVEL)
    def _key_press_alt(self, event):
        """
        Create the search box GUI and maintain it while the bound key is held
        down
        """
        self.search_box.maintain()

    @log_class(LOG_LEVEL)
    def _key_release_alt(self, event):
        """
        Destroy the search box GUI when the bound key is released
        """
        self.search_box.destroy()

    @log_class(LOG_LEVEL)
    def _alt_mouse_1(self, event):
        if self.search_box is None:
            return
        self.search_box.add(self.file_list_treeview.events["Alt-1"]["cell"])

    @log_class(LOG_LEVEL)
    def rename_valid_files(self):
        #prompt for confirmation of action
        message_box = tk.messagebox.askquestion(
            "Rename all files",
            "Are you sure you wish to tag and rename all files? Only files "
            "with valid final names will be affected.",
            icon = "warning"
            )

        if message_box != "yes":
            return

        for filename in self.file_list_treeview.get_children():
            new_filename = self.file_list_treeview.set(filename, "Final name")
            if ((new_filename != "" and not new_filename is None) and
                (self.file_list_treeview.set(filename, "Done") != "✓")):
                exception = False
                text = None
                #File operation related exceptions, can be raised at any
                #point
                try:
                    #Tag file with ID3 tags
                    try:
                        self.tag_file(filename)
                    except ValueError as e:
                        text = str(e)
                        raise
                    except:
                        text = "Failed to tag file"
                        raise

                    #Add keyword matches
                    try:
                        self.add_keyword_matching(filename,
                                                  )
                    except:
                        text = "Failed to add keyword matching"
                        raise

                    #Add to Insight
                    try:
                        self.add_insight(filename)
                    except:
                        text = "Failed to add to Insight"
                        raise

                    #rename file
                    v = {"old_directory": self.io_directory.input_directory,
                         "old_name": filename + self.pr.c.file_extension,
                         "new_directory": self.io_directory.output_directory,
                         "new_name": new_filename + self.pr.c.file_extension}
                    try:
                        self.pr.f.rename_file(**v)
                    except:
                        text = "Failed to rename file"
                        raise

                except FileNotFoundError:
                    exception = True
                    text = "Renaming failed, original file not found"
                except FileExistsError:
                    exception = True
                    text = "Renaming failed, new file already exists"
                except Exception as err:
                    """ All errors not handled elsewhere """
                    exception = True
                    error = err

                if exception:
                    if text is None: text = "An unexpected error occurred"
                    done_text = "✘ - %s (%s)" % (text, error)
                else:
                    done_text = "✓"
                self.file_list_treeview.set(filename, "Done", done_text)

        self.save_treeview()

    @log_class(LOG_LEVEL)
    def tag_file(self, filename):
        tags = {
            "composer": self.file_list_treeview.set(filename, "Composer"),
            "album": self.file_list_treeview.set(filename, "Album"),
            "track": self.file_list_treeview.set(filename, "Track"),
            "number": self.file_list_treeview.set(filename, "#"),
            "performer(s)": self.file_list_treeview.set(filename, "Performer(s)"),
            "year": self.file_list_treeview.set(filename, "Year"),
            "genre": self.file_list_treeview.set(filename, "Genre"),
            "url": self.file_list_treeview.set(filename, "URL"),
            }
        self.pr.f.tag_file(
            directory = self.io_directory.input_directory,
            filename = filename,
            tags = tags
            )

    @log_class(LOG_LEVEL)
    def save_treeview(self, event = None):
        """ Save the treeview contents for recovery later. Immediately
        dump to disk so if the program exits early the data is still saved """
        config.config.config_dict[self.name]["FileListTreeview"]["treeview_values"] = self.file_list_treeview.to_json()
        config.config.dump_values()

    @log_class(LOG_LEVEL)
    def add_keyword_matching(self, filename):
        values_dict = {}
        for field in ["Composer", "Album", "#", "Genre", "Year", "Track"]:
            values_dict[field] = self.file_list_treeview.set(filename, field)

        self.pr.f.add_keyword_pattern(values_dict)

    @log_class(LOG_LEVEL)
    def add_insight(self, filename):
        values = self.file_list_treeview.get_dict(iid = filename,
                                                  include_key = True)
        del values["Done"]
        values["original_path"] = self.io_directory.input_directory
        values["final_path"] = self.io_directory.output_directory
        filepath = os.path.join(self.io_directory.input_directory,
                                filename + self.pr.c.file_extension)
        ctime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
        values["date_created"] = ctime
        self.pr.insight_rn.add_row(**values)

    @log_class(LOG_LEVEL)
    def load_from_config(self):
        return