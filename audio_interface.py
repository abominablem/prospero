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
from arrange_widgets import WidgetSet
from mh_logging import log_class

class ProgressBar:
    @log_class
    def __init__(self, figure, draw_func, sound_scale = 1):
        self.figure = figure
        self.draw_func = draw_func
        self.sound_scale = sound_scale
        self.playpoint = 0
        self.line  = None

    @log_class
    def draw(self, x):
        x = x/self.sound_scale
        if self.line is None:
            self.line = self.figure.axvline(x = x, color = "red")
        else:
            self.line.set_xdata([x, x])
        self.draw_func()

    @log_class
    def remove(self):
        if not self.line is None:
            self.line.remove()
            self.line = None

def audio_function(func):
    """
    Decorator for functions which should not be run if self.audio is None
    """
    def _func_with_play_check(self, *args, **kwargs):
        if self.audio is None: return
        return func(self, *args, **kwargs)
    return _func_with_play_check

class AudioInterface:
    @log_class
    def __init__(self, parent, master, audio_canvas):
        self.name = self.__class__.__name__
        self.pr = parent.pr
        self.master = master
        self.audio_canvas = audio_canvas
        self.audio_breakpoints = audio_canvas.breakpoints
        self.progress_bar = None

        self.audio = None
        self.load_from_config()

        """
        ### BUTTONS ###
        """
        self.frame = tk.Frame(self.master,
                              background = self.pr.c.colour_background)

        self.audio_button_standard_args = {
            "background" : self.pr.c.colour_interface_button,
            "font" : self.pr.c.font_prospero_interface_button
            }

        self.btn_skip_to_previous = tk.Button(
            self.frame,
            text="⏮",
            command = self._btn_skip_to_previous_click,
            **self.audio_button_standard_args
            )
        self.btn_rewind = tk.Button(
            self.frame,
            text="⏪",
            command = self._btn_rewind_click,
            **self.audio_button_standard_args
            )
        self.btn_toggle_play_pause = tk.Button(
            self.frame,
            text="▶️",
            command = self._btn_toggle_play_pause_click,
            **self.audio_button_standard_args
            )
        self.btn_fast_forward = tk.Button(
            self.frame,
            text="⏩",
            command = self._btn_fast_forward_click,
            **self.audio_button_standard_args
            )
        self.btn_skip_to_next = tk.Button(
            self.frame,
            text="⏭",
            command = self._btn_skip_to_next_click,
            **self.audio_button_standard_args
            )

        widgets = {1: {'widget': self.btn_skip_to_previous,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   2: {'widget': self.btn_rewind,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   3: {'widget': self.btn_toggle_play_pause,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   4: {'widget': self.btn_fast_forward,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   5: {'widget': self.btn_skip_to_next,
                       'grid_kwargs': self.pr.c.grid_sticky},
                   -1: {'grid_kwargs': self.pr.c.grid_sticky_padding_small,
                        'widget_kwargs': {'bg': self.pr.c.colour_background,
                                          'text': ""},
                       'stretch_width': True},
                   }

        self.widget_set = WidgetSet(
            self.frame, widgets, layout = [[-1, 1, 2, 3, 4, 5, -1]])

    @log_class
    def load_audio(self, audio):
        """
        Take one parameter of type pydub AudioSegment. Prepare audio for
        playback.
        """
        self.audio = audio
        self.audio_length = len(audio)
        self.play_point = 0
        self.playing = False
        self.play_start_datetime = None

        if not self.progress_bar is None:
            self.progress_bar.remove()

        self.progress_bar = ProgressBar(
            self.audio_canvas.figure,
            self.audio_canvas.draw,
            self.audio_canvas.get_scale()
            )

    @log_class
    def refresh_breakpoints(self):
        """
        Refreshes the list of audio breakpoints. Includes the start and end of
        the audio.
        """
        self.breakpoints = self.audio_breakpoints.true_breakpoints(
            scale_to_sound = True)

    @log_class
    @audio_function
    def _btn_skip_to_previous_click(self):
        """
        Skip to last breakpoint before the current playback point.
        """
        was_playing = self.playing

        if was_playing: self.end_audio_process()

        self.set_play_point()
        play_point = self.get_play_point()
        breakpoint_range = self._get_breakpoint_index(play_point,
                                                      )
        prev_brkpt = int(self.breakpoints[breakpoint_range[0]])

        #To ensure you don't get stuck on a breakpoint, utilise a grace period
        #where you will instead go to the breakpoint before
        if play_point - prev_brkpt < self.breakpoint_grace_period:
            breakpoint_range = self._get_breakpoint_index(play_point,
                                                          )
            self.play_point = int(self.breakpoints[breakpoint_range[0]-1])
        else:
            self.play_point = int(self.breakpoints[breakpoint_range[0]])

        self.draw_progress_bar()
        if was_playing: self._start_audio_process()
        return

    @log_class
    @audio_function
    def _btn_rewind_click(self):
        """
        Moves the playback point back a pre-determined distance
        """
        if not self.playing:
            self.set_play_point(offset = -1*self.rewind_milliseconds,
                                )
            self.draw_progress_bar()
        else:
            self.end_audio_process()
            self.set_play_point(offset = -1*self.rewind_milliseconds,
                                )
            self._start_audio_process()
        return

    @log_class
    @audio_function
    def _btn_toggle_play_pause_click(self):
        """
        Start/end the audio playback process. Saves the progress of playback.
        """
        self.refresh_breakpoints()

        # Update the icon
        if self.btn_toggle_play_pause['text'] == "⏸":
            self.playing = False
            self.btn_toggle_play_pause['text'] = "▶️"
            if not self.audio_process is None:
                self.set_play_point(offset = 0, )
                self.end_audio_process()
        else:
            self.btn_toggle_play_pause['text'] = "⏸"
            if self.play_point >= self.breakpoints[-1]:
                self.play_point = self.breakpoints[0]
            if not self.playing:
                self._start_audio_process()

        self.draw_progress_bar()
        return

    @log_class
    @audio_function
    def _btn_fast_forward_click(self):
        """
        Moves the playback point forward a pre-determined distance
        """
        if not self.playing:
            self.set_play_point(offset = self.fast_forward_milliseconds)
            self.draw_progress_bar()
        else:
            self.end_audio_process()
            self.set_play_point(offset = self.fast_forward_milliseconds)
            self._start_audio_process()
        return

    @log_class
    @audio_function
    def _btn_skip_to_next_click(self):
        """
        Skip to next breakpoint after the current playback point.
        """
        self.end_audio_process()
        self.set_play_point()
        breakpoint_range = self._get_breakpoint_index(
            self.get_play_point(),
            )
        self.play_point = int(self.breakpoints[breakpoint_range[1]])
        self._start_audio_process()
        return

    @log_class
    def _start_audio_process(self):
        """
        Start a new audio playback thread at the current playpoint
        """
        # create killable thread since tkinter does not play well with
        # multiprocessing
        self.playing = True
        self.btn_toggle_play_pause['text'] = "⏸"
        self.audio_process = KThread(target = self.play_audio)
        self.audio_process.daemon = True

        # set time of playback start
        self.play_start_datetime = datetime.now()
        self.audio_process.start()

    @log_class
    def end_audio_process(self):
        """
        End the current audio playback thread
        """
        self.playing = False
        self.btn_toggle_play_pause['text'] = "▶️"
        try:
            self.audio_process.kill()
        except AttributeError:
            pass

    @log_class
    def play_audio(self):
        # pydub.playback.play
        play(self.audio[self.get_play_point():])
        # toggle back to paused mode when track finishes
        # this does not run if the thread is ended early e.g. through pausing
        # or skipping around
        self._btn_toggle_play_pause_click()
        self.play_point = 0

    @log_class
    def get_play_point(self):
        """
        Returns the currently stored playpoint, within the bounds of the audio.
        """
        self.refresh_breakpoints()
        self.play_point = max(self.breakpoints[0], self.play_point)
        self.play_point = min(self.breakpoints[1], self.play_point)
        return self.play_point

    @log_class
    def set_play_point(self, offset = 0):
        """
        Update the playpoint based on time elapsed since playback was started.
        Optionally provide an offset for e.g. fast forward/rewinding.
        """
        # calculate the new starting point for playing next time
        # based on elapsed time since starting playback
        if self.play_start_datetime is None: return #new waveform being loaded
        self.play_point += int((datetime.now() - self.play_start_datetime
                                ).total_seconds()*1000)
        self.play_start_datetime = datetime.now()
        self.play_point += offset
        self.play_point = int(self.play_point)

    @log_class
    def _get_breakpoint_index(self, num):
        """
        Provides the index of the breakpoints to either side of the play point
        num, based on the list self.breakpoints.
        """
        self.refresh_breakpoints()
        num_breakpoints = len(self.breakpoints)

        for k in range(num_breakpoints - 1):
            if num >= self.breakpoints[k] and num <= self.breakpoints[k+1]:
                return (k, k+1)

        # if num is outside of the allowed range
        if num > self.breakpoints[-1]:
            return (num_breakpoints, num_breakpoints)
        else:
            return (0, 0)

    @log_class
    def draw_progress_bar(self, freq = 1000):
        """
        Draw the playback progress bar on the audio waveform, auto-updating
        after a defined period in ms.
        """
        self.set_play_point(offset = 0)
        if self.progress_bar is not None:
            self.progress_bar.draw(self.get_play_point())
        if not self.playing: return

        # loop while the audio is playing (ms refresh time)
        self.master.after(freq,lambda: self.draw_progress_bar())

    @log_class
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    @log_class
    def load_from_config(self):
        self.rewind_milliseconds = config.config.config_dict["AudioFunctions"]["AudioInterface"]["rewind_seconds"]*1000
        self.fast_forward_milliseconds = config.config.config_dict["AudioFunctions"]["AudioInterface"]["fast_forward_seconds"]*1000
        self.breakpoint_grace_period = config.config.config_dict["AudioFunctions"]["AudioInterface"]["breakpoint_grace_period"]*1000