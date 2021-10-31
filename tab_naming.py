# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 20:07:22 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk
import config
import os
import re
from datetime import datetime
from search_box import SearchBox
from io_directory import IODirectory
from arrange_widgets import WidgetSet
from value_from_filename import ValueFromFilename
import described_widgets as dw

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
    
    def __init__(self, parent, trace = None):
        self.root = parent.root
        self.parent = parent
        self.pr = parent.pr
        self.tab = parent.tab_naming
        self.name = self.__class__.__name__
        
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}

        frame_kwargs = {"bg": self.pr.c.colour_background}
        self.widget_frame = tk.Frame(self.tab, **frame_kwargs)
        
        self.io_directory = IODirectory(
            parent = self,
            master = self.widget_frame,
            trace = inf_trace, 
            call_after_input = self.populate_treeview, 
            call_after_input_kwargs = {"populate_values": False}
            )
        
        self.search_box = SearchBox(
            parent = self,
            master = self.widget_frame,
            trace = inf_trace
            )

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

        btnImportFiles = tk.Button(
            self.io_directory.frame,
            text = "Import Files", 
            background = self.pr.c.colour_interface_button, 
            command = self._btnImportFiles_Click
            )
        self.io_directory.add_widget(widget = btnImportFiles, 
                                     fixed_width = True, trace = inf_trace, 
                                     row = "input", column = "end")
        
        btnRenameFiles = tk.Button(
            self.io_directory.frame,
            text="Rename Files", 
            background = self.pr.c.colour_interface_button, 
            command = self._btnRenameFiles_click
            )
        self.io_directory.add_widget(widget = btnRenameFiles, 
                                     fixed_width = True, trace = inf_trace, 
                                     row = "output", column = btnImportFiles)

        #search box
        self.file_list_treeview.bind("<KeyPress-Alt_L>", lambda event: self._key_press_alt(event, trace = {"source": "bound event", "widget": self.name + ".FileListTreeview", "event": "<KeyPress-Alt_L>"}))
        self.file_list_treeview.bind("<KeyRelease-Alt_L>", lambda event: self._key_release_alt(event, trace = {"source": "bound event", "widget": self.name + ".FileListTreeview", "event": "<KeyRelease-Alt_L>"}))
        self.file_list_treeview.bind("<Alt-1>", lambda event: self._alt_mouse_1(event, trace = {"source": "bound event", "widget": "Naming.FileListTreeview", "event": "<Alt-1>"}))
        
        #treeview values
        self.file_list_treeview.bind("<1>", lambda event: self._treeview_mouse1_click(event, trace = {"source": "bound event", "widget": self.name + ".FileListTreeview", "event": "<1>"}))
        self.file_list_treeview.bind("<Double-1>", lambda event: self.edit_value_via_interface(event, trace = {"source": "bound event", "widget": self.name + ".FileListTreeview", "event": "<Double-1>"}))
        self.file_list_treeview.bind("<Control-d>", lambda event: self.copy_from_above(event, trace = {"source": "bound event", "widget": self.name + ".FileListTreeview", "event": "<Control-d>"}))
        self.file_list_treeview.bind("<Control-s>", lambda event: self.save_treeview(event, trace = {"source": "bound event", "widget": self.name + ".save_treeview", "event": "<Control-s>"}))
        
        widgets = {1: {'widget': self.io_directory,
                       'grid_kwargs': self.pr.c.grid_sticky,
                       'stretch_width': True},
                   2: {'widget': self.file_list_treeview,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                       'stretch_width': True, 'stretch_height': True},
                   3: {'widget': self.search_box,
                       'grid_kwargs': self.pr.c.grid_sticky,
                       'stretch_width': True},
                   }

        self.widget_set = WidgetSet(self.widget_frame,
                                    widgets,
                                    layout = [[1], [2], [3]])
        self.widget_set.grid(row = 0, column = 0, **self.pr.c.grid_sticky)
        self.tab.rowconfigure(index = 0, weight = 1)
        self.tab.columnconfigure(index = 0, weight = 1)

        treeview_config = \
            config.config.config_dict[self.name]["FileListTreeview"]
        
        if "FileListTreeview" in config.config.config_dict[self.name].keys():
            if treeview_config["load_from_json"] == True:
                if "treeview_values" in treeview_config.keys():
                    self.pr.f.json_to_treeview(
                        treeview = self.file_list_treeview,
                        json_dict = treeview_config["treeview_values"],
                        trace = inf_trace
                        )
        else:
            self.populate_treeview(populate_values = False, trace = inf_trace)
            
        self._configure_last_called = datetime.min

        return
    
    def _btnRenameFiles_click(self, trace = None):
        self.pr.f._log_trace(self, "_btnRenameFiles_click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnRenameFiles_click"}
        
        self.rename_valid_files(trace = inf_trace)
        return
    
    def _btnImportFiles_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnInputFiles_click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnInputFiles_click"}
        
        populate_values = tk.messagebox.askquestion(
            "Reset field values?", 
            message="Do you want to reset all field values?", 
            default='no'
            )
        populate_values = (populate_values == 'yes')
        self.populate_treeview(populate_values = populate_values, 
                               trace = inf_trace)
        return
    
    def populate_treeview(self, populate_values = True, trace = None):
        self.pr.f._log_trace(self, "populate_treeview", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".populate_treeview"}
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
            
            #######
            if add:
                values = self.get_values_from_filename(new_name, 
                                                       trace = inf_trace)
                self.file_list_treeview.insert("", 
                                             index=j, 
                                             text = new_name, 
                                             iid = new_name, 
                                             values = values
                                             )
                self.match_filename_pattern(new_name, trace = inf_trace)
                self.match_keywords(new_name, trace = inf_trace)
                self.set_final_name(new_name, trace = inf_trace)
                i+=0
                j+=1
            elif remove:
                self.file_list_treeview.delete(cur_name)
                i+=1
                j+=0
            elif populate_values:
                values = self.get_values_from_filename(new_name, 
                                                       trace = inf_trace)
                self.file_list_treeview.item(new_name, values = values)
                self.match_filename_pattern(new_name, trace = inf_trace)
                self.match_keywords(new_name, trace = inf_trace)
                self.set_final_name(new_name, trace = inf_trace)
                i+=1
                j+=1
            else:
                pass
                i, j = i+1, j+1
        return
        
    def edit_value_via_interface(self, event, trace = None):
        self.pr.f._log_trace(self, "edit_value_via_interface", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".edit_value_via_interface"}
        """
        Open a window with the selected filename where a value can be specified 
        for the selected cell
        """
            
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
            filename = clicked_row,
            columnString = self.treeview_column_id_to_name(clicked_column_id),
            columnId = clicked_column_id,
            treeview = self.file_list_treeview,
            trace = inf_trace
            )
        return event
    
    def match_keywords(self, filename, overwrite = False, trace = None):
        """
        Matches filename fields based on already entered keywords.
        Can take any number of Composer/Album/#/Track/Genre/Year and outputs
        some subset of those not taken as inputs.
        """
        self.pr.f._log_trace(self, "match_keywords", trace)
        values_dict = {}
        for field in ["Composer", "Album", "#", "Genre", "Year", "Track"]:
            values_dict[field] = self.file_list_treeview.set(filename, field)
            
        keyword_dicts = config.keyword_dict.regex_dict

        for compare_dict in keyword_dicts.values():
            #run through all available keyword mapping dictionaries, overlaying
            #to get the best output
            for key in compare_dict['key'].keys():
                invalid_match = False
                try:
                    if not re.match(compare_dict['key'][key], values_dict[key], 
                                    re.IGNORECASE):
                        invalid_match = True
                        break
                except:
                    break
            if invalid_match: continue
            #run only once a full set of valid pattern matches has been made    
            for field in compare_dict['value'].keys():
                if values_dict[field] == "" or overwrite:
                    self.file_list_treeview.set(filename, field, 
                                              compare_dict['value'][field])
                    values_dict[field] = compare_dict['value'][field]
        return values_dict
    
    def match_filename_pattern(self, filename, overwrite = False, trace = None):
        self.pr.f._log_trace(self, "match_filename_pattern", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name 
                          + ".match_filename_pattern"}
        match = self.pr.f.match_filename_pattern(filename, inf_trace)
        for k in match:
            coln = self.column_map[k]
            if overwrite:
                self.file_list_treeview.set(filename, coln, match[k])
            else:
                cur_v = self.file_list_treeview.set(filename, coln)
                if cur_v.strip() == "" or cur_v is None:
                    self.file_list_treeview.set(filename, coln, match[k])
        
    
    def get_values_from_filename(self, filename, trace = None):
        self.pr.f._log_trace(self, "get_values_from_filename", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name 
                         + ".get_values_from_filename"}
        
        values = [self.pr.f.suggest_value(filename, field, trace = inf_trace) 
                  for field in self.treeview_info["columns"][1:]]
        return values
        
    def copy_from_above(self, event, trace = None):
        self.pr.f._log_trace(self, "copy_from_above", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".copy_from_above"}
        """
        Copies a value down to all selected rows in certain column
        """
        selected_items = self.file_list_treeview.selection()
        clicked_column_id = self._treeview_mouse1_click_column
        if clicked_column_id == "#0":
            #cancel if the filename ID column was the last column clicked
            return event
        
        #get the value to copy down. If one row is selected, this is the value in
        #the row above. If multiple values are selected, this is the value in the
        #first selected row
        if len(selected_items) == 1:
            value_to_copy = self.file_list_treeview.set(
                self.file_list_treeview.prev(selected_items[0]),
                clicked_column_id
                )
        else:
            value_to_copy = self.file_list_treeview.set(selected_items[0],
                                                      clicked_column_id)
        
        #update the value of all cells in the selected rows and column
        for item in selected_items:
            self.file_list_treeview.set(item, clicked_column_id, value_to_copy)
            self.match_filename_pattern(item, trace = inf_trace)
            self.match_keywords(item, trace = inf_trace)
            self.set_final_name(item, trace = inf_trace)

        self.treeview_info["unsaved_changes"] = True
        return event
    
    def _treeview_mouse1_click(self, event, trace = None):
        self.pr.f._log_trace(self, "_treeview_mouse1_click", trace)
            
        self._treeview_mouse1_click_column = self.file_list_treeview.identify_column(event.x)
        self._treeview_mouse1_click_row = self.file_list_treeview.identify_row(event.y)
        self._treeview_mouse1_click_cell = (
            self._treeview_mouse1_click_row
            if self._treeview_mouse1_click_column == "#0"
            else self.file_list_treeview.set(self._treeview_mouse1_click_row,
                                           self._treeview_mouse1_click_column)
            )
        return event
    
    def treeview_column_id_to_name(self, column_id, trace = None):
        self.pr.f._log_trace(self, "treeview_column_id_to_name", trace)
        headers = self.treeview_info["headers"]
        return headers[int(column_id[1:])]
    
    def _key_press_alt(self, event, trace = None):
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._key_press_alt"}
        """
        Create the search box GUI and maintain it while the bound key is held down
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
        self.search_box.add(self._treeview_mouse1_click_cell, trace = inf_trace)
        return event
    
    def rename_valid_files(self, trace = None):
        #prompt for confirmation of action
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".rename_valid_files"}
        message_box = tk.messagebox.askquestion("Rename all files", 
                                                "Are you sure you wish the tag"
                                                " and rename all files? Only "
                                                "files with valid final names "
                                                "will be affected.", 
                                                icon = "warning")
        
        if message_box == "yes":
            self.pr.f._log_trace(self, "rename_valid_files", trace)
            for filename in self.file_list_treeview.get_children():
                new_filename = self.file_list_treeview.set(filename, "Final name")
                inf_trace = {"source": "function call", 
                             "parent": self.name + ".rename_valid_files", 
                             "add": f"Tagged file {filename}, and renamed to {new_filename}."}
                if (new_filename != "" and not new_filename is None) and (self.file_list_treeview.set(filename, "Done") != "✓"):
                    exception = False
                    #File operation related exceptions, can be raised at any
                    #point
                    try:
                        #Tag file with ID3 tags
                        try:
                            self.tag_file(filename, trace = inf_trace)
                        except ValueError as e:
                            exception = True
                            text = str(e)
                            raise
                        except:
                            exception = True
                            text = "Failed to tag file"
                            raise
                        
                        #Add keyword matches
                        try:
                            self.add_keyword_matching(filename, 
                                                      trace = inf_trace)
                        except:
                            exception = False
                            text = "Failed to add keyword matching"
                            raise
                            
                        #Add to Insight
                        try:
                            self.add_insight(filename, trace = inf_trace)
                        except:
                            exception = True
                            text = "Failed to add to Insight"
                            raise
                            
                        #rename file
                        v = {"old_directory": self.io_directory.input_directory,
                             "old_name": filename + self.pr.c.file_extension,
                             "new_directory": self.io_directory.output_directory,
                             "new_name": new_filename + self.pr.c.file_extension}
                        try:
                            self.pr.f.rename_file(**v, trace = inf_trace)
                        except:
                            exception = True
                            text = "Failed to rename file"
                            raise
                    except FileNotFoundError:
                        exception = True
                        text = "Renaming failed, original file not found"
                    except FileExistsError:
                        exception = True
                        text = "Renaming failed, new file already exists"
                    except:
                        """ All errors not handled elsewhere """
                        pass
                    
                    if exception:
                        done_text = "✘ - " + text
                    else:
                        done_text = "✓"
                    self.file_list_treeview.set(filename, "Done", done_text)
                        
            self.save_treeview(None, trace = inf_trace)
        return
    
    def tag_file(self, filename, trace = None):
        self.pr.f._log_trace(self, "tag_file", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".tag_file"}
        
        tags = {"composer": self.file_list_treeview.set(filename, "Composer"),
                "album": self.file_list_treeview.set(filename, "Album"),
                "track": self.file_list_treeview.set(filename, "Track"),
                "number": self.file_list_treeview.set(filename, "#"),
                "performer(s)": self.file_list_treeview.set(filename, "Performer(s)"),
                "year": self.file_list_treeview.set(filename, "Year"),
                "genre": self.file_list_treeview.set(filename, "Genre"),
                "url": self.file_list_treeview.set(filename, "URL"),
                }
        self.pr.f.tag_file(directory = self.io_directory.input_directory,
                           filename = filename,
                           tags = tags,
                           trace = inf_trace)
        return
    
    def save_treeview(self, event, trace = None):
        self.pr.f._log_trace(self, "save_treeview", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".save_treeview"}
        
        config.config.config_dict[self.name]["FileListTreeview"]["treeview_values"] = self.pr.f.treeview_to_json(self.file_list_treeview, trace = inf_trace)
        config.config.dump_values()
        
    def set_final_name(self, filename, trace = None):
        self.pr.f._log_trace(self, "set_final_name", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".set_final_name"}
        parts = [filename] + list(self.file_list_treeview.item(filename,'values'))
        final_name = self.pr.f.filename_from_parts(parts = parts, 
                                                   headers = self.treeview_info["headers"], 
                                                   trace = inf_trace
                                                   )
        self.file_list_treeview.set(filename, 'Final name', final_name)
        
    def add_keyword_matching(self, filename, trace = None):
        self.pr.f._log_trace(self, "add_keyword_matching", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".add_keyword_matching"}
        values_dict = {}
        for field in ["Composer", "Album", "#", "Genre", "Year", "Track"]:
            values_dict[field] = self.file_list_treeview.set(filename, field)
        
        self.pr.f.add_keyword_pattern(values_dict, trace = inf_trace)
        
    def add_insight(self, filename, trace = None):
        self.pr.f._log_trace(self, "add_insight", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".add_insight"}
        
        values = self.pr.f.get_values_dict(self.file_list_treeview, filename, 
                                           self.treeview_info["headers"])
        del values["Done"]
        values["original_path"] = self.io_directory.input_directory
        values["final_path"] = self.io_directory.output_directory
        filepath = os.path.join(self.io_directory.input_directory, 
                                filename + self.pr.c.file_extension)
        ctime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
        values["date_created"] = ctime
        self.pr.insight_rn.add_row(**values, trace = inf_trace)
        
    def load_from_config(self, trace = None):
        self.pr.f._log_trace(self, "load_from_config", trace)