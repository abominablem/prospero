# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 23:03:46 2021

@author: marcu
"""

import tkinter as tk
import pydub
from datetime import datetime
from pydub.playback import play
from kthread import KThread
import config

class AudioInterface:
    def __init__(self, parent, master, trace = None):

        self.name = self.__class__.__name__
        self.parent = parent
        self.pr = parent.pr
        self.master = master

        self.pr.f._log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call",
                     "parent": self.name + ".__init__"}
        
        self.audio = None
        self.load_from_config(trace = inf_trace)
        
        """
        ### BUTTONS ###
        """
        self.frame = tk.Frame(self.master,
                              background = self.pr.c.colour_background)
        
        self.AudioControlsSpacer1_GridColumn = 0
        self.btnSkipToPrevious_GridColumn = self.AudioControlsSpacer1_GridColumn + 1
        self.btnRewind_GridColumn = self.btnSkipToPrevious_GridColumn + 1
        self.btnTogglePlayPause_GridColumn = self.btnRewind_GridColumn + 1
        self.btnFastForward_GridColumn = self.btnTogglePlayPause_GridColumn + 1
        self.btnSkipToNext_GridColumn = self.btnFastForward_GridColumn + 1
        self.AudioControlsSpacer2_GridColumn = self.btnSkipToNext_GridColumn + 1
        
        self.audio_button_standard_args = {
            "background" : self.pr.c.colour_interface_button,
            "font" : self.pr.c.font_prospero_interface_button
            }
                
        self.AudioControlsSpacer1 = tk.Label(
            self.frame,
            text="",
            bg = self.pr.c.colour_background
            )
        self.btnSkipToPrevious = tk.Button(
            self.frame,
            text="⏮",
            command = self._btnSkipToPrevious_Click,
            **self.audio_button_standard_args
            )
        self.btnRewind = tk.Button(
            self.frame,
            text="⏪",
            command = self._btnRewind_Click,
            **self.audio_button_standard_args
            )
        self.btnTogglePlayPause = tk.Button(
            self.frame,
            text="▶️",
            command = self._btnTogglePlayPause_Click,
            **self.audio_button_standard_args
            )
        self.btnFastForward = tk.Button(
            self.frame,
            text="⏩",
            command = self._btnFastForward_Click,
            **self.audio_button_standard_args
            )
        self.btnSkipToNext = tk.Button(
            self.frame,
            text="⏭",
            command = self._btnSkipToNext_Click,
            **self.audio_button_standard_args
            )
        self.AudioControlsSpacer2 = tk.Label(
            self.frame,
            text="",
            bg = self.pr.c.colour_background
            )

        self.AudioControlsSpacer1.grid(
            row = 0,
            column = self.AudioControlsSpacer1_GridColumn,
            sticky = "nesw"
            )
        self.btnSkipToPrevious.grid(
            row = 0,
            column = self.btnSkipToPrevious_GridColumn,
            sticky = "nesw"
            )
        self.btnRewind.grid(
            row = 0,
            column = self.btnRewind_GridColumn,
            sticky = "nesw"
            )
        self.btnTogglePlayPause.grid(
            row = 0,
            column = self.btnTogglePlayPause_GridColumn,
            sticky = "nesw"
            )
        self.btnFastForward.grid(
            row = 0,
            column = self.btnFastForward_GridColumn,
            sticky = "nesw"
            )
        self.btnSkipToNext.grid(
            row = 0,
            column = self.btnSkipToNext_GridColumn,
            sticky = "nesw"
            )
        self.AudioControlsSpacer2.grid(
            row = 0,
            column = self.AudioControlsSpacer2_GridColumn,
            sticky = "nesw"
            )
        
        """
        #######################################################################
        ################################ ALLOCATE SCALING #####################
        #######################################################################
        """
        
        self.frame.columnconfigure(self.AudioControlsSpacer1_GridColumn, 
                                   weight = 1)
        self.frame.columnconfigure(self.AudioControlsSpacer2_GridColumn, 
                                   weight = 1)

    def load_audio(self, audio, trace = None):
        """
        Takes one parameter of type pydub AudioSegment. Prepares audio for
        playback.
        """
        self.pr.f._log_trace(self, "load_audio", trace)
        
        self.audio = audio
        self.audio_length = len(audio)
        self.play_point = 0
        self.playing = False
        self.play_start_datetime = None
    
    def refresh_breakpoints(self, trace = None):
        """
        Refreshes the list of audio breakpoints. Includes the start and end of
        the audio.
        """
        self.pr.f._log_trace(self, "refresh_breakpoints", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".refresh_breakpoints"}
        self.breakpoints = self.parent._true_breakpoints(
            scale_to_sound = True, trace = inf_trace)
    
    def _btnSkipToPrevious_Click(self, trace = None):
        """
        Skip to last breakpoint before the current playback point.
        """
        self.pr.f._log_trace(self, "_btnSkipToPrevious_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + 
                         "._btnSkipToPrevious_Click"}
        
        if self.audio is None: return
        was_playing = self.playing
        
        if was_playing: self.end_audio_process(trace = inf_trace)
        
        self.set_play_point(trace = inf_trace)
        play_point = self.get_play_point(trace = inf_trace)
        breakpoint_range = self._get_breakpoint_index(play_point, 
                                                      trace = inf_trace)
        prev_brkpt = int(self.breakpoints[breakpoint_range[0]])
        
        #To ensure you don't get stuck on a breakpoint, utilise a grace period
        #where you will instead go to the breakpoint before
        if play_point - prev_brkpt < self.breakpoint_grace_period:
            breakpoint_range = self._get_breakpoint_index(play_point, 
                                                          trace = inf_trace)
            self.play_point = int(self.breakpoints[breakpoint_range[0]-1])
        else:
            self.play_point = int(self.breakpoints[breakpoint_range[0]])
            
        self.draw_progress_bar(trace = inf_trace)
        if was_playing: self._start_audio_process(trace = inf_trace)
        return
    
    def _btnRewind_Click(self, trace = None):
        """
        Moves the playback point back a pre-determined distance
        """
        self.pr.f._log_trace(self, "_btnRewind_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._btnRewind_Click"}
        if self.audio is None: return
        if not self.playing:
            self.set_play_point(offset = -1*self.rewind_milliseconds, 
                                trace = inf_trace)
            self.draw_progress_bar(trace = inf_trace)
        else:
            self.end_audio_process(trace = inf_trace)
            self.set_play_point(offset = -1*self.rewind_milliseconds, 
                                trace = inf_trace)
            self._start_audio_process(trace = inf_trace)
        return
    
    def _btnTogglePlayPause_Click(self, trace = None):
        """
        Start/end the audio playback process. Saves the progress of playback.
        """
        self.pr.f._log_trace(self, "_btnTogglePlayPause_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + 
                         "._btnTogglePlayPause_Click"}
        self.refresh_breakpoints(trace = inf_trace)
        
        #Exit if no audio is loaded
        if self.audio is None:
            return
        
        # Update the icon
        if self.btnTogglePlayPause['text'] == "⏸":
            self.playing = False
            self.btnTogglePlayPause['text'] = "▶️"
            if not self.audio_process is None:
                self.set_play_point(offset = 0, trace = inf_trace)
                self.end_audio_process(trace = inf_trace)
        else:
            self.btnTogglePlayPause['text'] = "⏸"
            if self.play_point >= self.breakpoints[-1]:
                self.play_point = self.breakpoints[0]
            if not self.playing:
                self._start_audio_process(trace = inf_trace)
            
        self.draw_progress_bar(trace = inf_trace)
        return
        
    def _btnFastForward_Click(self, trace = None):
        """
        Moves the playback point forward a pre-determined distance
        """
        self.pr.f._log_trace(self, "_btnFastForward_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + 
                         "._btnFastForward_Click"}
        if self.audio is None: return
        if not self.playing:
            self.set_play_point(offset = self.fast_forward_milliseconds, 
                                trace = inf_trace)
            self.draw_progress_bar(trace = inf_trace)
        else:
            self.end_audio_process(trace = inf_trace)
            self.set_play_point(offset = self.fast_forward_milliseconds, 
                                trace = inf_trace)
            self._start_audio_process(trace = inf_trace)
        return
    
    def _btnSkipToNext_Click(self, trace = None):
        """
        Skip to next breakpoint after the current playback point.
        """
        self.pr.f._log_trace(self, "_btnSkipToNext_Click", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + 
                         "._btnSkipToNext_Click"}
        if self.audio is None or not self.playing: return
        
        self.end_audio_process(trace = inf_trace)
        self.set_play_point(trace = inf_trace)
        breakpoint_range = self._get_breakpoint_index(
            self.get_play_point(trace = inf_trace), trace = inf_trace
            )
        self.play_point = int(self.breakpoints[breakpoint_range[1]])
        self._start_audio_process(trace = inf_trace)
        return
    
    def _start_audio_process(self, trace = None):
        """
        Start a new audio playback thread at the current playpoint
        """
        self.pr.f._log_trace(self, "_create_audio_process", trace)
        #create killable thread since tkinter does not play well with
        #multiprocessing
        self.playing = True
        self.btnTogglePlayPause['text'] = "⏸"
        self.audio_process = KThread(target = self.play_audio)
        self.audio_process.daemon = True
        
        #set time of playback start
        self.play_start_datetime = datetime.now()
        self.audio_process.start()
    
    def end_audio_process(self, trace = None):
        """
        End the current audio playback thread
        """
        self.pr.f._log_trace(self, "end_audio_process", trace)
        
        self.playing = False
        self.btnTogglePlayPause['text'] = "▶️"
        try:
            self.audio_process.kill()
        except AttributeError:
            pass
        
    def play_audio(self, trace = None):
        self.pr.f._log_trace(self, "play_audio", trace, 
                             add = "Started playing audio at play_point %d"
                             % self.play_point)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".play_audio"}
        
        #pydub.playback.play
        play(self.audio[self.get_play_point():])
        #toggle back to paused mode when track finishes
        #this does not run if the thread is ended early e.g. through pausing
        #or skipping around
        self._btnTogglePlayPause_Click(trace = inf_trace)
        self.play_point = 0
        
    def get_play_point(self, trace = None):
        """
        Returns the currently stored playpoint, within the bounds of the audio.
        """
        self.pr.f._log_trace(self, "get_play_point", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".get_play_point"}
        self.refresh_breakpoints(trace = inf_trace)
        self.play_point = max(self.breakpoints[0], self.play_point)
        self.play_point = min(self.breakpoints[-1], self.play_point)
        return self.play_point
    
    def set_play_point(self, offset = 0, trace = None):
        """
        Update the playpoint based on time elapsed since playback was started.
        Optionally provide an offset for e.g. fast forward/rewinding.
        """
        self.pr.f._log_trace(self, "set_play_point", trace)
        #calculate the new starting point for playing next time
        #based on elapsed time since starting playback
        if self.play_start_datetime is None: return #new waveform being loaded
        self.play_point += int((datetime.now() - self.play_start_datetime
                                ).total_seconds()*1000)
        self.play_start_datetime = datetime.now()
        self.play_point += offset
        self.play_point = int(self.play_point)
    
    def _get_breakpoint_index(self, num, trace = None):
        """
        Provides the index of the breakpoints to either side of the play point
        num, based on the list self.breakpoints.
        """
        self.pr.f._log_trace(self, "_get_breakpoint_index", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + "._get_breakpoint_index"}
        
        self.refresh_breakpoints(trace = inf_trace)
        num_breakpoints = len(self.breakpoints)
        
        for k in range(num_breakpoints - 1):
            if num >= self.breakpoints[k] and num <= self.breakpoints[k+1]:
                return (k, k+1)
        
        #if num is outside of the allowed range
        if num > self.breakpoints[-1]:
            return (num_breakpoints, num_breakpoints)
        else:
            return (0, 0)
    
    def draw_progress_bar(self, trace = None):
        """
        Draw the playback progress bar on the audio waveform, auto-updating
        after a defined period.
        """
        self.pr.f._log_trace(self, "draw_progress_bar", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".draw_progress_bar"}
        
        self.set_play_point(offset = 0, trace = inf_trace)
        self.parent.draw_playback_progress_bar(
            self.get_play_point(trace = inf_trace), trace = inf_trace)
        if not self.playing: return
        
        #loop while the audio is playing (ms refresh time)
        self.tab.after(1000, lambda: self.draw_progress_bar(trace=inf_trace))

    def grid(self, trace = None, **kwargs):
        self.pr.f._log_trace(self, "grid", trace)
        self.frame.grid(**kwargs)

    def load_from_config(self, trace = None):
        self.pr.f._log_trace(self, "load_from_config", trace)
        self.rewind_milliseconds = config.config.config_dict["AudioFunctions"]["AudioInterface"]["rewind_seconds"]*1000
        self.fast_forward_milliseconds = config.config.config_dict["AudioFunctions"]["AudioInterface"]["fast_forward_seconds"]*1000
        self.breakpoint_grace_period = config.config.config_dict["AudioFunctions"]["AudioInterface"]["breakpoint_grace_period"]*1000