# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 23:51:25 2021

@author: marcu
"""

import tkinter as tk
from datetime import datetime
from arrange_widgets import WidgetSet, ButtonSet
import described_widgets as dw

class ValueFromFilename:
    def __init__(self, parent, filename, columnString, columnId, treeview,
                 row_iid = None):
        self.tab = parent.tab
        self.parent = parent
        self.root = parent.root
        self.pr = parent.pr

        self.name = "ValueFromFilename"


        self.column_string = columnString
        self.filename = filename
        self.column_id = columnId
        self.treeview = treeview
        self.row_iid = filename if row_iid is None else row_iid
        self.focus = treeview.focus()
        self._configure_last_called = datetime.min
        self.filter_insight = True

        self.window = tk.Toplevel(self.tab,
                                  background = self.pr.c.colour_background)
        self.window.title("Prospero - Decide tag value from filename - "
                          + columnString)

        entry_kwargs = {"font" : self.pr.c.font_prospero_box_header}
        frame_kwargs = {"bg": self.pr.c.colour_background}

        # frame to contain all widgets in window
        self.widget_frame = tk.Frame(self.window, **frame_kwargs)

        """
        ### VALUE ###
        """
        self.value = tk.StringVar()
        """
        ### LABELS AND TEXT BOXES ###
        """
        lblFilename = tk.Label(self.widget_frame,
                               text = "Filename",
                               **self.pr.c.label_standard_args)

        lblTag = tk.Label(self.widget_frame,
                          text = "Tag value",
                          **self.pr.c.label_standard_args)

        self.txt_filename = tk.Entry(self.widget_frame,
                                     **self.pr.c.entry_medium_args,
                                     **entry_kwargs
                                     )

        self.txt_tag = tk.Entry(self.widget_frame,
                                **self.pr.c.entry_medium_args,
                                **entry_kwargs,
                                textvariable = self.value
                                )
        """
        ### POPULATE txtTAG WITH CURRENT VALUE ###
        """
        #get the current value and insert it into the text box
        if not (self.treeview.item(self.focus, 'values') is None and
            self.treeview.item(self.focus, 'values') != ''):
            self.txt_tag.insert(0, self.treeview.set(self.focus, self.column_id))

        """
        ### ACTION BUTTONS ###

        # PREFIX        SUFFIX          REPLACE         SUBMIT
        # UPPERCASE     LOWERCASE       TITLE_CASE      CLEAR
        # REMOVE DIACRITICS     REMATCH VALUE   TOGGLE FILTERS

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

        buttons = {1: {"label": "Prefix",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnPrefix_Click,
                                                 self.btnPrefix_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   2: {"label": "Suffix",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnSuffix_Click,
                                                 self.btnSuffix_ShiftClick]
                              },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   3: {"label": "Replace",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnReplace_Click,
                                                 self.btnReplace_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   4: {"label": "Submit",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnSubmit_Click,
                                                 self.btnSubmit_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   5: {"label": "Uppercase",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnUppercase_Click,
                                                 self.btnUppercase_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   6: {"label": "Lowercase",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnLowercase_Click,
                                                 self.btnLowercase_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   7: {"label": "Title Case",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnTitleCase_Click,
                                                 self.btnTitleCase_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   8: {"label": "Clear",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnClear_Click,
                                                 self.btnClear_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   9: {"label": "Remove Diacritics",
                       "bindings": {"event": ["<Button-1>",
                                              "<Shift-Button-1>"],
                                    "function": [self.btnRemoveDiacritics_Click,
                                                 self.btnRemoveDiacritics_ShiftClick]
                                    },
                       "widget_kwargs": self.pr.c.button_standard_args,
                       "grid_kwargs": self.pr.c.grid_sticky,
                       "stretch_width": True, "stretch_height": True},
                   10: {"label": "Rematch Value",
                        "bindings": {"event": ["<Button-1>",
                                               "<Shift-Button-1>"],
                                     "function": [self.btnRematchValue_Click,
                                                  self.btnRematchValue_ShiftClick]
                                     },
                       "widget_kwargs": self.pr.c.button_standard_args,
                        "grid_kwargs": self.pr.c.grid_sticky,
                        "stretch_width": True, "stretch_height": True},
                   11: {"label": "Toggle Filters",
                        "bindings": {"event": ["<Button-1>",
                                               "<Shift-Button-1>"],
                                     "function": [self.btnToggleFilters_Click,
                                                  self.btnToggleFilters_ShiftClick]
                                     },
                       "widget_kwargs": self.pr.c.button_standard_args,
                        "grid_kwargs": self.pr.c.grid_sticky,
                        "stretch_width": True, "stretch_height": True},
                    }


        self.button_set = ButtonSet(root = self.widget_frame,
                                 buttons = buttons,
                                 layout = [[1, 2, 3, 4],
                                           [5, 6, 7, 8],
                                           [9, 10, 11]],
                                 frm_kwargs = frame_kwargs,
                                 set_width = 70)

        """
        ### SUGGESTED VALUES ###
        """
        self.suggested_values = dw.SimpleTreeview(
            self.widget_frame, {1: {"header": "Suggested values",
                                    "width": self.pr.c.width_text_long,
                                    "stretch": True,
                                    "anchor": "w"}
                                }
            )

        """
        ### POPULATE VALUES ###
        """
        self.txt_filename.insert(0, filename)
        self.get_insight_values()
        self.populate_suggested_values()

        """
        ### BIND EVENTS ###
        """
        self.window.bind("<Return>", self.btnSubmit_Click)
        self.value.trace_add("write", self._write_value)
        self.suggested_values.events.add("<1>")
        self.suggested_values.bind("<Double-1>", self._treeview_double_click)

        """
        ### ALLOCATE SCALING ###
        """
        widgets = {1: {'widget': lblFilename,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small},
                   2: {'widget': self.txt_filename,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                       'stretch_width': True},
                   3: {'widget': lblTag,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small},
                   4: {'widget': self.txt_tag,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                       'stretch_width': True},
                   5: {'widget': self.button_set.frame,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                       'stretch_width': True, 'stretch_height': True,
                       "stretch_height_weight": 1},
                   6: {'widget': self.suggested_values,
                       'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                       'stretch_width': True, 'stretch_height': True,
                       'stretch_height_weight': 5},
                   }

        self.widget_set = WidgetSet(frame = self.widget_frame,
                                    widgets = widgets,
                                    layout = [[1, 2, 2, 2],
                                              [3, 4, 4, 4],
                                              [5],
                                              [6]]
                                    )
        self.widget_set.grid(row = 0, column = 0,
                             sticky = "nesw")
        self.window.columnconfigure(0, weight = 1)
        self.window.rowconfigure(0, weight = 1)

        """
        ### MAIN LOOP ###
        """
        self.root.eval(f'tk::PlaceWindow {self.window} center')
        self.start()
        return

    def start(self):
        self.window.transient(self.tab)
        self.window.grab_set()
        self.window.mainloop()

    def Get_SelectedTextClean(self, tk_entry):
        new_text = tk_entry.selection_get()
        new_text = self.pr.f.clean_track_string(new_text, iterate = True)
        return new_text

    def btnPrefix_Click(self, event):
        if not self.txt_filename.selection_present():
            return event

        new_text = self.Get_SelectedTextClean(self.txt_filename)
        new_text += " "
        self.txt_tag.insert(0, new_text)
        self.whitespace_clean(self.txt_tag)
        self.txt_filename.selection_clear()

    def btnPrefix_ShiftClick(self, event):
        self.btnPrefix_Click(event)

    def btnSuffix_Click(self, event):
        if not self.txt_filename.selection_present():
            return event

        if self.column_string == "Composer":
            new_text = ", " + self.Get_SelectedTextClean(
                self.txt_filename)
        else:
            new_text = " " + self.Get_SelectedTextClean(
                self.txt_filename)

        self.txt_tag.insert("end", new_text)
        self.whitespace_clean(self.txt_tag)
        self.txt_filename.selection_clear()

    def btnSuffix_ShiftClick(self, event):
        if not self.txt_filename.selection_present():
            return event

        if self.column_string == "Composer":
            new_text = " " + self.Get_SelectedTextClean(self.txt_filename)
        elif self.column_string == "Performer(s)":
            new_text = "; " + self.Get_SelectedTextClean(self.txt_filename)
        else:
            new_text = " (%s)" % self.Get_SelectedTextClean(self.txt_filename)

        self.txt_tag.insert("end", new_text)
        self.whitespace_clean(self.txt_tag)
        self.txt_filename.selection_clear()



    def btnReplace_Click(self, event):
        if not self.txt_filename.selection_present():
            return event

        new_text = self.Get_SelectedTextClean(self.txt_filename)
        self.txt_tag.delete(0, "end")
        self.txt_tag.insert(0, new_text)
        self.whitespace_clean(self.txt_tag)
        self.txt_filename.selection_clear()

    def btnReplace_ShiftClick(self, event):
        self.btnReplace_Click(event)


    def btnSubmit_Click(self, event):
        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            set_text = self.Get_SelectedTextClean(self.txt_filename)
        else:
            set_text = self.txt_tag.get().strip()

        set_text = self.clean_submission(set_text, self.column_string,
                                         )

        self.treeview.set(self.focus, self.column_id, set_text)

        #update the final name column via the formula
        if not self.column_string == "Final name":
            try:
                self.parent.match_keywords(self.focus)
            except AttributeError:
                pass
            self.parent.set_final_name(self.focus)

        self.destroy()
        self.parent.treeview_info["unsaved_changes"] = True

    def btnSubmit_ShiftClick(self, event):
        self.btnSubmit_Click(event)


    def btnLowercase_Click(self, event):
        if not (self.txt_tag.selection_present()
                or self.txt_filename.selection_present()):
            return event

        if (self.txt_tag.get() == ""
            and self.txt_filename.selection_present() == True):
            new_text = self.Get_SelectedTextClean(
                self.txt_filename)
        else:
            new_text = self.Get_SelectedTextClean(
                self.txt_tag)
        new_text = new_text.lower()

        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text)
        elif self.txt_filename.selection_present() and self.txt_tag.get() == "":
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event)

    def btnLowercase_ShiftClick(self, event):
        self.select_all(self.txt_tag)
        self.btnLowercase_Click(event)

    def btnUppercase_Click(self, event):
        if not (self.txt_tag.selection_present() or
                self.txt_filename.selection_present()):
            return event

        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            new_text = self.Get_SelectedTextClean(
                self.txt_filename)
        else:
            new_text = self.Get_SelectedTextClean(
                self.txt_tag)

        new_text = new_text.upper()

        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text)
        elif (self.txt_filename.selection_present()
              and self.txt_tag.get() == ""):
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event)

    def btnUppercase_ShiftClick(self, event):
        self.select_all(self.txt_tag)
        self.btnUppercase_Click(event)



    def btnTitleCase_Click(self, event):
        if not (self.txt_tag.selection_present() or
                self.txt_filename.selection_present()):
            return event

        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            new_text = self.Get_SelectedTextClean(self.txt_filename)
        else:
            new_text = self.Get_SelectedTextClean(self.txt_tag)

        new_text = self.pr.f.true_titlecase(new_text)

        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text)
        elif (self.txt_filename.selection_present()
              and self.txt_tag.get() == ""):
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event)

    def btnTitleCase_ShiftClick(self, event):
        self.select_all(self.txt_tag)
        self.btnTitleCase_Click(event)


    def btnClear_Click(self, event):
        self.txt_tag.delete(0, "end")

    def btnClear_ShiftClick(self, event):
        self.btnClear_Click(event)


    def btnRemoveDiacritics_Click(self, event):
        if self.txt_tag.get() == "" and self.txt_filename.selection_present():
            new_text = self.Get_SelectedTextClean(self.txt_filename)
        else:
            new_text = self.Get_SelectedTextClean(self.txt_tag)

        new_text = self.pr.f.remove_diacritics(new_text)

        if self.txt_tag.selection_present():
            self.replace_selected(self.txt_tag, new_text)
        elif (self.txt_filename.selection_present()
              and self.txt_tag.get() == ""):
            self.txt_tag.insert("end", new_text)
            self.btnSubmit_Click(event)

    def btnRemoveDiacritics_ShiftClick(self, event):
        self.select_all(self.txt_tag)
        self.btnRemoveDiacritics_Click(event)


    def btnRematchValue_Click(self, event):
        rematch = self.pr.f.suggest_value(self.filename, self.column_string)
        if not rematch is None and rematch != "":
            self.btnClear_Click(event)
            self.txt_tag.insert("end", rematch)

    def btnRematchValue_ShiftClick(self, event):
        self.btnRematchValue_Click(event)


    def btnToggleFilters_Click(self, event):
        self.filter_insight = not self.filter_insight
        self.get_insight_values()
        self.populate_suggested_values(text = "")

    def btnToggleFilters_ShiftClick(self, event):
        self.btnToggleFilters_Click(event)


    def whitespace_clean(self, objEntry):
        original_value = objEntry.get()
        new_value = original_value.strip()
        new_value = " ".join(new_value.split())
        objEntry.delete(0, "end")
        objEntry.insert(0, new_value)

    def get_value(self):
        return self.txt_tag.get()

    def destroy(self):
        self.window.destroy()
        self.window.update()

    def replace_selected(self, objEntry, new_text):

        selection_start = objEntry.index(tk.SEL_FIRST)
        selection_end = objEntry.index(tk.SEL_LAST)

        objEntry.delete(selection_start, selection_end)
        objEntry.insert(selection_start, new_text)

    def select_all(self, objEntry):
        objEntry.select_from(0)
        objEntry.select_to("end")

    def get_insight_values(self):
        if self.filter_insight:
            values = self.pr.f.get_values_dict(
                treeview = self.treeview,
                iid = self.row_iid,
                columns = self.treeview.get_columns(include_key = True)
                )
        else:
            values = {}

        invalid_cols = ["Done", "Final name", "Genre", "Performer(s)", "URL",
                        "", "Original name"]

        # All columns we don't want to filter on
        for col in invalid_cols:
            try: del values[col]
            except KeyError: pass

        insight_col = self.pr.insight_rn.map_field_names(self.column_string)

        if insight_col in invalid_cols:
            self.insight_values = []
            return

        query = self.pr.insight_rn.get_insight(
            values = values, column = insight_col, distinct = True)

        #assume one column queried and one list returned
        self.insight_values = query[insight_col]

    def get_suggested_values(self, text):
        values = self.pr.f.autocomplete(
            text = text, options = self.insight_values, out = "list")
        return values

    def _write_value(self, *args, **kwargs):
        self.populate_suggested_values()

    def populate_suggested_values(self, text = None):
        if text is None:
            text = self.pr.f.clean_track_string(
                self.txt_tag.get(), iterate = True)

        values = self.get_suggested_values(text = text)
        values = sorted(values)

        #Remove all current suggestions and add new suggestions
        self.suggested_values.clear()
        for v in values:
            self.suggested_values.insert("", index="end", text = v, iid = v)

    def _treeview_double_click(self, event):
        if self.suggested_values.selection() == []:
            return event

        self.txt_tag.delete(0, "end")
        self.txt_tag.insert(0, self.suggested_values.events.last["cell"])
        self.whitespace_clean(self.txt_tag)
        self.suggested_values.selection_clear()
        self.btnSubmit_Click(event)

    def clean_submission(self, value, column):
        if column == "URL":
            value = value.replace(r"https://", "")
            value = value.replace(r"http://", "")
        return value