# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 19:37:23 2021

@author: marcu
"""

from math import gcd
from functools import reduce
import tkinter as tk

def lcm(*args):
    lcm = 1
    for x in args:
        lcm *= x//gcd(lcm, x)
    return lcm

class WidgetLayout:
    """
    Private class containing layout logic for the WidgetSet classes. Should
    not be instantiated directly.
    """
    def __init__(self, layout):
        self.original_layout = layout
        self.span = self._get_set_width(layout)
        self.height = self._get_set_height(layout)
        self.layout = self._normalise_layout(layout)

    def _normalise_layout(self, layout):
        """
        Clean the specified layout. If all values are non-lists, assume all
        buttons should be placed on a single line. Otherwise, take a non-list 
        to mean a button covering an entire line.
        
        Normalise the layout so that all lists have the same length. Where
        an impossible layout has been specified, adjust the scaling to
        approximate the input as closely as possible. The heirarchy here is
        to prioritise the scaling in earlier rows and then allocate/trim any 
        extra/missing space from re-distributing later button spacing.
        """
        has_list = False
        for k in layout:
            if isinstance(k, list):
                has_list = True
                break
        
        if has_list:
            for i, k in enumerate(layout):
                if not isinstance(k, list):
                    layout[i] = [k]
        else:
            layout = [layout]

        
        span_dict = {}
        
        for i, layer in enumerate(layout):
            layer_out = []
            
            # how much of the width of the layer each item in the list
            # corresponds to, as a fraction
            layer_above = layout[i-1] if i != 0 else []
            
            for j, x in enumerate(layer):
                if x in layer_out and x != -1:
                    continue
                
                exp_start = len(layer_out)
                try:
                    act_start = layer_above.index(x)
                except ValueError:
                    act_start = exp_start

                if act_start < exp_start:
                    pass
                    # if the space being overlaid is blank, continue
                    if list(set(layer[act_start:exp_start])) == [-1]:
                        pass
                    else:
                    # TODO - work out how much space must be taken away from
                    # previous buttons. allocate that removed space so that
                    # proportions are preserved
                        raise ValueError("Unable to draw button set. "
                                          "Objects would overlap")
                elif act_start > exp_start:
                    pad_len = act_start - exp_start
                    if len(layer_out) == 0:
                        pad_val = -1
                    elif layer_out[-1] not in layer_above:
                        pad_val = layer_out[-1]
                    else:
                        pad_val = -1
                    layer_out += [pad_val]*pad_len
                    
                    scale = lcm(pad_len, len(layer))
                    for j in range(i):
                        layout[j] = self._scale_list(layout[j], scale)
                    for key in span_dict:
                        span_dict[key] *= scale
                    layer_out = self._scale_list(layer_out, scale)
                    layer_above = self._scale_list(layer_above, scale)
                    self.span *= scale
                    
                available_span = self.span - len(layer_out)
                if x == -1:
                    count = self._count_sequence(layer, x, start = j)
                else:
                    count = layer.count(x)
                exp_span = int(count/len(layer[j:]) * available_span)
                act_span = (span_dict[x] if x in span_dict.keys() and x != -1 
                            else exp_span)
                span_diff = exp_span - act_span
                
                # allocate the difference if the expected and actual spans
                # are different
                scale = 1
                if span_diff != 0:
                    unallocated_items = [k for k in layer 
                                         if not (k in layer_out or k == x)]
                    # scale up the whole layout to ensure the difference can
                    # be properly allocated according to the defined 
                    # proportions
                    scale = len(unallocated_items)
                    for j in range(i):
                        layout[j] = self._scale_list(layout[j], scale)
                    for key in span_dict:
                        span_dict[key] *= scale
                    layer_out = self._scale_list(layer_out, scale)
                    layer_above = self._scale_list(layer_above, scale)
                    self.span *= scale
                
                span_dict[x] = act_span*scale
                layer_out += [x]*(act_span*scale)
                     
            layout[i] = layer_out
        
        # pad the layout to ensure each layer is the same length
        len_dict = {i: len(layer) for i, layer in enumerate(layout)}
        max_layer_len = max(list(len_dict.values()))
        for i, layer in enumerate(layout):
            layout[i] = layer + [-1]*(max_layer_len - len_dict[i])
        
        # reduce the layout to the smallest version preserving the allocated
        # spacing
        layout, span_gcd = self._reduce_layout(layout)
        # self.span_dict = {k: int(span_dict[k]/span_gcd) for k in span_dict}
        return layout

    def _scale_list(self, lst, scale):
        lst_out = []
        for x in lst:
            lst_out += [x]*scale
        return lst_out
    
    def _reduce_layout(self, layout):
        """
        Reduce a layout to the smallest possible version which preserves all
        scaling.
        """
        counts = []
        for i in self._get_indices(layout):
            for layer in layout:
                counts.append(layer.count(i))
        
        count_gcd = reduce(gcd, counts)
        return [layer[::count_gcd] for layer in layout], count_gcd
    
    def _count_sequence(self, lst, value, start = 0):
        """
        Count the number of sequential occurrences of a value in a list after
        a defined point.
        """
        lst = lst[start:]
        try:
            lst = lst[lst.index(value):]
            i = 0
            while lst[i] == value:
                i += 1
            return i
        except ValueError:
            return 0

    def _get_indices(self, layout):
        return list(set([i for layer in layout for i in layer if i >= 0]))

    def _check_layout(self, layout):
        for i, layer in enumerate(layout):
            vdict = {x: layer.count(x) for x in set(layer)}
            print("Layer %s: %s, " % (i, len(layer)), vdict, layer)
        
        for num in self.indices:
            print({"num": num, 
                   "row": self._get_grid_row(num),
                   "column": self._get_grid_column(num),
                   "rowspan": self._get_row_span(num),
                   "columnspan": self._get_column_span(num)
                   })

    def _get_set_width(self, layout = None):
        if layout is None: layout = self.layout
        lengths = [len(k) for k in layout]
        return lcm(*lengths)
        
    def _get_set_height(self, layout = None):
        if layout is None: layout = self.layout
        return len(layout)


class WidgetSet(WidgetLayout):
    def __init__(self, root, widgets, layout, kwargs_dict = None,
                 frm_kwargs = None, grd_kwargs = None, spc_kwargs = None):
        """
        Parameters
        ----------
        root : tk.Frame
            master to add the frame to.
        widgets : dict
            dict of tkinter widgets with keys the corresponding numbers used
            when specifying the layout
        layout : list
            Up to 2-dimensional list defining the layout of the buttons. Use
            sequential numbers aligning to the list of button names.
            [[1, 2 , 2],[1, 3, 4],[5]] will result in a set of buttons that
            looks like the following:
            [1][  2 ]
            ["][3][4]
            [   5   ]
            The number of entries in each row will weight the relative width of
            each button.
            Use negative numbers to insert a blank space in the button set. 
            Where buttons span multiple rows, the button width is determined by 
            the first row it appears.
        w_kwargs : dict
            Dictionary  of dictionaries to use as grid_kwargs
            when arranging the widgets. keys must be the widget names.
            Use key 'all' to apply the specified kwargs to all widgets.
        frm_kwargs : dict
            kwargs to pass to the frame object.
        """
        self.name = self.__class__.__name__
        self.widgets = widgets
        self.root = root

        self.frm_kwargs = {} if frm_kwargs is None else frm_kwargs
        self.grd_kwargs = {} if grd_kwargs is None else grd_kwargs
        self.spc_kwargs = {} if spc_kwargs is None else spc_kwargs

        self.frame = tk.Frame(self.root, **frm_kwargs)
        super().__init__(layout)

        if not widgets is None and widgets != {}:
            self.create_widgets()

    def create_widgets(self):
        for key, w_dict in self.widgets.items():
            if key < 0: continue

            w_dict.setdefault("grid_kwargs", {})
            w = w_dict["widget"]
            w.grid(**self._get_grid_kwargs(key),
                   **w_dict["grid_kwargs"])

        self._create_spacers()
        self.rc_configure()

    def _get_grid_kwargs(self, key):
        return {"row": self._get_grid_row(key),
                "column": self._get_grid_column(key),
                "rowspan": self._get_row_span(key),
                "columnspan": self._get_column_span(key)}

    def _get_row_span(self, key):
        i = 0
        for n, layer in enumerate(self.layout):
            if key in layer:
                i += 1
        return None if i == 0 else i
    
    def _get_column_span(self, key):
        for layer in self.layout:
            count = layer.count(key)
            if count != 0: return count
            
    def _get_grid_row(self, key):
        for n, layer in enumerate(self.layout):
            if key in layer:
                return n

    def _get_grid_column(self, key):
        """
        Return index of first column widget appears
        """
        for layer in self.layout:
            try:
                return layer.index(key)
            except:
                continue

    def get_frame(self):
        return self.frame

    def _create_spacers(self):
        for i, layer in enumerate(self.layout):
            for j, x in enumerate(layer):
                if x < 0:
                    self.widgets.setdefault(x, {})
                    self.widgets[x].setdefault("grid_kwargs", {})
                    self._add_spacer(i, j, 1, 1,
                                     self.widgets[x]["grid_kwargs"])
    
    def _add_spacer(self, row, column, rowspan = 1, columnspan = 1,
                    grd_kwargs = None):
        lbl_width = int(self.set_width/self.span*columnspan)
        spc = tk.Label(master = self.frame,
                       width = lbl_width,
                        **self.spc_kwargs)
        grd_kwargs = {} if grd_kwargs is None else grd_kwargs
        spc.grid(row = row,
                  column = column,
                  rowspan = rowspan,
                  columnspan = columnspan,
                  **grd_kwargs
                  )

    def rc_configure(self):
        """
        Configure the row/column allocation of scaling changes. Strictly
        enforces fixed width assumptions. If unspecified, assume that the
        widget should be fixed width.
        """
        # dictionary of whether to allow each row or column to stretch
        rc_cfg = {
            "column": {c: True for c in range(self._get_set_width())},
            "row": {r: True for r in range(self._get_set_height())}
            }

        # Check each cell and fix width/height of those intersecting a fixed
        # width/height widget
        for r, layer in enumerate(self.layout):
            for c, wdgt in enumerate(layer):
                if not self.widgets[wdgt].get("stretch_width", False):
                    rc_cfg["column"][c] = False

                if not self.widgets[wdgt].get("stretch_height", False):
                    rc_cfg["row"][r] = False

        for c, bln in rc_cfg["column"].items():
            if bln:
                self.frame.columnconfigure(c, weight = 1)
            else:
                self.frame.columnconfigure(c, weight = 0)

        for r, bln in rc_cfg["row"].items():
            if bln:
                self.frame.rowconfigure(r, weight = 1)
            else:
                self.frame.rowconfigure(r, weight = 0)

class ButtonSet(WidgetSet):
    """
    Generate a bound button set from a dictionary of buttons and bindings and
    corresponding layout matrix
    """
    def __init__(self, root, buttons, set_width, layout, **kwargs):
        self.root = root
        self.buttons = buttons
        self.set_width = set_width
        grd_kwargs = {key: buttons[key].setdefault("grid_kwargs", {})
                    for key in buttons}
        super().__init__(root = root, widgets = {}, layout = layout,
                         grd_kwargs = grd_kwargs, **kwargs)
        for key in buttons:
             self.add_button(key)
        self.widgets = self.buttons
        self.create_widgets()

    def add_button(self, key):
        if key < 0: return
        btn_width = int(self.set_width*self._get_column_span(key)/self.span)

        btn_args = self.buttons[key]
        btn_args.setdefault("kwargs", {})

        # Create tk button
        btn = tk.Button(master = self.frame,
                        text = btn_args["label"],
                        width = btn_width,
                        **btn_args["kwargs"]
                        )

        bindings = btn_args.get("bindings")
        if bindings is not None:
            events = bindings["event"]
            functions = bindings["function"]
            if isinstance(events, str): events = [events]
            if isinstance(functions, str): functions = [functions]
            for i in range(len(events)):
                event = events[i]
                function = functions[i]
                btn.bind(event, function)

        self.buttons[key]["widget"] = btn

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background = "black", padx=15, pady=10)
    
    def btn1(*args):
        print("btn1 click")
        
    def btn1_shift(*args):
        print("btn1 shift click")
    
    bindings = {"btn1": {"event": ["<Button-1>", "<Shift-Button-1>"], 
                         "function": [btn1, btn1_shift]}}

    buttons = {1: {"label": "btn1",
                   "bindings": {"event": ["<Button-1>", "<Shift-Button-1>"],
                                "function": [btn1, btn1_shift]},
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": False, "stretch_height": True},
               2: {"label": "btn2",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": True},
               3: {"label": "btn3",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": True},
               4: {"label": "btn4",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": True},
               5: {"label": "btn5",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": True},
               6: {"label": "btn6",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": False},
               7: {"label": "btn7",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": True},
               8: {"label": "btn8",
                   "grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": False, "stretch_height": True},
               -1: {"grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": False, "stretch_height": True},
               -2: {"grid_kwargs": {"sticky": "nesw"},
                   "stretch_width": True, "stretch_height": True},
               }

    bs = ButtonSet(root,
                   buttons = buttons,
                    layout = [[-1, 7, -2, 1, 2, 8],[6, 1, 2, 3, 4],[5]],
                    frm_kwargs = {"bg": "black"},
                    spc_kwargs = {"bg": "black"},
                    set_width = 70)

    print(bs.layout)

    # bs._check_layout(bs.layout)
    
    bs.get_frame().grid(row = 1, column = 1, **{"sticky" : "nesw"})
    root.rowconfigure(0, weight = 0)
    root.columnconfigure(0, weight = 0)
    root.rowconfigure(1, weight = 1)
    root.columnconfigure(1, weight = 1)
    root.rowconfigure(2, weight = 0)
    root.columnconfigure(2, weight = 0)
    root.mainloop()