# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 23:51:25 2021

@author: marcu
"""

import prospero_constants as prc
import tkinter as tk
from tkinter import ttk
import prospero_functions as prf
import re
from datetime import datetime
from button_set import ButtonSet

class ValueFromFilename:
    def __init__(self, parent, filename, columnString, columnId, treeview, 
                 row_iid = None, trace = None):
        self.tab = parent.tab
        self.parent = parent
        self.root = parent.root
        self.pr = parent.pr
        
        self.class_name = "ValueFromFilename"
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".__init__"}
        
        self.columnString = columnString
        self.filename = filename
        self.columnId = columnId
        self.treeview = treeview
        self.row_iid = filename if row_iid is None else row_iid
        self.focus = treeview.focus()
        self._configure_last_called = datetime.min
        
        self.window = tk.Toplevel(self.tab, 
                                  background = self.pr.c.colour_background)
        self.window.title("Prospero - Decide tag value from filename - " 
                          + columnString)
        
        button_additional_args = {"command" : self.pr.f.null_function}
        
        entry_additional_args = {"font" : self.pr.c.font_prospero_box_header}
        """
        ### FRAMES ###
        """
        self.window_InputOutputFrame = tk.Frame(self.window, background = self.pr.c.colour_background)
        self.window_InputOutputFrame.grid(row = 0, column = 0)
        """
        ### VALUE ###
        """
        self.value = tk.StringVar()
        """
        ### LABELS AND TEXT BOXES ###
        """
    
        labelFilenameGridRow = 0
        labelFilenameGridColumn = 0
        labelFilenameColumnSpan = 1
        labelFilenameRowSpan = 1
        
        labelFilename = tk.Label(self.window_InputOutputFrame, 
                                 text = "Filename",
                                 **self.pr.c.label_standard_args)
        
        labelFilename.grid(row = labelFilenameGridRow, 
                            column = labelFilenameGridColumn,
                            columnspan = labelFilenameColumnSpan,
                            rowspan = labelFilenameRowSpan,
                            **self.pr.c.grid_sticky_padding_small
                            )   
        
        labelTagGridRow = labelFilenameGridRow + 1
        labelTagGridColumn = labelFilenameGridColumn
        labelTagColumnSpan = labelFilenameColumnSpan
        labelTagRowSpan = 1    
        
        labelTag = tk.Label(self.window_InputOutputFrame, 
                            text = "Tag value", 
                            **self.pr.c.label_standard_args) 
        
        labelTag.grid(row = labelTagGridRow, 
                                          column = labelTagGridColumn,
                                          columnspan = labelTagColumnSpan,
                                          rowspan = labelTagRowSpan,
                                          **self.pr.c.grid_sticky_padding_small
                                          )      
        
        txtFilenameGridRow = labelFilenameGridRow
        txtFilenameGridColumn = labelFilenameGridColumn + 1
        txtFilenameColumnSpan = self.pr.c.columnspan_all
        txtFilenameRowSpan = labelFilenameRowSpan
        
        self.txt_filename = tk.Entry(self.window_InputOutputFrame,
                                     **self.pr.c.entry_medium_args,
                                     **entry_additional_args
                                     )
        
        self.txt_filename.grid(row = txtFilenameGridRow, 
                                column = txtFilenameGridColumn,
                                columnspan = txtFilenameColumnSpan,
                                rowspan = txtFilenameRowSpan,
                                **self.pr.c.grid_sticky_padding_small
                                )
        
        txtTagGridRow = txtFilenameGridRow + 1
        txtTagGridColumn = txtFilenameGridColumn
        txtTagColumnSpan = txtFilenameColumnSpan
        txtTagRowSpan = 1
        
        self.txt_tag = tk.Entry(self.window_InputOutputFrame,
                            **self.pr.c.entry_medium_args,
                            **entry_additional_args,
                            textvariable = self.value
                            )
        
        self.txt_tag.grid(row = txtTagGridRow, 
                     column = txtTagGridColumn,
                     columnspan = txtTagColumnSpan,
                     rowspan = txtTagRowSpan,
                     **self.pr.c.grid_sticky_padding_small
                     )
        
        """
        ### POPULATE txtTAG WITH CURRENT VALUE ###
        """        
        
        if not (self.treeview.item(self.focus, 'values') is None and 
            self.treeview.item(self.focus, 'values') != ''):
            self.txt_tag.insert(0, self.treeview.set(self.focus, self.columnId)) 
            #get the current value and insert it into the text box
     
        """
        ### ACTION BUTTONS ###
        """
        
        """
        # PREFIX        SUFFIX          REPLACE         SUBMIT
        # UPPERCASE     LOWERCASE       TITLE_CASE      CLEAR
        
        Actions:
            Prefix:         Insert the select text from txtFilename and add to the beginning of the txtTag value        <SELECTION> <CURRENT>
                Variant 1)      If the 'Performer(s)' column is selected and the Shift key is held, add to start with ; <SELECTION>; <CURRENT>
            Suffix:         Insert the select text from txtFilename and add to the end of the txtTag value              <CURRENT> <SELECTION>
                Variant 1)      If the Shift key is held, enclose the selection in brackets before appending            <CURRENT> (<SELECTION>)
                Variant 2)      If the 'Composer' column is selected, add to end with a comma                           <CURRENT>, <SELECTION>
                Variant 3)      If the 'Composer' column is selected and the Shift key is held, revert to default       <CURRENT> <SELECTION>
                Variant 4)      If the 'Performer(s)' column is selected and the Shift key is held, add to end with ;   <CURRENT>; <SELECTION>
            Replace:        Replace the txtTag value with the selected text                                             <SELECTION>
            Uppercase:      Convert the selected portion of the txtTag value to uppercase
                Variant 1)      If the Shift key is held, convert the entire txtTag value to uppercase
            Lowercase:      Convert the selected portion of the txtTag value to uppercase
                Variant 1)      If the Shift key is held, convert the entire txtTag value to lowercase
            Title case:      Convert the selected portion of the txtTag value to uppercase
                Variant 1)      If the Shift key is held, convert the entire txtTag value to title case
            Clear:          Delete the txtTag value
        """
        
        grid_kwargs = self.pr.c.grid_sticky
        frame_kwargs = {"bg": self.pr.c.colour_background}
        button_kwargs = self.pr.c.button_standard_args
        
        def trace_click(btn):
            return {"source": "bound event", 
                    "widget": self.class_name + ".%s" % btn, 
                    "event": "<Button-1>"}
        
        def trace_shift_click(btn):
            return {"source": "bound event", 
                    "widget": self.class_name + ".%s" % btn, 
                    "event": "<Shift-Button-1>"}
        
        bindings = {"btnPrefix": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnPrefix_Click(event, trace = trace_click("btnPrefix")),
                                               lambda event: self.btnPrefix_ShiftClick(event, trace = trace_shift_click("btnPrefix"))]
                                  },
                    "btnSuffix": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnSuffix_Click(event, trace = trace_click("btnSuffix")),
                                               lambda event: self.btnSuffix_ShiftClick(event, trace = trace_shift_click("btnSuffix"))]
                                  },
                    "btnReplace": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnReplace_Click(event, trace = trace_click("btnReplace")),
                                               lambda event: self.btnReplace_ShiftClick(event, trace = trace_shift_click("btnReplace"))]
                                  },
                    "btnSubmit": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnSubmit_Click(event, trace = trace_click("btnSubmit")),
                                               lambda event: self.btnSubmit_ShiftClick(event, trace = trace_shift_click("btnSubmit"))]
                                  },
                    "btnUppercase": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnUppercase_Click(event, trace = trace_click("btnUppercase")),
                                               lambda event: self.btnUppercase_ShiftClick(event, trace = trace_shift_click("btnUppercase"))]
                                  },
                    "btnLowercase": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnLowercase_Click(event, trace = trace_click("btnLowercase")),
                                               lambda event: self.btnLowercase_ShiftClick(event, trace = trace_shift_click("btnLowercase"))]
                                  },
                    "btnTitleCase": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnTitleCase_Click(event, trace = trace_click("btnTitleCase")),
                                               lambda event: self.btnTitleCase_ShiftClick(event, trace = trace_shift_click("btnTitleCase"))]
                                  },
                    "btnClear": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnClear_Click(event, trace = trace_click("btnClear")),
                                               lambda event: self.btnClear_ShiftClick(event, trace = trace_shift_click("btnClear"))]
                                  },
                    "btnRemoveDiacritics": {"event": ["<Button-1>",
                                            "<Shift-Button-1>"], 
                                  "function": [lambda event: self.btnRemoveDiacritics_Click(event, trace = trace_click("btnRemoveDiacritics")),
                                               lambda event: self.btnRemoveDiacritics_ShiftClick(event, trace = trace_shift_click("btnRemoveDiacritics"))]
                                  }
                    }
        
        self.buttons = ButtonSet(root = self.window,
                                 names = ["btnPrefix", "btnSuffix", 
                                          "btnReplace", "btnSubmit", 
                                          "btnUppercase", "btnLowercase", 
                                          "btnTitleCase", "btnClear", 
                                          "btnRemoveDiacritics", 
                                          "btnRematchValue", 
                                          "btnToggleFilter"],
                                 labels = ["Prefix", "Suffix", 
                                           "Replace", "Submit", 
                                           "Uppercase", "Lowercase", 
                                           "Titlecase", "Clear", 
                                           "Remove Diacritics", 
                                           "Rematch Value",
                                           "Toggle Filters"],
                                 layout = [[1, 2, 3, 4], 
                                           [5, 6, 7, 8], 
                                           [9, 10, 11]],
                                 bindings = bindings,
                                 grid_kwargs = grid_kwargs,
                                 frame_kwargs = frame_kwargs,
                                 button_kwargs = button_kwargs,
                                 set_width = 70)
        
        self.buttons.frame.grid(row = 1, column = 0, 
                                **self.pr.c.grid_sticky_padding_small)
        
        """
        ### SUGGESTED VALUES ###
        """

        self.suggested_values_columns = ["#0"]
        self.suggested_values_headers = ["Suggested values"]
        self.suggested_values_column_widths = [self.pr.c.width_text_long]
        self.suggested_values_fixed_width = [False]
        
        self.suggested_values = ttk.Treeview(self.window)
        
        self.pr.f.configure_treeview_columns(treeview = self.suggested_values, 
                                             columns = self.suggested_values_columns,
                                             headers = self.suggested_values_headers,
                                             widths = self.suggested_values_column_widths,
                                             create_columns = True,
                                             trace = inf_trace
                                             )
        self.suggested_values.grid(row = 2,
                                    column = 0,
                                    columnspan = self.pr.c.columnspan_all,
                                    rowspan = 1,
                                    **self.pr.c.grid_sticky_padding_small
                                    ) 
        #     # REMATCH VALUE BUTTON #
        #     # UNDO BUTTON #
        """
        ### POPULATE VALUES ###
        """
        
        self.txt_filename.insert(0, filename)
        self.get_insight_values(trace = inf_trace)
        self.populate_suggested_values(trace = inf_trace)
        
        """
        ### BIND EVENTS ###
        """
        self.window.bind("<Return>", lambda event: self.btnSubmit_Click(event, trace = {"source": "bound event", 
                                                                                        "widget": self.class_name + ".btnSubmit_Click", 
                                                                                        "event": "<Return>"}))
        self.value.trace_add("write", lambda *args: self._write_value(*args, trace = {"source": "bound event", 
                                                                                      "widget": self.class_name + "._write_value", 
                                                                                      "event": "write"}))
        self.suggested_values.bind("<Configure>", lambda event: self._resize_treeview(event, trace={"source": "bound event", 
                                                                                                    "widget": self.class_name + ".suggested_values", 
                                                                                                    "event": "<Configure>"}))
        self.suggested_values.bind("<1>", lambda event: self._treeview_mouse1_click(event, trace = {"source": "bound event", 
                                                                                                    "widget": self.class_name + ".suggested_values", 
                                                                                                    "event": "<1>"}))
        self.suggested_values.bind("<Double-1>", lambda event: self._treeview_double_click(event, trace = {"source": "bound event", 
                                                                                                           "widget": self.class_name + ".suggested_values", 
                                                                                                           "event": "<Double-1>"}))
        
        """
        ### MAIN LOOP ###
        """
        self.root.eval(f'tk::PlaceWindow {self.window} center')
        self.window.mainloop()
        
        return
    
    def Get_SelectedTextClean(self, objEntry, trace = None):
        self.pr.f._log_trace(self, "Get_SelectedTextClean", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".Get_SelectedTextClean"}
        
        new_text = objEntry.selection_get()
        new_text = self.pr.f.clean_track_string(new_text, 
                                                iterate = True,
                                                trace = inf_trace)
        
        return new_text
    
    def btnPrefix_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnPrefix_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnPrefix_Click"}
        
        if not self.txt_filename.selection_present():
            return event
        
        new_text = self.Get_SelectedTextClean(self.txt_filename, 
                                              trace = inf_trace) 
        new_text += " "
        self.txt_tag.insert(0, new_text)
        self.whitespace_clean(self.txt_tag, trace = inf_trace)
        self.txt_filename.selection_clear()
        return event
    
    def btnPrefix_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnPrefix_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnPrefix_ShiftClick"}
        
        self.btnPrefix_Click(event, trace = inf_trace)
        return event
    
    
    
    def btnSuffix_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnSuffix_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnSuffix_Click"}
        
        if not self.txt_filename.selection_present():
            return event
        
        if self.columnString == "Composer":
            new_text = ", " + self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
        else:
            new_text = " " + self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
            
        self.txt_tag.insert("end", new_text)
        self.whitespace_clean(self.txt_tag, trace = inf_trace)
        self.txt_filename.selection_clear()
        return event
        
    def btnSuffix_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnSuffix_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnSuffix_ShiftClick"}
        
        if not self.txt_filename.selection_present():
            return event
        
        if self.columnString == "Composer":
            new_text = " " + self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
        elif self.columnString == "Performer(s)":
            new_text = "; " + self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
        else:
            new_text = " (" + self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace) + ")"
            
        self.txt_tag.insert("end", new_text)
        self.whitespace_clean(self.txt_tag, trace = inf_trace)
        self.txt_filename.selection_clear()
        return event



    def btnReplace_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnReplace_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnReplace_Click"}
        
        if not self.txt_filename.selection_present():
            return event
        
        new_text = self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
        self.txt_tag.delete(0, "end")
        self.txt_tag.insert(0, new_text)
        self.whitespace_clean(self.txt_tag, trace = inf_trace)
        self.txt_filename.selection_clear()
        return event
        
    def btnReplace_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnReplace_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnReplace_ShiftClick"}
        
        self.btnReplace_Click(event, trace = inf_trace)
        return event    



    def btnSubmit_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnSubmit_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnSubmit_Click"}
        
        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            set_text = self.Get_SelectedTextClean(self.txt_filename)
        else:
            set_text = self.txt_tag.get().strip()
        
        set_text = self.clean_submission(set_text, self.columnString, 
                                         trace = inf_trace)
            
        self.treeview.set(self.focus, self.columnId, set_text)
        
        #update the final name column via the formula
        if not self.columnString == "Final name":
            try:
                self.parent.match_keywords(self.focus, trace = inf_trace)
            except AttributeError:
                pass
            self.parent.set_final_name(self.focus, trace = inf_trace)
            
        self.destroy(trace = inf_trace)
        self.parent.treeview_info["unsaved_changes"] = True
        return event
        
    def btnSubmit_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnSubmit_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnSubmit_ShiftClick"}
        
        self.btnSubmit_Click(event, trace = inf_trace)
        return event
        


    def btnLowercase_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnLowercase_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnLowercase_Click"}
        
        if not (self.txt_tag.selection_present() or self.txt_filename.selection_present()):
            return event
        
        if self.txt_tag.get() == "" and self.txt_filename.selection_present() == True:
            new_text = self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
        else:
            new_text = self.Get_SelectedTextClean(self.txt_tag, trace = inf_trace)
        
        new_text = new_text.lower()
        
        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text, trace = inf_trace)
        elif self.txt_filename.selection_present() and self.txt_tag.get() == "":
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event, trace = inf_trace)
        return event
        
    def btnLowercase_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnLowercase_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnLowercase_ShiftClick"}
        
        self.select_all(self.txt_tag, trace = inf_trace)
        self.btnLowercase_Click(event, trace = inf_trace)
        return event

    def btnUppercase_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnUppercase_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnUppercase_Click"}
        
        if not (self.txt_tag.selection_present() or 
                self.txt_filename.selection_present()):
            return event
        
        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            new_text = self.Get_SelectedTextClean(self.txt_filename, trace = inf_trace)
        else:
            new_text = self.Get_SelectedTextClean(self.txt_tag, trace = inf_trace)
            
        new_text = new_text.upper()
        
        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text, trace = inf_trace)
        elif self.txt_filename.selection_present() and self.txt_tag.get() == "":
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event, trace = inf_trace)
            
        return event
        
    def btnUppercase_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnUppercase_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnUppercase_ShiftClick"}
        
        self.select_all(self.txt_tag, trace = inf_trace)
        self.btnUppercase_Click(event, trace = inf_trace)
        return event    



    def btnTitleCase_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnTitleCase_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnTitleCase_Click"}
        
        if not (self.txt_tag.selection_present() or
                self.txt_filename.selection_present()):
            return event
        
        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            new_text = self.Get_SelectedTextClean(self.txt_filename, 
                                                  trace = inf_trace)
        else:
            new_text = self.Get_SelectedTextClean(self.txt_tag, 
                                                  trace = inf_trace)
        
        new_text = self.pr.f.true_titlecase(new_text, trace = inf_trace)
        
        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text, trace = inf_trace)
        elif self.txt_filename.selection_present() and self.txt_tag.get() == "":
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event, trace = inf_trace)
            
        return event
        
    def btnTitleCase_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnTitleCase_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnTitleCase_ShiftClick"}
        
        self.select_all(self.txt_tag, trace = inf_trace)
        self.btnTitleCase_Click(event, trace = inf_trace)
        return event
       
        
        
    def btnClear_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnClear_Click", trace)
        self.txt_tag.delete(0, "end")
        return event
        
    def btnClear_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnClear_ShiftClick", trace)
        self.txt_tag(event)
        return event
    
    
    
    def btnRemoveDiacritics_Click(self, event, trace = None):
        self.pr.f._log_trace(self, "btnRemoveDiacritics_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".btnRemoveDiacritics_Click"}
        
        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            new_text = self.Get_SelectedTextClean(self.txt_filename, 
                                                  trace = inf_trace)
        else:
            new_text = self.Get_SelectedTextClean(self.txt_tag, 
                                                  trace = inf_trace)
            
        new_text = self.pr.f.remove_diacritics(new_text, trace = inf_trace)
        
        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text, trace = inf_trace)
        elif self.txt_filename.selection_present() and self.txt_tag.get() == "":
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event, trace = inf_trace)
        
        
    def btnRemoveDiacritics_ShiftClick(self, event, trace = None):
        self.pr.f._log_trace(self, "btnRemoveDiacritics_ShiftClick", trace)
        inf_trace = {"source": "function call", 
                     "parent": (self.class_name + 
                                ".btnRemoveDiacritics_ShiftClick")}
        self.select_all(self.txt_tag, trace = inf_trace)
        self.btnRemoveDiacritics_Click(event, trace = inf_trace)
        

    
    def whitespace_clean(self, objEntry, trace = None):
        self.pr.f._log_trace(self, "whitespace_clean", trace)
        
        original_value = objEntry.get()
        new_value = original_value.strip()
        new_value = " ".join(new_value.split())
        objEntry.delete(0, "end")
        objEntry.insert(0, new_value)
        return
    
    def get_value(self, trace = None):
        self.pr.f._log_trace(self, "get_value", trace)
        return self.txt_tag.get()
    
    def destroy(self, trace = None):
        self.pr.f._log_trace(self, "destroy", trace)
        
        self.window.destroy()
        self.window.update()
        return
        
    def replace_selected(self, objEntry, new_text, trace = None):
        self.pr.f._log_trace(self, "replace_selected", trace)
        
        selection_start = objEntry.index(tk.SEL_FIRST)
        selection_end = objEntry.index(tk.SEL_LAST)
        
        objEntry.delete(selection_start, selection_end)
        objEntry.insert(selection_start, new_text)
        return
    
    def select_all(self, objEntry, trace = None):
        self.pr.f._log_trace(self, "select_all", trace)
        objEntry.select_from(0)
        objEntry.select_to("end")
        return
    
    def get_insight_values(self, trace = None):
        self.pr.f._log_trace(self, "get_insight_values", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".get_insight_values"}
        
        values = self.pr.f.get_values_dict(treeview = self.treeview,
                                           iid = self.row_iid,
                                           columns = self.parent.treeview_info["headers"], 
                                           trace = inf_trace)
        # All columns we don't want to filter on
        for col in ["Done", "Final name", "Genre", 
                    "Performer(s)", "URL", "", "Original name"]:
            try:
                del values[col]
            except KeyError:
                pass
        
        insight_col = self.pr.insight_rn.map_field_names(self.columnString)
        
        query = self.pr.insight_rn.get_insight(values = values, 
                                               column = insight_col, 
                                               trace = inf_trace)
        #assume one column queried and one list returned
        self.insight_values = query[insight_col]
        
    def get_suggested_values(self, text, trace = None):
        self.pr.f._log_trace(self, "get_suggested_values", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".get_suggested_values"}
        
        values = self.pr.f.autocomplete(text = text,
                                        options = self.insight_values,
                                        out = "list",
                                        trace = inf_trace)
        return values
    
    def _write_value(self, a,b,c, trace = None):
        self.pr.f._log_trace(self, "_write_value", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + "._write_value"}
        self.populate_suggested_values(trace = inf_trace)
        
    
    def populate_suggested_values(self, trace = None):
        self.pr.f._log_trace(self, "populate_suggested_values", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".populate_suggested_values"}
        
        text = self.pr.f.clean_track_string(self.txt_tag.get(),
                                            iterate = True,
                                            trace = inf_trace)
        
        values = self.get_suggested_values(text = text, trace = inf_trace)
        values = list(set(values)) #remove duplicates
        values = sorted(values)
        
        #Remove all current suggestions and add new suggestions
        self.suggested_values.delete(*self.suggested_values.get_children())
        for v in values:
            self.suggested_values.insert("", index="end", 
                                         text = v, iid = v)
    
    def _resize_treeview(self, event = None, trace = None):
        if not self.pr.running: return
        
        seconds_elapsed = (datetime.now() - 
                           self._configure_last_called).total_seconds()
        if seconds_elapsed >= self.pr.c.max_refresh_frequency_seconds:
            self.pr.f._log_trace(self, "_resize_treeview", trace, 
                                 add = " _configure_last_called was %f" % 
                                         seconds_elapsed)
            
            if self._configure_last_called == datetime.min:
                self._configure_last_called = datetime.now()
                
            #update widget info
            self.suggested_values.update()
            self.root.update()
            
            #get new width of widget
            treeview_width = self.suggested_values.winfo_width()
            
            #set width of column
            self.suggested_values.column("#0", 
                                         width = treeview_width, 
                                         minwidth = treeview_width, 
                                         stretch = tk.NO)
            
            #update the time the event was last called
            self._configure_last_called = datetime.now()
        return event

    def _treeview_mouse1_click(self, event, trace = None):
        self.pr.f._log_trace(self, "_treeview_mouse1_click", trace)
            
        self._treeview_mouse1_click_column = self.suggested_values.identify_column(event.x)
        self._treeview_mouse1_click_row = self.suggested_values.identify_row(event.y)
        self._treeview_mouse1_click_cell = (self._treeview_mouse1_click_row if self._treeview_mouse1_click_column == "#0" 
                                            else self.suggested_values.set(self._treeview_mouse1_click_row, 
                                                                           self._treeview_mouse1_click_column)
                                            )
        return event
    
    def _treeview_double_click(self, event, trace = None):
        self.pr.f._log_trace(self, "_treeview_double_click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + "._treeview_double_click"}
        
        if self.suggested_values.selection() == []:
            return event
        
        self.txt_tag.delete(0, "end")
        self.txt_tag.insert(0, self._treeview_mouse1_click_cell)
        self.whitespace_clean(self.txt_tag, trace = inf_trace)
        self.suggested_values.selection_clear()
        self.btnSubmit_Click(event, trace = inf_trace)
        
    def clean_submission(self, value, column, trace = None):
        self.pr.f._log_trace(self, "clean_submission", trace)
        
        if column == "URL":
            value = value.replace(r"https://", "")
            value = value.replace(r"http://", "")
            
        return value
        