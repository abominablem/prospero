# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 22:13:21 2021

@author: marcu
"""

from PIL import Image, ImageTk

class Resources:
    def __init__(self, parent, trace = None):
        self.pr = parent.pr
        
        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", "parent": self.__class__.__name__ + ".__init__"}
        
        #errors cause the image import to fail until the kernel is restarted. For simplicity while testing, disable the logo
        with Image.open("..\Icon\Wave icon (full circle, quarter size, transparent).png") as image:
            self.logo_circular_small = ImageTk.PhotoImage(image.resize((100, 100)))
        
        with Image.open("..\Icon\Wave icon (full circle, quarter size, transparent).png") as image:
            self.logo_circular_small_padded = ImageTk.PhotoImage(self.pr.f.pad_image_with_transparency(image = image.resize((85, 85)), pixels = self.pr.c.padding_medium, keep_size = False, trace = inf_trace))
            
        with Image.open("..\Icon\settings_cog.png") as image:
            self.icon_settings_image = ImageTk.PhotoImage(self.pr.f.pad_image_with_transparency(image = image.resize((85, 85)), pixels = self.pr.c.padding_medium, keep_size = False, trace = inf_trace))