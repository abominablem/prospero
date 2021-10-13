# -*- coding: utf-8 -*-
"""
Created on Sat May 15 16:35:32 2021

@author: marcu
"""
from pydub import AudioSegment
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
import os
import copy
import re

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
                                               NavigationToolbar2Tk)
# from tkinter.scrolledtext import ScrolledText
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from io_directory import IODirectory
#function imports
from value_from_filename import ValueFromFilename
from audio_interface import AudioInterface
from search_box import SearchBox
import config

# #### REQUIRED ####
# conda install ffmpeg
# Run command prompt as administrator
     

class AudioFunctions():
    def __init__(self, parent, grid_references, trace = None):
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab_audio_functions
        self.name = self.__class__.__name__
        
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        
        #Horrific UI code below.
        self.io_directory = IODirectory(parent = self, trace = inf_trace)
        self.IODirectoryGridRow = grid_references[0]
        self.IODirectoryGridColumn = grid_references[1]
        self.IODirectoryColumnSpan = self.pr.c.columnspan_all
        self.IODirectoryRowSpan = 1
        
        self.io_directory.grid(row = self.IODirectoryGridRow, 
                                column = self.IODirectoryGridColumn, 
                                columnspan = self.IODirectoryColumnSpan,
                                rowspan = self.IODirectoryRowSpan,
                                sticky = "nesw"
                                )        

        self._colour_breakpoint = "#bfb598"
        self._colour_waveform = parent.pr.c.colour_prospero_blue_pastel
        self._plot_background_colour = parent.pr.c.colour_background
        
        self.InputFilesFrameGridRow = (self.IODirectoryGridRow 
                                       + self.IODirectoryRowSpan)
        self.InputFilesFrameGridColumn = self.IODirectoryGridColumn
        self.InputFilesFrameColumnSpan = 1
        self.InputFilesFrameRowSpan = 1
        
        self.input_files_frame = tk.Frame(self.tab, background = 
                                          self.pr.c.colour_background)
        
        self.input_files_frame.grid(row = self.InputFilesFrameGridRow,
                                    column = self.InputFilesFrameGridColumn,
                                    columnspan = self.InputFilesFrameColumnSpan,
                                    rowspan = self.InputFilesFrameRowSpan,
                                    **self.pr.c.grid_sticky_padding_small)
        
        self.VisualFrameGridRow = self.InputFilesFrameGridRow
        self.VisualFrameGridColumn = (self.InputFilesFrameGridColumn 
                                      + self.InputFilesFrameColumnSpan)
        
        self.VisualFrameColumnSpan = 1
        self.VisualFrameRowSpan = self.InputFilesFrameRowSpan
        
        self.visual_frame = tk.Frame(self.tab, 
                                     background = self.pr.c.colour_background, 
                                     highlightthickness = 1, 
                                     highlightcolor = self.pr.c.colour_selection_background)
        self.visual_frame.grid(row = self.VisualFrameGridRow, 
                                column = self.VisualFrameGridColumn, 
                                columnspan = self.VisualFrameColumnSpan,
                                rowspan = self.VisualFrameRowSpan,
                                sticky = "nesw"
                                )
        
        self.AudioControlsGridRow = self.VisualFrameGridRow + self.VisualFrameRowSpan
        self.AudioControlsGridColumn = self.InputFilesFrameGridColumn + self.InputFilesFrameGridColumn
        self.AudioControlsColumnSpan = self.pr.c.columnspan_all
        self.AudioControlsRowSpan = 1
        
        self.audio_interface = AudioInterface(self, trace = {"source": "initialise class", "parent": self.name})
        self.audio_controls_frame = self.audio_interface.frame
        self.audio_controls_frame.grid(row = self.AudioControlsGridRow, 
                              column = self.AudioControlsGridColumn, 
                              columnspan = self.AudioControlsColumnSpan,
                              rowspan = self.AudioControlsRowSpan,
                              sticky = "nesw"
                              )
        
        self.NamesFrameGridRow = self.AudioControlsGridRow + self.AudioControlsRowSpan
        self.NamesFrameGridColumn = self.InputFilesFrameGridColumn + self.InputFilesFrameGridColumn
        self.NamesFrameColumnSpan = self.pr.c.columnspan_all
        self.NamesFrameRowSpan = 1
        
        self.names_frame = tk.Frame(self.tab, background = self.pr.c.colour_background)
        self.names_frame.grid(row = self.NamesFrameGridRow, 
                              column = self.NamesFrameGridColumn, 
                              columnspan = self.NamesFrameColumnSpan,
                              rowspan = self.NamesFrameRowSpan,
                              sticky = "nesw"
                              )
        
        self.search_box_gridrow = self.NamesFrameGridRow + self.NamesFrameRowSpan
        self.search_box_gridcolumn = self.NamesFrameGridColumn
        self.search_box_columnspan = self.pr.c.columnspan_all
        self.search_box_rowspan = 1
        
        self.search_box = SearchBox(parent = self,
                                    trace = inf_trace,
                                    row = self.search_box_gridrow, 
                                    column = self.search_box_gridcolumn, 
                                    columnspan = self.search_box_columnspan,
                                    rowspan = self.search_box_rowspan,
                                    sticky = "nesw"
                                    )
        
        self.breakpoints = [] #list of mpl Line2D objects (breakpoints) for addition and removal to figure
        self.breakpoints_x = [] #list of x coordinates of the breakpoint
        self.figure_numbers = []
        self.waveform = None
        self.start_breakpoint = None
        self.end_breakpoint = None
        self._control_pressed = False
        self._shift_pressed = False
        self._alt_pressed = False
        self.playback_bar = None
        self._action_stack = []
        self._stack_location = -1
        
        self._configure_last_called = datetime.min
        self._initialise_canvas(trace = inf_trace)
        
        """
        ##########################################################################################
        ################################ INPUT FILES #############################################
        ##########################################################################################
        """         

        self.treeview_input_files_columns = ["#0"]
        self.treeview_input_files_headers = ["Filename"]
        self.treeview_input_files_column_widths = [self.pr.c.width_text_long]
        self.treeview_input_files_fixed_width = [False]
        
        self.treeview_input_files = ttk.Treeview(self.input_files_frame)
        
        self.pr.f.configure_treeview_columns(treeview = self.treeview_input_files, 
                                             columns = self.treeview_input_files_columns,
                                             headers = self.treeview_input_files_headers,
                                             widths = self.treeview_input_files_column_widths,
                                             create_columns = True,
                                             trace = inf_trace
                                             )
        self.InputFilesTreeviewGridRow = 0
        self.InputFilesTreeviewGridColumn = 0
        self.InputFilesTreeviewColumnSpan = 1
        self.InputFilesTreeviewRowSpan = 1
        self.treeview_input_files.grid(row = self.InputFilesTreeviewGridRow,
                                    column = self.InputFilesTreeviewGridColumn,
                                    columnspan = self.InputFilesTreeviewColumnSpan,
                                    rowspan = self.InputFilesTreeviewRowSpan,
                                    **self.pr.c.grid_sticky_padding_small
                                    ) 
        
        
        """
        #############################################################################################################################################################################################################
        ###################################################################### ACTION BUTTONS #######################################################################################################################
        #############################################################################################################################################################################################################
        """
        
        """
        #################################
        ########## INPUT FILES ##########
        #################################
        """
        btnImportFiles = tk.Button(self.io_directory.frame,
                                    text = "Import Files", 
                                    background = self.pr.c.colour_interface_button, 
                                    command = self._btnImportFiles_Click
                                    )
        self.io_directory.add_widget(widget = btnImportFiles, 
                                     fixed_width = True, trace = inf_trace, 
                                     row = "input", column = "end")
        
        """
        #################################
        ###### EXECUTE BREAKPOINTS ######
        #################################
        """
        btnExecuteBreakpoints = tk.Button(self.io_directory.frame,
                                            text="Execute Breakpoints", 
                                            background = self.pr.c.colour_interface_button, 
                                            command = self._btnExecuteBreakpoints_Click
                                            )
        self.io_directory.add_widget(widget = btnExecuteBreakpoints, 
                                     fixed_width = True, trace = inf_trace, 
                                     row = "output", column = btnImportFiles)
        
        """
        #################################
        ######## DISPLAY WAVEFORM #######
        #################################
        """
        
        self.DisplayWaveformGridRow = self.InputFilesTreeviewGridRow + self.InputFilesTreeviewRowSpan
        self.DisplayWaveformGridColumn = self.InputFilesTreeviewGridColumn
        self.DisplayWaveformColumnSpan = self.InputFilesTreeviewColumnSpan
        self.DisplayWaveformRowSpan = 1
        self.btnDisplayWaveform = tk.Button(self.input_files_frame,
                                            text="Display Waveform", 
                                            background = self.pr.c.colour_interface_button, 
                                            command = self._btnDisplayWaveform_Click
                                            )
        self.btnDisplayWaveform.grid(row = self.DisplayWaveformGridRow,
                                     column = self.DisplayWaveformGridColumn,
                                     columnspan = self.DisplayWaveformColumnSpan,
                                     rowspan = self.DisplayWaveformRowSpan,
                                     sticky = "nesw",
                                     padx = self.pr.c.padding_small,
                                     pady = self.pr.c.padding_small_bottom_only
                                     ) 
        
        self.ImportBreakpointsGridRow = self.DisplayWaveformGridRow + self.DisplayWaveformRowSpan
        self.ImportBreakpointsGridColumn = self.InputFilesTreeviewGridColumn
        self.ImportBreakpointsColumnSpan = self.InputFilesTreeviewColumnSpan
        self.ImportBreakpointsRowSpan = 1
        self.btnImportBreakpoints = tk.Button(self.input_files_frame,
                                            text="Import Breakpoints", 
                                            background = self.pr.c.colour_interface_button, 
                                            command = self._btnImportBreakpoints_Click
                                            )
        self.btnImportBreakpoints.grid(row = self.ImportBreakpointsGridRow,
                                     column = self.ImportBreakpointsGridColumn,
                                     columnspan = self.ImportBreakpointsColumnSpan,
                                     rowspan = self.ImportBreakpointsRowSpan,
                                     sticky = "nesw",
                                     padx = self.pr.c.padding_small,
                                     pady = self.pr.c.padding_small_bottom_only
                                     ) 
        
        """
        ##########################################################################################
        ################################ NAMES INPUT #############################################
        ##########################################################################################
        """      
        
        self.treeview_info = {"columns" : ["#0", "Composer", "Album", "Track", "#", "Performer(s)", "Year", "Genre", "URL", "Final name", "Done"],
                              "headers" : ["", "Composer", "Album", "Track", "#", "Performer(s)", "Year", "Genre", "URL", "Final name", "Done"],
                              "column_widths" : {"#0": self.pr.c.width_text_tiny, 
                                                 "Composer": self.pr.c.width_text_short, 
                                                 "Album": self.pr.c.width_text_short, 
                                                 "Track": self.pr.c.width_text_short, 
                                                 "#": self.pr.c.width_text_tiny, 
                                                 "Performer(s)": self.pr.c.width_text_short, 
                                                 "Year": self.pr.c.width_text_tiny, 
                                                 "Genre": self.pr.c.width_text_veryshort, 
                                                 "URL": self.pr.c.width_text_short, 
                                                 "Final name": self.pr.c.width_text_long, 
                                                 "Done": self.pr.c.width_text_tiny
                                                 },
                              "fixed_width" : {"#0": True, 
                                                "Composer": False, 
                                                "Album": False, 
                                                "Track": False, 
                                                "#": True, 
                                                "Performer(s)": False, 
                                                "Year": True, 
                                                "Genre": False, 
                                                "URL": False, 
                                                "Final name": False, 
                                                "Done": True
                                                 },
                              "centering" : {"#0": "center", 
                                                "Composer": "w", 
                                                "Album": "w", 
                                                "Track": "w", 
                                                "#": "center", 
                                                "Performer(s)": "w", 
                                                "Year": "center", 
                                                "Genre": "w", 
                                                "URL": "w", 
                                                "Final name": "w", 
                                                "Done": "center"
                                                 },
                              "copy_from_above" : {"#0": True, 
                                                    "Composer": True, 
                                                    "Album": True, 
                                                    "Track": False, 
                                                    "#": False, 
                                                    "Performer(s)": True, 
                                                    "Year": True, 
                                                    "Genre": True, 
                                                    "URL": True, 
                                                    "Final name": False, 
                                                    "Done": False
                                                 },
                                "minimum_rows" : 1,
                                "requested_rows" : 10,
                                "row_height" : self.pr.c.width_text_tiny
                                }
        
        self.FileNamesTreeviewGridRow = 0
        self.FileNamesTreeviewGridColumn = 0
        self.FileNamesTreeviewColumnSpan = 1
        self.FileNamesTreeviewRowSpan = 1
        
        self.treeview_file_names = ttk.Treeview(self.names_frame, 
                                                height = self.treeview_info["requested_rows"])
        self.treeview_file_names['columns'] = self.treeview_info["columns"][1:]
        
        for i in range(len(self.treeview_info["columns"])):
            columnName = self.treeview_info["columns"][i]
            columnHeader = self.treeview_info["headers"][i]
            columnWidth = self.treeview_info["column_widths"][columnName]
            columnCentering = self.treeview_info["centering"][columnName]
            
            self.treeview_file_names.column(columnName, 
                                            width = columnWidth, 
                                            minwidth = columnWidth, 
                                            stretch = tk.NO, 
                                            anchor = columnCentering)
            self.treeview_file_names.heading(columnName, text = columnHeader)
            
        self.treeview_file_names.grid(row = self.FileNamesTreeviewGridRow, 
                                        column = self.FileNamesTreeviewGridColumn, 
                                        columnspan = self.FileNamesTreeviewColumnSpan,
                                        rowspan = self.FileNamesTreeviewRowSpan,
                                        **self.pr.c.grid_sticky_padding_small
                                        )
        """
        #############################################################################################################################################################################################################
        ########################################################################### BOUND FUNCTIONS #################################################################################################################
        #############################################################################################################################################################################################################
        """
        
        self.treeview_input_files.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<Configure>"}))
        self.treeview_file_names.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".treeview_file_names", "event": "<Configure>"}))
        self.tab.bind("<Configure>",lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".tab", "event": "<Configure>"}))
        
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
        
        """
        ##########################################################################################
        ################################ ALLOCATE SCALING ########################################
        ##########################################################################################
        """
        self.names_frame.columnconfigure(self.FileNamesTreeviewGridColumn,
                                         weight=1)
        self.visual_frame.columnconfigure(self.VisualFrameGridColumn, weight=1)
        
        self.tab.columnconfigure(0, weight=0)
        self.tab.columnconfigure(1, weight=1)
        
        self.load_from_config(trace = inf_trace)
        self.populate_input_files(trace = inf_trace)
    
    def _btnImportFiles_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnImportFiles_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnImportFiles_Click"}
        
        self.populate_input_files(trace = inf_trace)
    
    def populate_input_files(self, trace = None):
        self.pr.f._log_trace(self, "populate_treeview", trace)
        """
        Populate the treeview with file names
        """
        self.treeview_input_files.delete(*self.treeview_input_files.get_children())
        
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
    
    def _btnExecuteBreakpoints_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnExecuteBreakpoints_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnExecuteBreakpoints_Click"}
        
        true_breakpoints = self._true_breakpoints(scale_to_sound = True, 
                                                  trace = inf_trace)
        
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
                    
            except:
                exception = True
                """ All errors not handled elsewhere """
                pass
                
            if exception:
                if text is None: text = "An unknown error occurred"
                done_text = "✘ - " + text
            else:
                done_text = "✓"
            self.treeview_file_names.set(str(k+1), "Done", done_text)
        
        
        original_files_dir = os.path.join(self.io_directory.output_directory, 
                                          "Original files")
        if not os.path.exists(original_files_dir):
            os.makedirs(original_files_dir)
        self.pr.f.rename_file(old_directory = self.io_directory.input_directory, 
                              old_name = self.filename + self.pr.c.file_extension,  
                              new_directory = original_files_dir, 
                              new_name = self.filename + self.pr.c.file_extension, 
                              trace = inf_trace)
        self.treeview_input_files.delete(self.filename)
        
    def write_audio(self, audio, name, trace = None):
        self.pr.f._log_trace(self, "write_audio", trace)
        audio.export(os.path.join(self.io_directory.output_directory, name), 
                     format = "mp3")
    
    def _btnDisplayWaveform_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnDisplayWaveform_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnDisplayWaveform_Click"}
        
        
        if len(self.treeview_input_files.selection()) == 0: return
        self.filename = self.treeview_input_files.selection()[0]
        self.display_waveform(filepath = os.path.join(self.io_directory.input_directory, 
                                                      self.filename + 
                                                          self.pr.c.file_extension
                                                      ),
                              trace = inf_trace)
        
        self.audio_interface.end_audio_process(trace = inf_trace)
        self.audio_interface.load_audio(self.sound, trace = inf_trace)
    
    def _btnImportBreakpoints_Click(self, trace = None):
        """
        Open a text input for the user to input either a list of timecodes
        of the format XX:XX or XX:XX:XX separated by commas, or a block of
        text to parse for timecodes in that format.
        
        Add breakpoints to the audio track at the specified timecodes. If the
        input is a block of parsed text, attempt to also parse it for track
        names.
        """
        self.pr.f._log_trace(self, "_btnImportBreakpoints", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnImportBreakpoints"}
        if self.waveform is None: return
        timecodes = tk.simpledialog.askstring(title = "Import Breakpoints",
                                              prompt = "Enter a list of "
                                              "timecodes separated by commas,"
                                              " or text to parse for "
                                              "timecodes.",
                                              )
        #First try to parse as a list of timecodes 12:34 separated by commas
        #Failing that, parse directly using RegEx, matching XX:XX:XX or XX:XX
        #where X are numbers.
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
            
            #Assume that the space in between the timecodes is a list of tracks
            #split based on the timecode pattern
            track_list = re.split(tc_pattern, timecodes)
            track_list = [trk for trk in track_list if trk.strip() != ""]
            for trk in track_list:
                for regex in config.numerals_dict.regex_dict:
                    match = re.search(regex, trk, re.IGNORECASE)
                    if match:
                        #exclude matched string
                        trk_num = str(config.numerals_dict.regex_dict[regex])
                        trk_name = trk[:match.start()] + trk[match.end():]
                        trk_name = self.pr.f.clean_track_string(trk_name, 
                                                                trace = inf_trace)
                        track_dict[trk_num] = trk_name
            
            track_list = [self.pr.f.clean_track_string(trk, trace = inf_trace) 
                          for trk in track_list]
            track_list = [trk for trk in track_list if trk.strip() != ""]
            
            for i, trk in enumerate(track_list):
                if str(i+1) not in track_dict:
                    track_dict[str(i+1)] = trk
                        
        tc_list = [t*self.sound_subsample_length/self.sound_length
                   for t in tc_list]
        
        #loop through and add breakpoints at specified points
        for tc in set(tc_list):
            self._add_breakpoint_x(tc, inf_trace)
        
        #Loop through the track_dict and set track names accordingly
        if track_dict != {}:
            for i, trk in track_dict.items():
                if trk.strip() != "":
                    self.treeview_file_names.set(i, "Track", trk)
    
    def _true_breakpoints(self, scale_to_sound = False, trace = None):
        self.pr.f._log_trace(self, "_true_breakpoints", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._true_breakpoints"}
        """
        Get a sorted list of all breakpoints on the waveform, including the 
        start and end. Optionally scale the breakpoints up to the original 
        sound.
        """
        #Since we are making changes directly to the list, we must create a
        #true (deep) copy of it, rather than simple a new variable pointing at
        #it. Otherwise, the changes will accumulate even though true_breakpoints
        #only has private scope.
        true_breakpoints = copy.deepcopy(self.breakpoints_x)
        #add the start and end of the audio
        true_breakpoints.append(self.start_breakpoint_x)
        true_breakpoints.append(self.end_breakpoint_x)
        
        #multiply back up to the full sound length
        if scale_to_sound:
            true_breakpoints = self.pr.f.multiply_list(true_breakpoints, 
                                                       self.sound_length/self.sound_subsample_length, 
                                                       trace = inf_trace)
            
        true_breakpoints.sort()
        return true_breakpoints
    
    def _initialise_canvas(self, trace = None):
        self.pr.f._log_trace(self, "_initialise_canvas", trace)
        """
        Initialise the canvas used to draw the audio waveform
        """
        self.visual_figure = Figure(figsize=(10, 6), dpi=100)
        self.figure = self.visual_figure.add_subplot(111)
        self.figure.axes.get_yaxis().set_visible(False)
        self.figure.axis("off")
        self.figure.set(facecolor = self._colour_waveform)
        
        self.canvas = FigureCanvasTkAgg(self.visual_figure, master = self.visual_frame)  # A tk.DrawingArea.
        self.canvas.draw()
        key_trace = {"source": "bound event", "widget": self.name + ".canvas", "event": "<event.key>"}
        self.canvas.mpl_connect("key_press_event", lambda event: 
                                self._on_key_press(event, trace = key_trace))
        self.canvas.mpl_connect("button_press_event", lambda event: 
                                self._on_button_press(event, trace = key_trace))
        self.canvas.mpl_connect("key_release_event", lambda event: 
                                self._on_key_release(event, trace = key_trace))
        
        #must use .pack() here to avoid conflict with matplotlib backend
        self.tk_canvas = self.canvas.get_tk_widget()
        self.tk_canvas.pack(side=tk.TOP, fill = "x", expand = 0)
        
        #add toolbar below plot
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.visual_frame)
        self.toolbar.config(background = self.pr.c.colour_background)
        self.toolbar._message_label.config(background = self.pr.c.colour_background)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill = "x", expand = 0)
    
    def display_waveform(self, filepath, trace = None):
        self.pr.f._log_trace(self, "display_waveform", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".display_waveform"}
        """
        Displays the waveform of the specified file in a matplotlib window with
        navigation toolbar. subsampling_rate controls the resolution of the plot;
        higher is more expensive.
        """
        self.sound = AudioSegment.from_mp3(filepath)
        self.sound_length = len(self.sound)
        
        #plotting the entire waveform is very intensive for long tracks
        #we take every nth sample, which preserves the waveform all the way
        #up to ~n = 10,000
        self.sound_subsample = self.sound.get_array_of_samples()[0::self.subsampling_rate]
        self.sound_subsample_length = len(self.sound_subsample)
        
        #remove current waveform figure
        self.clear_waveform(trace = inf_trace)
        
        plot_config = {"color": self._colour_waveform}
        self.waveform, = self.figure.plot(self.sound_subsample, **plot_config)
        self.start_breakpoint_x = 0
        self.end_breakpoint_x = self.sound_subsample_length - 1
        self._draw_outside_breakpoints(trace = inf_trace)
        
        self.figure_ylim = self.figure.get_ylim()
        self.figure_xlim = self.figure.get_xlim()
        
        self._remove_figure_numbers(trace = inf_trace)
        self._add_figure_numbers(trace = inf_trace)
        self._scale_plot(trace = inf_trace)
        
        self.canvas.draw()
        self.toolbar.update() #update toolbar, including home view
        
        self.treeview_file_names.delete(*self.treeview_file_names.get_children())
        self.fresh_waveform = True
        self.update_treeview_numbers(trace = inf_trace)
    
    def clear_waveform(self, trace = None): #TODO
        self.pr.f._log_trace(self, "clear_waveform", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".clear_waveform"}
        """
        Remove the waveform and all breakpoints from the canvas
        """
        self.toolbar.home()
        if not self.waveform is None: 
            self.waveform.remove()
            self.waveform = None
        if not self.start_breakpoint is None: 
            self.start_breakpoint.remove()
            self.start_breakpoint = None
        if not self.end_breakpoint is None: 
            self.end_breakpoint.remove()
            self.end_breakpoint = None
            
        self.remove_playback_progress_bar(trace = inf_trace)
        self.reset_breakpoints(trace = inf_trace)
        # removing the waveform takes the focus away from the canvas widget
        # without focus, it cannot detect the key press events
        self.canvas.get_tk_widget().focus_force()
    
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
    
    def _draw_outside_breakpoints(self, trace = None):
        self.pr.f._log_trace(self, "_draw_outside_breakpoints", trace)
        """
        Draw the black starting and ending lines.
        """
        
        if self.waveform is None: return
        if not self.start_breakpoint is None: 
            self.start_breakpoint.remove()
            self.start_breakpoint = None
        if not self.end_breakpoint is None: 
            self.end_breakpoint.remove()
            self.end_breakpoint = None
        
        self.start_breakpoint = self.figure.axvline(x = self.start_breakpoint_x, 
                                                    color = "black")
        self.end_breakpoint = self.figure.axvline(x = self.end_breakpoint_x, 
                                                  color = "black")
        self.canvas.draw()
    
    def _change_outside_breakpoint(self, event, trace = None):
        self.pr.f._log_trace(self, "_change_outside_breakpoint", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + 
                             "._change_outside_breakpoint"
                    }
        
        if self.waveform is None: return
        if event.xdata <= (self.start_breakpoint_x + self.end_breakpoint_x)/2:
            self.start_breakpoint_x = event.xdata
        else:
            self.end_breakpoint_x = event.xdata
        
        for bp in self.breakpoints:
            if not self.start_breakpoint_x <= bp._x[0] <= self.end_breakpoint_x:
                bp.remove()
                i = self.breakpoints.index(bp)
                self.breakpoints.pop(i)
                self.breakpoints_x.pop(i)
        
        self._draw_outside_breakpoints(trace = inf_trace)
        self._remove_figure_numbers(trace = inf_trace)
        self._add_figure_numbers(trace = inf_trace)
        self.canvas.draw()
            
    def _add_breakpoint(self, event, trace = None):
        self.pr.f._log_trace(self, "_add_breakpoint", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._add_breakpoint"}
        """
        Handle the event to add a new breakpoint to the waveform
        """
        self._add_breakpoint_x(event.xdata, trace = inf_trace)
        
    def _add_breakpoint_x(self, x, trace = None):
        self.pr.f._log_trace(self, "_add_breakpoint_x", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._add_breakpoint_x"}
        """
        Adds a vertical line to the waveform, denoting a point where the
        audio will be split. Take the x coordinate from the x input.
        """
        if self.figure is None: return
        
        #exit if coordinate is outside the x bounds of the waveform
        if (x is None or x < self.start_breakpoint_x 
            or x > self.end_breakpoint_x): 
            return
        
        #add a breakpoint line at the cursor's x position
        breakline = self.figure.axvline(x = x, color = self._colour_breakpoint)
        self.breakpoints.append(breakline)
        self.breakpoints_x.append(x)
        
        self._remove_figure_numbers(trace = inf_trace)
        self._add_figure_numbers(trace = inf_trace)
        
        self.canvas.draw()
        self.fresh_waveform = False
        self.update_treeview_numbers(trace = inf_trace)
        
    def _add_figure_numbers(self, trace = None):
        self.pr.f._log_trace(self, "_add_figure_numbers", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._add_figure_numbers"}
        """
        Add numbers halfway between each breakpoint denoting the track number
        of that audio segment when exporting
        """
        true_breakpoints = self._true_breakpoints(scale_to_sound = False, 
                                                  trace = inf_trace)
        txt_kwargs = {"fontfamily": "Palatino Linotype", 
                      "fontsize": 10, "color": "black"}
        
        for k in range(len(true_breakpoints)-1):
            #add halfway between breakpoints
            x = (true_breakpoints[k+1] + true_breakpoints[k])/2
            y = self.figure_ylim[0]*0.97 #add to bottom of plot
            text = str(k+1)
            fig_num = self.figure.text(x=x, y=y, s=text, **txt_kwargs)
            self.figure_numbers.append(fig_num)
        self.canvas.draw()
    
    def _scale_plot(self, trace = None):
        """
        Set the limits of the canvas and figure to fit the waveform
        """
        self.pr.f._log_trace(self, "_scale_plot", trace)
        self.figure.set_autoscalex_on(True)
        
        self.figure.set_ylim(ymin=self.figure_ylim[0], 
                             ymax=self.figure_ylim[1])
        self.figure.set_xlim(xmin=0, xmax=self.sound_subsample_length)
        
    def _remove_figure_numbers(self, trace = None):
        self.pr.f._log_trace(self, "_remove_figure_numbers", trace)
        """
        Remove all figure numbers
        """
        if self.figure_numbers == []: return
        for fig_num in self.figure_numbers:
            fig_num.remove()
            self.figure_numbers = []
        self.canvas.draw()
    
    def remove_breakpoint(self, brkpt, refresh_treeview = True, trace = None):
        self.pr.f._log_trace(self, "remove_breakpoint", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".remove_breakpoint"}
        """
        Removes the given breakpoint.
        """
        if brkpt is None: return
        
        brkpt.remove()
        index = self.breakpoints.index(brkpt)
        self.breakpoints.pop(index)
        self.breakpoints_x.pop(index)
        
        self._remove_figure_numbers(trace = inf_trace)
        self._add_figure_numbers(trace = inf_trace)
        self.canvas.draw()
        
        if refresh_treeview:
            self.update_treeview_numbers(trace = inf_trace)
    
    def _undo_breakpoint(self, event, trace = None):
        self.pr.f._log_trace(self, "_undo_breakpoint", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._undo_breakpoint"}
        """
        Undoes the most recent breakpoint action.
        """
        if self.breakpoints == []:
            return
        
        self.remove_breakpoint(self.breakpoints[-1], trace = inf_trace)
            
    def reset_breakpoints(self, trace = None):
        self.pr.f._log_trace(self, "_undo_breakpoint", trace)
        """
        Remove all breakpoints
        """
        for brkpt in self.breakpoints: 
            brkpt.remove()
        self.breakpoints = []
        self.breakpoints_x = []
        
    def _resize_treeview(self, event = None, trace = None):
        if not self.pr.running: return
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._resize_treeview"}
        
        seconds_elapsed = (datetime.now() - 
                           self._configure_last_called).total_seconds()
        if seconds_elapsed >= self.pr.c.max_refresh_frequency_seconds:
            self.pr.f._log_trace(self, "_resize_treeview", trace, 
                                 add = " _configure_last_called was %f" % 
                                         seconds_elapsed)
            
            if self._configure_last_called == datetime.min:
                self._configure_last_called = datetime.now()
                
            #update widget info
            self.treeview_input_files.update()
            self.treeview_file_names.update()
            self.root.update()
            
            #update the treeview height (number of rows visible)
            #match this to the height of the waveform
            available_height = self.visual_frame.winfo_height()
            self.treeview_input_files["height"] = int(available_height/self.pr.c.treeview_item_height) - 5
            
            #get new width of widget
            treeview_width = self.treeview_file_names.winfo_width()
            
            #get array of the new width for each column, distributed according to their previous widths and any fixed width columns
            new_widths = self.pr.f.distribute_width(treeview_width, 
                                                    list(self.treeview_info["column_widths"].values()), 
                                                    list(self.treeview_info["fixed_width"].values()), 
                                                    trace = inf_trace)
            
            #update the width for each column
            for i in range(len(self.treeview_info["columns"])):
                self.treeview_file_names.column(self.treeview_info["columns"][i], 
                                                width = new_widths[i], 
                                                minwidth = new_widths[i], 
                                                stretch = tk.NO)
            
            #update the time the event was last called
            self._configure_last_called = datetime.now()
        return event
    
    def load_from_config(self, trace = None):
        self.pr.f._log_trace(self, "load_from_config", trace)
        self.subsampling_rate = 1000
    
    def _treeview_mouse1_click(self, event, trace = None):
        self.pr.f._log_trace(self, "_treeview_mouse1_click", trace)
        inf_trace = {"source": "function call", "parent": self.name + "._treeview_mouse1_click"}
        
        treeview_list = [self.treeview_file_names, self.treeview_input_files]
        x,y = self.root.winfo_pointerxy()
        
        for widget in treeview_list:
            if self.pr.f.point_is_inside_widget(x, y, widget, 
                                                trace = inf_trace):
                self._treeview_mouse1_click_column = widget.identify_column(event.x)
                self._treeview_mouse1_click_row = widget.identify_row(event.y)
                self._treeview_mouse1_click_cell = (self._treeview_mouse1_click_row 
                                                    if self._treeview_mouse1_click_column == "#0" 
                                                    else widget.set(self._treeview_mouse1_click_row, 
                                                                    self._treeview_mouse1_click_column)
                                                    )
                return event
        return event
        
    def edit_value_via_interface(self, event, trace = None):
        self.pr.f._log_trace(self, "edit_value_via_interface", trace)
        inf_trace = {"source": "function call", "parent": self.name + ".edit_value_via_interface"}
        """
        Open a window with the selected filename where a value can be specified for the selected cell
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
        
        ValueFromFilename(parent = self, 
                          filename = self.filename,
                          columnString = self.treeview_column_id_to_name(clicked_column_id),
                          columnId = clicked_column_id,
                          treeview = self.treeview_file_names,
                          row_iid = clicked_row,
                          trace = inf_trace
                          )
        return event

    def update_treeview_numbers(self, trace = None):
        self.pr.f._log_trace(self, "update_treeview_numbers", trace)
        inf_trace = {"source": "function call", "parent": self.name + ".update_treeview_numbers"}
        
        treeview_count = len(self.treeview_file_names.get_children())
        breakpoint_count = len(self._true_breakpoints(scale_to_sound = False, trace = inf_trace)) - 1
        
        while treeview_count < breakpoint_count:
            _id = treeview_count + 1
            
            if self.fresh_waveform == True:
                values = [self.pr.f.suggest_value(self.filename, field, 
                                                  trace = inf_trace) 
                          for field in self.treeview_info["columns"][1:]]
                values[self.treeview_info["headers"].index("#")-1] = 1
            else:
                values = list(self.treeview_file_names.item(self.treeview_file_names.get_children()[-1], "values"))
                values[self.treeview_info["headers"].index("#")-1] = int(values[self.treeview_info["headers"].index("#")-1]) + 1
                
            self.treeview_file_names.insert("", index="end", text = str(_id), iid = str(_id), values = values)
            self.treeview_file_names.set(str(_id), "Track", "")
            self.set_final_name(str(_id), trace = inf_trace)
            treeview_count = len(self.treeview_file_names.get_children())
            
        while treeview_count > breakpoint_count:
            self.treeview_file_names.delete(self.treeview_file_names.get_children()[-1])
            treeview_count = len(self.treeview_file_names.get_children())
            
    def treeview_column_id_to_name(self, column_id, trace = None):
        self.pr.f._log_trace(self, "treeview_column_id_to_name", trace)
        
        headers = self.treeview_info["headers"]
        return headers[int(column_id[1:])]
        
    def copy_from_above(self, event, trace = None):
        self.pr.f._log_trace(self, "copy_from_above", trace)
        """
        Copies a value down to all selected rows in certain column
        """
        selected_items = self.treeview_file_names.selection()
        selection_iter = range(len(selected_items))
        clicked_column_id = self._treeview_mouse1_click_column
        if clicked_column_id == "#0":
            #cancel if the filename ID column was the last column clicked
            return event
            
        #get the value to copy down. If one row is selected, this is the value in
        #the row above. If multiple values are selected, this is the value in the
        #first selected row
        if self.treeview_column_id_to_name(clicked_column_id) == "#":
            #number column case
            if len(selected_items) == 1:
                #increment from row above
                value_to_copy = int(self.treeview_file_names.set(self.treeview_file_names.prev(selected_items[0]), 
                                                                 clicked_column_id)) + 1
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
                value_to_copy = self.treeview_file_names.set(self.treeview_file_names.prev(selected_items[0]), 
                                                             clicked_column_id)
            else:
                value_to_copy = self.treeview_file_names.set(selected_items[0], 
                                                             clicked_column_id)
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
        
        parts = [filename] + list(self.treeview_file_names.item(filename, 'values'))
        
        self.treeview_file_names.set(filename, 
                                     'Final name', 
                                     self.pr.f.filename_from_parts(
                                         parts = parts,
                                         headers = self.treeview_info["headers"], 
                                         trace = inf_trace
                                         )
                                     )
    
    def match_keywords(self, filename, overwrite = False, trace = None):
        self.pr.f._log_trace(self, "match_keywords", trace)
        
        values_dict = {}
        for field in ["Composer", "Album", "#", "Genre", "Year", "Track"]:
            values_dict[field] = self.treeview_file_names.set(filename, field)
            
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
                    self.treeview_file_names.set(filename, field, 
                                                 compare_dict['value'][field])
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
        
        values = self.pr.f.get_values_dict(self.treeview_file_names, filename, 
                                           self.treeview_info["headers"])
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
        
    def draw_playback_progress_bar(self, start, trace = None):
        self.pr.f._log_trace(self, "draw_playback_progress_bar", trace)
        
        x = start*self.sound_subsample_length/self.sound_length
        
        if self.playback_bar is None:
            self.playback_bar = self.figure.axvline(x=x, color = "red")
        else:
            self.playback_bar.set_xdata([x, x])
            
        self.canvas.draw()
        
    def remove_playback_progress_bar(self, trace = None):
        self.pr.f._log_trace(self, "remove_playback_progress_bar", trace)
        if not self.playback_bar is None:
            self.playback_bar.remove()
            self.playback_bar = None
            
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
            min_pixels = 20 * sensitivity
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
        if brkpt is None: return
        self.remove_breakpoint(brkpt, refresh_treeview = False, 
                               trace = inf_trace)
        self._add_breakpoint_x(x, trace = inf_trace)
        
    def _reset_action_stack(self, trace = None):
        self.pr.f._log_trace(self, "_reset_action_stack", trace)
        
        self._action_stack = []
        self._stack_location = -1
        
    def _undo_action(self, trace = None):
        self.pr.f._log_trace(self, "_undo_action", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._undo_action"}
        
        self._reverse_action(self._action_stack[self._stack_location],
                             trace = inf_trace)
        
    def _reverse_action(self, action, trace = None):
        self.pr.f._log_trace(self, "_reverse_action", trace)
    
    def _redo_action(self, trace = None):
        self.pr.f._log_trace(self, "_redo_action", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._redo_action"}
        
        self._do_action(self._action_stack[self._stack_location + 1],
                             trace = inf_trace)
    
    def _do_action(self, action, trace = None):
        self.pr.f._log_trace(self, "_do_action", trace)
        
    def _add_action(self, action, brkpt, trace = None, **kwargs):
        self.pr.f._log_trace(self, "_add_action", trace)
        
        self._action_stack = self._action_stack[:self._stack_location]
        self._action_stack.append({"action": action,
                                   "breakpoint": brkpt,
                                   **kwargs})
        