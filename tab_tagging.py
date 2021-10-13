# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 19:45:18 2021

@author: marcu
"""

import tkinter as tk
from tkinter import ttk
import os
import eyed3
import config
from datetime import datetime
from io_directory import IODirectory


class Tagging :
    def __init__(self, parent, grid_references, trace = None):
        self.class_name = "Tagging"
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab_tagging
        
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".__init__"}
        """
        ###################################
        ############# FRAMES ##############
        ###################################
        """
        self.io_directory = IODirectory(parent = self, trace = inf_trace, call_after_input = self.populate_file_list)
        TreeviewFrame = tk.Frame(self.tab, background = self.pr.c.colour_background)
        
        IODirectoryGridRow = grid_references[0]
        IODirectoryGridColumn = grid_references[1]
        IODirectoryColumnSpan = self.pr.c.columnspan_all
        IODirectoryRowSpan = 1
        
        TreeviewFrameGridRow = IODirectoryGridRow + 1
        TreeviewFrameGridColumn = IODirectoryGridColumn
        TreeviewFrameColumnSpan = self.pr.c.columnspan_all
        TreeviewFrameRowSpan = 1
        
        self.io_directory.grid(row = IODirectoryGridRow, 
                                column = IODirectoryGridColumn, 
                                columnspan = IODirectoryColumnSpan,
                                rowspan = IODirectoryRowSpan,
                                sticky = "nesw"
                                )
        
        TreeviewFrame.grid(row = TreeviewFrameGridRow, 
                            column = TreeviewFrameGridColumn, 
                            columnspan = TreeviewFrameColumnSpan,
                            rowspan = TreeviewFrameRowSpan,
                            sticky = "nesw"
                            )
        
        
        """
        ################################################
        ############# INPUT FOLDER FILES LIST ##########
        ################################################
        """
        
        InputFilesGridRow = 0
        InputFilesGridColumn = 0
        InputFilesColumnSpan = 2
        InputFilesRowSpan = 12
        
        self.treeview_input_files_columns = ["#0"]
        self.treeview_input_files_headers = ["Filename"]
        self.treeview_input_files_column_widths = [self.pr.c.width_text_long]
        self.treeview_input_files_fixed_width = [False]
        
        self.treeview_input_files = ttk.Treeview(TreeviewFrame)
        
        self.pr.f.configure_treeview_columns(treeview = self.treeview_input_files, 
                                         columns = self.treeview_input_files_columns,
                                         headers = self.treeview_input_files_headers,
                                         widths = self.treeview_input_files_column_widths,
                                         create_columns = True,
                                         trace = inf_trace
                                         )
        
        self.treeview_input_files.grid(row = InputFilesGridRow,
                                    column = InputFilesGridColumn,
                                    columnspan = InputFilesColumnSpan,
                                    rowspan = InputFilesRowSpan,
                                    pady = self.pr.c.padding_large_top_only,
                                    sticky = "nesw",
                                    padx = self.pr.c.padding_small
                                    )      

        """
        #############################################################################################################################################################################################################
        ###################################################################### CURRENT TAGS LIST ####################################################################################################################
        #############################################################################################################################################################################################################
        """
        CurrentTagsGridRow = InputFilesGridRow
        CurrentTagsGridColumn = InputFilesGridColumn + InputFilesColumnSpan + 1
        CurrentTagsColumnSpan = 1
        CurrentTagsRowSpan = InputFilesRowSpan - 1
 
        self.treeview_current_tags_columns = ["#0", "Value"]
        self.treeview_current_tags_headers = ["Tag", "Value"]
        self.treeview_current_tags_column_widths = [self.pr.c.width_text_short, self.pr.c.width_text_medium]
        self.treeview_current_tags_fixed_width = [True, False]
        
        #Create the treeview with the relevant columns
        self.treeview_current_tags = ttk.Treeview(TreeviewFrame)
        self.pr.f.configure_treeview_columns(treeview = self.treeview_current_tags, 
                                             columns = self.treeview_current_tags_columns,
                                             headers = self.treeview_current_tags_headers,
                                             widths = self.treeview_current_tags_column_widths,
                                             create_columns = True,
                                             trace = inf_trace
                                             )
        self.treeview_current_tags.grid(row = CurrentTagsGridRow, 
                                   column = CurrentTagsGridColumn, 
                                   columnspan = CurrentTagsColumnSpan,
                                   rowspan = InputFilesRowSpan,
                                   sticky = "nesw", 
                                   pady = self.pr.c.padding_large_top_only,
                                   padx = self.pr.c.padding_small
                                   )
        """
        #############################################################################################################################################################################################################
        ###################################################################### SUGGESTED TAGS LIST ##################################################################################################################
        #############################################################################################################################################################################################################
        """
        SuggestedTagsGridRow = CurrentTagsGridRow
        SuggestedTagsGridColumn = CurrentTagsGridColumn + CurrentTagsColumnSpan + 1
        SuggestedTagsColumnSpan = 1
        SuggestedTagsRowSpan = InputFilesRowSpan
 
        self.treeview_suggested_tags_columns = ["#0", "Value"]
        self.treeview_suggested_tags_headers = ["Tag", "Value"]
        self.treeview_suggested_tags_column_widths = [self.pr.c.width_text_short, self.pr.c.width_text_medium]
        self.treeview_suggested_tags_fixed_width = [True, False]
        
        self.treeview_suggested_tags = ttk.Treeview(TreeviewFrame)
        self.pr.f.configure_treeview_columns(treeview = self.treeview_suggested_tags, 
                                             columns = self.treeview_suggested_tags_columns,
                                             headers = self.treeview_suggested_tags_headers,
                                             widths = self.treeview_suggested_tags_column_widths,
                                             create_columns = True,
                                             trace = inf_trace
                                             )
        
        self.treeview_suggested_tags.grid(row = SuggestedTagsGridRow, 
                                           column = SuggestedTagsGridColumn, 
                                           columnspan = SuggestedTagsColumnSpan,
                                           rowspan = SuggestedTagsRowSpan,
                                           sticky = "nesw", 
                                           pady = self.pr.c.padding_large_top_only,
                                           padx = self.pr.c.padding_small
                                           )
        """
        #############################################################################################################################################################################################################
        ###################################################################### ACTION BUTTONS #######################################################################################################################
        #############################################################################################################################################################################################################
        """ 
        """
        #################################
        ########## SAVE CHANGES #########
        #################################
        """
        btnSaveChangesGridRow = CurrentTagsGridRow + CurrentTagsRowSpan + 1
        btnSaveChangesGridColumn = CurrentTagsGridColumn
        btnSaveChangesColumnSpan = CurrentTagsColumnSpan
        btnSaveChangesRowSpan = 1
               
        def btnSaveChanges_Click():
            print("SAavechanges")
        
        btnSaveChanges = tk.Button(TreeviewFrame,
                                    text="Save changes",
                                    command = btnSaveChanges_Click,
                                    **self.pr.c.button_light_standard_args
                                    )
        btnSaveChanges.grid(row = btnSaveChangesGridRow, 
                            column = btnSaveChangesGridColumn,
                            columnspan = btnSaveChangesColumnSpan,
                            rowspan = btnSaveChangesRowSpan,
                            sticky = "nesw",
                            padx = self.pr.c.padding_small,
                            pady = self.pr.c.padding_small_bottom_only
                            )
        """
        #################################
        ########## IMPORT FILES #########
        #################################
        """
        btnImportFilesGridRow = InputFilesGridRow + InputFilesRowSpan
        btnImportFilesGridColumn = InputFilesGridColumn
        btnImportFilesColumnSpan = InputFilesColumnSpan
        btnImportFilesRowSpan = 1
        
        btnImportFiles = tk.Button(TreeviewFrame, text="Import Files", 
                                   command = self.populate_file_list,
                                   **self.pr.c.button_light_standard_args
                                   )
        btnImportFiles.grid(row = btnImportFilesGridRow, 
                            column = btnImportFilesGridColumn,
                            columnspan = btnImportFilesColumnSpan,
                            rowspan = btnImportFilesRowSpan,
                            sticky = "nesw",
                            padx = self.pr.c.padding_small,
                            pady = self.pr.c.padding_small_bottom_only
                            )
        """
        ###########################################
        ###### INTER-COLUMN ACTION BUTTONS ########
        ###########################################
        """
        InterColumnButtonsRowOffset = 0
        """
        #################################
        ######## PREVIOUS FILE ##########
        #################################
        """
        btnPreviousFileNameGridRow = int(CurrentTagsGridRow + InputFilesRowSpan/2 - 1) + InterColumnButtonsRowOffset
        btnPreviousFileNameGridColumn = InputFilesGridColumn + InputFilesColumnSpan
        btnPreviousFileColumnSpan = 1
        btnPreviousFileNameRowSpan = 2
        
        def btnPreviousFileName_Click():
            print("prevfile")
        
        btnPreviousFileName = tk.Button(TreeviewFrame,
                                        text="▲", 
                                        width = self.pr.c.width_button_small,
                                        command = btnPreviousFileName_Click,
                                        **self.pr.c.button_standard_args
                                        )
        btnPreviousFileName.grid(row = btnPreviousFileNameGridRow, 
                                column = btnPreviousFileNameGridColumn,
                                columnspan = btnPreviousFileColumnSpan,
                                rowspan = btnPreviousFileNameRowSpan,
                                sticky = "nesw",
                                padx = self.pr.c.padding_small
                                )
        """
        #################################
        ########## NEXT FILE ############
        #################################
        """
        btnNextFileNameGridRow = btnPreviousFileNameGridRow + btnPreviousFileNameRowSpan
        btnNextFileNameGridColumn = btnPreviousFileNameGridColumn
        btnNextFileNameColumnSpan = btnPreviousFileColumnSpan
        btnNextFileNameRowSpan = btnPreviousFileNameRowSpan
        
        def btnNextFileName_Click():
            print("nextfile")
        
        btnNextFileName = tk.Button(TreeviewFrame,
                                    text="▼",
                                    width = self.pr.c.width_button_small,
                                    command = btnNextFileName_Click,
                                    **self.pr.c.button_standard_args
                                    )
        btnNextFileName.grid(row = btnNextFileNameGridRow, 
                            column = btnNextFileNameGridColumn,
                            columnspan = btnNextFileNameColumnSpan,
                            rowspan = btnNextFileNameRowSpan,
                            sticky = "nesw",
                            padx = self.pr.c.padding_small
                            )
        """
        ####################################
        ####### COPY SUGGESTED TAGS ########
        ####################################
        """
        btnCopySuggestedTagsGridRow = int(CurrentTagsGridRow + InputFilesRowSpan/2) + InterColumnButtonsRowOffset
        btnCopySuggestedTagsGridColumn = CurrentTagsGridColumn + CurrentTagsColumnSpan
        btnCopySuggestedTagsColumnSpan = 1
        btnCopySuggestedTagsRowSpan = 2
        
        def btnCopySuggestedTags_Click():
            print("CopySuggestedTags")
        
        btnCopySuggestedTags = tk.Button(TreeviewFrame,
                                            text="«",
                                            width = self.pr.c.width_button_small,
                                            command = btnCopySuggestedTags_Click,
                                            **self.pr.c.button_standard_args
                                            )
        btnCopySuggestedTags.grid(row = btnCopySuggestedTagsGridRow, 
                                    column = btnCopySuggestedTagsGridColumn,
                                    columnspan = btnCopySuggestedTagsColumnSpan,
                                    rowspan = btnCopySuggestedTagsRowSpan,
                                    sticky = "nesw",
                                    padx = self.pr.c.padding_small
                                    )
        """
        #############################################################################################################################################################################################################
        ########################################################################### BOUND FUNCTIONS #################################################################################################################
        #############################################################################################################################################################################################################
        """

        self.treeview_input_files.bind("<ButtonRelease-1>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.class_name + ".treeview_input_files", "event": "<ButtonRelease-1>"})) #Also <ButtonPress-1>, <Double-1> for double click, etc. - bind the selection change event, updating the tag values 
        self.treeview_input_files.bind("<KeyRelease-Up>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.class_name + ".treeview_input_files", "event": "<KeyRelease-Up>"})) #refresh tags when moving up and down the file list with the arrow keys
        self.treeview_input_files.bind("<KeyRelease-Down>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.class_name + ".treeview_input_files", "event": "<KeyRelease-Down>"}))
        
        self.treeview_input_files.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.class_name + ".treeview_input_files", "event": "<Configure>"}))
        self.treeview_current_tags.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.class_name + ".treeview_current_tags", "event": "<Configure>"}))
        self.treeview_suggested_tags.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.class_name + ".treeview_suggested_tags", "event": "<Configure>"}))
        self.tab.bind("<Configure>",lambda event:  self._resize_treeview(event, trace={"source": "bound event", "widget": self.class_name + ".tab_tagging", "event": "<Configure>"}))
        
        """
        ##########################################################################################
        ################################ ALLOCATE SCALING ########################################
        ##########################################################################################
        """  
        self.tab.columnconfigure(0, weight=1)
        
        TreeviewFrame.columnconfigure(InputFilesGridColumn, weight=1)        
        TreeviewFrame.columnconfigure(CurrentTagsGridColumn, weight=1)      
        TreeviewFrame.columnconfigure(SuggestedTagsGridColumn, weight=1)      
        """
        ##########################################################################################
        ################################ INITIALISE WIDGETS ######################################
        ##########################################################################################
        """   
        
        self.populate_file_list(trace = inf_trace)
        self._configure_last_called = datetime.min
        self._resize_treeview(event = None, trace = inf_trace)
        return
    
    
    def populate_file_list(self, event = None, trace = None):
        self.pr.f._log_trace(self, "populate_file_list", trace)
        inf_trace = {"source": "function call", "parent": self.class_name + ".populate_file_list"}
        
        """
        Clears all treeviews and re-populates the list of filenames
        """
        
        if os.path.isdir(self.io_directory.input_directory):
            #clear all treeviews
            self.treeview_input_files.delete(*self.treeview_input_files.get_children())
            self.treeview_current_tags.delete(*self.treeview_current_tags.get_children())
            self.treeview_suggested_tags.delete(*self.treeview_suggested_tags.get_children())
               
            #add all files in the specified directory with the correct extension
            for file in os.listdir(self.io_directory.input_directory):
                filename, extension = os.path.splitext(file)
                if extension == self.pr.c.file_extension:  
                    self.treeview_input_files.insert("", index="end", text = filename, iid = filename)
        return event
    
    def populate_current_tags_box(self, event, trace = None):
        self.pr.f._log_trace(self, "populate_current_tags_box", trace)
        inf_trace = {"source": "function call", "parent": self.class_name + ".populate_current_tags_box"}
        """
        Updates the current and suggested tags Treeviews for the selected file
        """
        #Remove the current contents of each treeview
        self.treeview_suggested_tags.delete(*self.treeview_suggested_tags.get_children())
        self.treeview_current_tags.delete(*self.treeview_current_tags.get_children())
        
        #Get the selected file in the inputs files treeview
        if len(self.treeview_input_files.selection()) == 0: #exit if nothing is selected
            return
        
        filename = self.treeview_input_files.selection()[0]
        
        #List of tags to look at
        tag_list_alias = self.pr.c.tag_list_alias
        
        #Add suggested values to the relevant treeview
        tag_list_value = self.pr.f.SuggestTagsFromFinalFilename(filename, trace = inf_trace)
        tag_list_value = ["" if t is None else t for t in tag_list_value]
        for i in range(len(tag_list_alias)):
            self.treeview_suggested_tags.insert("", index=i, text=tag_list_alias[i], values=(tag_list_value[i], ""), iid = tag_list_alias[i])
            
        #Add current values to the relevant treeview
        tag_list_value = self.get_file_tags(directory = self.txtInputDirectory.get(), 
                                             filename = filename, 
                                             extension = self.pr.c.file_extension, 
                                             trace = inf_trace
                                             )
        for i in range(len(tag_list_alias)):
            self.treeview_current_tags.insert("", index=i, text=tag_list_alias[i], values=(tag_list_value[i], ""), iid = tag_list_alias[i])
        
        return event
   
    def get_file_tags(self, directory, filename, extension, trace = None):
        self.pr.f._log_trace(self, "get_file_tags", trace)
        inf_trace = {"source": "function call", "parent": self.class_name + ".get_file_tags"}
        """
        Returns the currently set ID3v2 tags of the specified file
        """
        audiofile = eyed3.load(os.path.join(directory, filename + extension))
        
        tag_list_value = [audiofile.tag.album_artist,
                          audiofile.tag.album,
                          audiofile.tag.track_num[0],
                          audiofile.tag.title,
                          audiofile.tag.artist,
                          audiofile.tag.recording_date.year if not audiofile.tag.recording_date is None else "",
                          audiofile.tag.genre,
                          audiofile.tag.artist_url]
        
        tag_list_value = ["" if tag_value is None else tag_value for tag_value in tag_list_value] #replace None with empty string
                
        return tag_list_value


    def _resize_treeview(self, event = None, trace = None):
        if not self.pr.running: return
        inf_trace = {"source": "function call", "parent": self.class_name + "._resize_treeview"}
        """
        Resize the treeview columns according to the current widget size
        """
        seconds_elapsed = (datetime.now() - self._configure_last_called).total_seconds()
        if seconds_elapsed >= self.pr.c.max_refresh_frequency_seconds:
            self.pr.f._log_trace(self, "_resize_treeview", trace, add = " _configure_last_called was %f" % seconds_elapsed)
            
            if self._configure_last_called == datetime.min:
                self._configure_last_called = datetime.now()
                
            self.treeview_input_files.update()
            self.treeview_current_tags.update()
            self.treeview_suggested_tags.update()
            
            self.pr.f.configure_treeview_columns(self.treeview_input_files, 
                                                 self.treeview_input_files_columns, 
                                                 self.treeview_input_files_headers,
                                                 self.pr.f.distribute_width(self.treeview_input_files.winfo_width(), 
                                                                      self.treeview_input_files_column_widths, 
                                                                      self.treeview_input_files_fixed_width
                                                                      ), 
                                                 trace = inf_trace
                                                 )
            self.pr.f.configure_treeview_columns(self.treeview_current_tags, 
                                                 self.treeview_current_tags_columns, 
                                                 self.treeview_current_tags_headers,
                                                 self.pr.f.distribute_width(self.treeview_current_tags.winfo_width(), 
                                                                      self.treeview_current_tags_column_widths, 
                                                                      self.treeview_current_tags_fixed_width
                                                                      ), 
                                                 trace = inf_trace
                                                 )
            self.pr.f.configure_treeview_columns(self.treeview_suggested_tags, 
                                                 self.treeview_suggested_tags_columns, 
                                                 self.treeview_suggested_tags_headers,
                                                 self.pr.f.distribute_width(self.treeview_suggested_tags.winfo_width(), 
                                                                      self.treeview_suggested_tags_column_widths, 
                                                                      self.treeview_suggested_tags_fixed_width
                                                                      ), 
                                                 trace = inf_trace
                                                 )
            
            self._configure_last_called = datetime.now()
            return event
        return
    
    def _btnOutputDirectory_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnOutputDirectory_Click", trace)
        inf_trace = {"source": "function call", "parent": self.class_name + "._btnOutputDirectory_Click"}
        
        #Ask for the output directory and populate the textbox
        self.output_directory = tk.filedialog.askdirectory(initialdir="../../../../Music",  title='Select the output directory')
        self.txtOutputDirectory.delete(0, "end")
        self.txtOutputDirectory.insert(0, self.output_directory)
        config.config_dict['prcfg_last_output_directory_tagging'] = self.output_directory
        return
    
    def _btnInputDirectory_Click(self, trace = None):
        self.pr.f._log_trace(self, "_btnInputDirectory_Click", trace)
        inf_trace = {"source": "function call", "parent": self.class_name + "._btnInputDirectory_Click"}
        
        #Ask for the input directory and populate the textbox. Then pull the file list
        self.input_directory = tk.filedialog.askdirectory(initialdir="../../../../Music",  title='Select the input directory')
        self.txtInputDirectory.delete(0, "end")
        self.txtInputDirectory.insert(0, self.input_directory)
        self.populate_file_list(event = None)
        config.config_dict['prcfg_last_input_directory_tagging'] = self.input_directory
        return
    
    def _configure_treeview_columns(self, treeview, columns, headers, widths, create_columns = False, trace = None):
        self.pr.f._log_trace(self, "_configure_treeview_columns", trace)
        inf_trace = {"source": "function call", "parent": self.class_name + "._configure_treeview_columns"}
        
        column_count = len(columns)
        if column_count > 1 and create_columns:
            treeview['columns'] = columns[1:]
        
        for i in range(column_count):
            column_name = columns[i]
            column_header = headers[i]
            column_width = widths[i]
            
            if create_columns:
                treeview.heading(column_name, text = column_header)
                
            treeview.column(column_name, width = column_width, minwidth = column_width, stretch = tk.NO)
        return