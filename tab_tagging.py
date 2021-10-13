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
        self.name = "Tagging"
        self.pr = parent.pr
        self.root = parent.root
        self.parent = parent
        self.tab = parent.tab_tagging
        
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        """
        ###################################
        ############# FRAMES ##############
        ###################################
        """
        self.io_directory = IODirectory(parent = self, 
                                        trace = inf_trace, 
                                        call_after_input = 
                                            self.populate_file_list)
        TreeviewFrame = tk.Frame(self.tab,
                                 background = self.pr.c.colour_background)
        
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
        ######################################
        ############# TREEVIEW INFO ##########
        ######################################
        """
        self.treeview_input_files = ttk.Treeview(TreeviewFrame)
        self.treeview_current_tags = ttk.Treeview(TreeviewFrame)
        self.treeview_suggested_tags = ttk.Treeview(TreeviewFrame)
        self.treeviews = [self.treeview_input_files, 
                          self.treeview_current_tags,
                          self.treeview_suggested_tags]
        
        self.treeview_info = {
            self.treeview_input_files: {
                "columns": ["#0"],
                "headers": ["Filename"],
                "widths": [self.pr.c.width_text_long],
                "fixed_width": [False]
                },
            self.treeview_current_tags: {
                "columns": ["#0", "Value"],
                "headers": ["Tag", "Value"],
                "widths": [self.pr.c.width_text_short, 
                                  self.pr.c.width_text_medium],
                "fixed_width": [True, False]
                },
            self.treeview_suggested_tags: {
                "columns": ["#0", "Value"],
                "headers": ["Tag", "Value"],
                "widths": [self.pr.c.width_text_short, 
                                  self.pr.c.width_text_medium],
                "fixed_width": [True, False]
                },
            }
        
        # create columns for each treeview
        for tv in self.treeviews:
            kwargs = {k: self.treeview_info[tv][k] 
                      for k in ["columns", "headers", "widths"]}
            self.pr.f.configure_treeview_columns(treeview = tv, **kwargs,
                                                 create_columns = True,
                                                 trace = inf_trace)
        
        # arrange treeviews on grid
        InputFilesGridRow = 0
        InputFilesGridColumn = 0
        InputFilesColumnSpan = 2
        InputFilesRowSpan = 12
        
        self.treeview_input_files.grid(row = InputFilesGridRow,
                                    column = InputFilesGridColumn,
                                    columnspan = InputFilesColumnSpan,
                                    rowspan = InputFilesRowSpan,
                                    pady = self.pr.c.padding_large_top_only,
                                    sticky = "nesw",
                                    padx = self.pr.c.padding_small
                                    )      

        CurrentTagsGridRow = InputFilesGridRow
        CurrentTagsGridColumn = (InputFilesGridColumn 
                                 + InputFilesColumnSpan + 1)
        CurrentTagsColumnSpan = 1
        CurrentTagsRowSpan = InputFilesRowSpan - 1
        
        self.treeview_current_tags.grid(row = CurrentTagsGridRow, 
                                   column = CurrentTagsGridColumn, 
                                   columnspan = CurrentTagsColumnSpan,
                                   rowspan = InputFilesRowSpan,
                                   sticky = "nesw", 
                                   pady = self.pr.c.padding_large_top_only,
                                   padx = self.pr.c.padding_small
                                   )
        
        SuggestedTagsGridRow = CurrentTagsGridRow
        SuggestedTagsGridColumn = (CurrentTagsGridColumn 
                                   + CurrentTagsColumnSpan + 1)
        SuggestedTagsColumnSpan = 1
        SuggestedTagsRowSpan = InputFilesRowSpan
 
        self.treeview_suggested_tags.grid(row = SuggestedTagsGridRow, 
                                           column = SuggestedTagsGridColumn, 
                                           columnspan = SuggestedTagsColumnSpan,
                                           rowspan = SuggestedTagsRowSpan,
                                           sticky = "nesw", 
                                           pady = self.pr.c.padding_large_top_only,
                                           padx = self.pr.c.padding_small
                                           )
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

        self.treeview_input_files.bind("<ButtonRelease-1>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<ButtonRelease-1>"})) #Also <ButtonPress-1>, <Double-1> for double click, etc. - bind the selection change event, updating the tag values 
        self.treeview_input_files.bind("<KeyRelease-Up>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<KeyRelease-Up>"})) #refresh tags when moving up and down the file list with the arrow keys
        self.treeview_input_files.bind("<KeyRelease-Down>", lambda event: self.populate_current_tags_box(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<KeyRelease-Down>"}))
        
        self.treeview_input_files.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".treeview_input_files", "event": "<Configure>"}))
        self.treeview_current_tags.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".treeview_current_tags", "event": "<Configure>"}))
        self.treeview_suggested_tags.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".treeview_suggested_tags", "event": "<Configure>"}))
        self.tab.bind("<Configure>",lambda event:  self._resize_treeview(event, trace={"source": "bound event", "widget": self.name + ".tab_tagging", "event": "<Configure>"}))
        
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
        """
        Clears all treeviews and re-populates the list of filenames
        """
        
        if os.path.isdir(self.io_directory.input_directory):
            #clear all treeviews
            for tv in self.treeviews:
                tv.delete(*tv.get_children())
               
        #add all files in the specified directory with the correct extension
            for file in os.listdir(self.io_directory.input_directory):
                filename, extension = os.path.splitext(file)
                if extension == self.pr.c.file_extension:  
                    self.treeview_input_files.insert("", 
                                                     index="end", 
                                                     text = filename, 
                                                     iid = filename)
        return event
    
    def populate_current_tags_box(self, event, trace = None):
        self.pr.f._log_trace(self, "populate_current_tags_box", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".populate_current_tags_box"}
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
            self.treeview_suggested_tags.insert("", 
                                                index=i, 
                                                text=tag_list_alias[i], 
                                                values=(tag_list_value[i], ""), 
                                                iid = tag_list_alias[i])
            
        #Add current values to the relevant treeview
        tag_list_value = self.get_file_tags(directory = self.txtInputDirectory.get(), 
                                             filename = filename, 
                                             extension = self.pr.c.file_extension, 
                                             trace = inf_trace
                                             )
        for i in range(len(tag_list_alias)):
            self.treeview_current_tags.insert("", 
                                              index=i, 
                                              text=tag_list_alias[i], 
                                              values=(tag_list_value[i], ""), 
                                              iid = tag_list_alias[i])
        return event
   
    def get_file_tags(self, directory, filename, extension, trace = None):
        self.pr.f._log_trace(self, "get_file_tags", trace)
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
        
        tag_list_value = ["" if tag_value is None else tag_value 
                          for tag_value in tag_list_value] #replace None with empty string
                
        return tag_list_value

    def _resize_treeview(self, event = None, trace = None):
        if not self.pr.running: return
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._resize_treeview"}
        """
        Resize all treeview columns according to the current widget size
        """
        seconds_elapsed = (datetime.now() - self._configure_last_called).total_seconds()
        if seconds_elapsed >= self.pr.c.max_refresh_frequency_seconds:
            self.pr.f._log_trace(self, "_resize_treeview", trace, add = " _configure_last_called was %f" % seconds_elapsed)
            
            if self._configure_last_called == datetime.min:
                self._configure_last_called = datetime.now()
            
            for tv in self.treeviews:
                tv.update()
                kwargs = {k: self.treeview_info[tv][k] 
                          for k in ["columns", "headers"]}
                kwargs["widths"] = self.pr.f.distribute_width(
                    tv.winfo_width(), 
                    self.treeview_info[tv]["widths"], 
                    self.treeview_info[tv]["fixed_width"]
                    )
                self.pr.f.configure_treeview_columns(tv, **kwargs,
                                                     create_columns = False,
                                                     trace = inf_trace)
            self._configure_last_called = datetime.now()
            return event
        return
    
