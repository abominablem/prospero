# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 22:04:30 2021

@author: marcu
"""

import tkinter as tk
from math import gcd
from functools import reduce

class ButtonSet:
    """
    Generates a set of buttons from a defined layout with optional custom
    bindings.
    """
    def __init__(self, root, names, labels, layout, set_width, bindings = None,  
                 frame_kwargs = None, button_kwargs = None, 
                 grid_kwargs = None):
        """
        Parameters
        ----------
        root : tk.Frame
            master to add the frame to.
        names : list
            List of button names to assign sequentially to the buttons.
        labels : list
            List of labels to assign sequentially to the buttons.
        bindings : dict
            Dictionary of button name to dictionary with "event" and 
            "function" keys. Values can be event string and function, or lists
            of events strings and corresponding functions.
        layout : list
            Multi-dimensional list defining the layout of the buttons. Use
            sequential numbers aligning to the list of button names.
            [[1, 2 , 2],[1, 3, 4],[5]] will result in a set of buttons that
            looks like the following:
            [1][  2 ]
            ["][3][4]
            [   5   ]
            The number of entries in each row will weight the relative width of
            each button.
            Use -1 to insert a blank space in the button set. Where buttons
            span multiple rows, the button width is determined by the first row
            it appears.
        set_width : int
            Total width of the button set. 
        frame_kwargs : dict
            kwargs to pass to frame object.
        button_kwargs : dict
            kwargs to pass to each new button object.
        button_kwargs : dict
            kwargs to pass to each call to grid().

        """
        self.name = self.__class__.__name__
        self.buttons = {}
        self.root = root
        self.names = names
        self.labels = labels
        self.bindings = {} if bindings is None else bindings
        self.button_kwargs = {} if button_kwargs is None else button_kwargs
        self.frame_kwargs = {} if frame_kwargs is None else frame_kwargs
        self.grid_kwargs = ({"sticky" : "nesw"} if grid_kwargs is None 
                            else grid_kwargs)
        self.set_width = set_width
        
        self.original_layout = layout[:]
        self.layout = self._normalise_layout(layout)
        self.indices = self._get_indices(self.layout)
        self.min_index = min(self.indices)
        
        self.frame = tk.Frame(self.root, **self.frame_kwargs)
        for i in self.indices:
            if i >= 0: 
                self._add_button(i)
                
        self._add_spacers()
        self._grid_configure()
        
    def _get_indices(self, layout):
        return list(set([i for layer in layout for i in layer if i >= 0]))
    
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
            
        self.span = self._get_set_width(layout)
        self.height = self._get_set_height(layout)
        
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
                    #if the space being overlaid is blank, continue
                    if list(set(layer[act_start:exp_start])) == [-1]:
                        pass
                    #TODO - work out how much space must be taken away from
                    # previous buttons. allocate that removed space so that
                    #proportions are preserved
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
                    
                    scale = self._lcm(pad_len, len(layer))
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
    
    def _ordered_set(self, lst):
        """
        Remove duplicates from a list while preserving the order
        """
        new_lst = []
        for x in lst:
            if not x in new_lst: new_lst.append(x)
        return new_lst
    
    def _add_button(self, num):
        index = num - self.min_index
        btn_width = int(self.set_width/self.span*self._get_column_span(num))
        btn = tk.Button(master = self.frame, 
                        text = self.labels[index],
                        width = btn_width,
                        **self.button_kwargs)
        btn_name = self.names[index]
        self.buttons[btn_name] = btn
        bindings = self.bindings.get(btn_name)
        
        # bind relevant functions
        if bindings is not None:
            events = bindings["event"]
            functions = bindings["function"]
            if isinstance(events, str): events = [events]
            if isinstance(functions, str): functions = [functions]
            for i in range(len(events)):
                event = events[i]
                function = functions[i]
                btn.bind(event, function)
        
        btn_grd_kwargs = {"row": self._get_grid_row(num),
                          "column": self._get_grid_column(num),
                          "rowspan": self._get_row_span(num),
                          "columnspan": self._get_column_span(num)}
        
        btn.grid(**btn_grd_kwargs,
                 **self.grid_kwargs
                 )
    
    def _add_spacers(self):
        for i, layer in enumerate(self.layout):
            for j, x in enumerate(layer):
                if x == -1:
                    self._add_spacer(i, j, 1, 1)
    
    def _add_spacer(self, row, column, rowspan, columnspan):
        lbl_width = int(self.set_width/self.span*columnspan)
        spc = tk.Label(master = self.frame,
                       width = lbl_width,
                        **self.frame_kwargs)
        spc.grid(row = row,
                  column = column,
                  rowspan = rowspan,
                  columnspan = columnspan,
                  **self.grid_kwargs
                  )
        return
    
    def _get_row_span(self, num):
        i = 0
        for n, layer in enumerate(self.layout):
            if num in layer:
                i += 1
        return None if i == 0 else i
    
    def _get_column_span(self, num):
        for layer in self.layout:
            count = layer.count(num)
            if count != 0: return count
            
    def _get_grid_row(self, num):
        for n, layer in enumerate(self.layout):
            if num in layer:
                return n
        
    def _get_grid_column(self, num):
        for layer in self.layout:
            try:
                return layer.index(num)
            except:
                continue
        
    def _get_set_width(self, layout):
        lengths = [len(k) for k in layout]
        return self._lcm(*lengths)
        
    def _get_set_height(self, layout):
        return len(layout)
        return
    
    def _lcm(self, *args):
        lcm = 1
        for x in args:
            lcm = lcm*x//gcd(lcm, x)
        return lcm
    
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
    
    def get_frame(self):
        return self.frame
    
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
            
    def _grid_configure(self):
        for r in range(self._get_set_height(self.layout)):
            self.frame.rowconfigure(r, weight=1)
        for c in range(self._get_set_width(self.layout)):
            self.frame.columnconfigure(c, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background = "black", padx=15, pady=10)
    
    def btn1(*args):
        print("btn1 click")
        
    def btn1_shift(*args):
        print("btn1 shift click")
    
    bindings = {"btn1": {"event": ["<Button-1>", "<Shift-Button-1>"], 
                         "function": [btn1, btn1_shift]}}
    
    bs = ButtonSet(root, 
                   ["btn1", "btn2", "btn3", "btn4", 
                    "btn5", "btn6", "btn7", "btn8"], 
                   ["btn1", "btn2", "btn3", "btn4", 
                    "btn5", "btn6", "btn7", "btn8"],
                   bindings = bindings,
                   layout = [[-1, 7, -1, 1, 2, 8],[6, 1, 2, 3, 4],[5]],
                   frame_kwargs = {"bg": "black"},
                   grid_kwargs = {"sticky" : "nesw"},
                   set_width = 70)
    
    # bs._check_layout(bs.layout)
    
    bs.get_frame().grid(row = 1, column = 1, **{"sticky" : "nesw"})
    root.rowconfigure(0, weight = 1)
    root.columnconfigure(0, weight = 1)
    root.rowconfigure(1, weight = 1)
    root.columnconfigure(1, weight = 1)
    root.rowconfigure(2, weight = 1)
    root.columnconfigure(2, weight = 1)
    root.mainloop()

    
