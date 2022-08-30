# @description ReaSamplOmatic5000 multi
# @version 1.3
# @author maxim
# @about
#   ## ReaSamploMatic5000 multi
#   A REAPER script for arranging multiple ReaSamplOmatic5000
#   instances on a piano roll, made using reapy and tkinter.
#   For detailed instructions, consult the
#   [readme](https://github.com/maximvdberg/reasamplomatic-multi).
#   Some configuration options are available, see the script
#   for more information.
# @links
#   GitHub repository https://github.com/maximvdberg/reasamplomatic-multi
# @provides 
#   [main] .
#   [main] reasamplomatic_multi_enable_reapy.py
#   [main] reasamplomatic_multi_detect_pitch.lua
# @screenshot
#   Window https://imgur.com/iUySLMr
# @changelog
#   Added reapy enable script
#   Fixed keybindings on MacOS
#   Fixed colors on MacOS


import reapy as rp
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

try:
    import tkinterdnd2
    dnd_available = True
    print("Drag-and-drop available")
except:
    print("Install tkinterdnd2 for drag-and-drop support.")
    dnd_available = False

try:
    from tktooltip import ToolTip
    tooltip_available = True
    print("Tooltips available")
except:
    print("Install tkinter-tooltip for drag-and-drop support.")
    tooltip_available = False

import webbrowser
import subprocess
import traceback
import random
import socket
import pickle
import queue
import time
import math
import sys
import os
import re

# Configuration options - Defaults (changeable in GUI)
width_per_note = 20            # Width in pixels of the notes.
piano_roll_height = 60         # Height in pixels of the piano roll.

create_pitched = 0             # When adding new note ranges, make them pitched: Set mode to
                               # `Note (semitone shifted) and `Obey note-offs` to `True`.
create_bus_on_separate = 1     # Whether to create a bus channel on separate.
separate_overlap = 1           # Whether to separate overlapping samples into different groups
name_by_general_midi = 0       # Whether to automatically name sample ranges by their position,
                               # following the general midi drumkit standard.
default_note_start = 36        # Default note to add an instance onto (default is C2).

allow_reaper_drag_and_drop = 0 # Since drag-and-dropping anything from REAPER freezes REAPER,
                               # communication with reapy will fail. This can be circumvented
                               # by disabling reapy communication when (possibly) doing drag and
                               # drop. Setting this to 1 will allow drag and drop from REAPER,
                               # but will only switch tracks when selecting the multi-sampler.
                               # A more elegant solution is W.I.P.

sync_with_reaper = 1           # If this is turned off, no automatic syncing is done with REAPER
                               # anymore. To reflect changes done in REAPER you need to manually
                               # use the `refresh' action.

default_multisampler_name = "Multi-Sampler" # Name of the created multi-sampler track.
default_fx_name = "ReaSamplOmatic5000"      # Default name of the FX instances.

# Configuration options - Functionality
resize_handle_width = 15        # The size of the resize handles in pixels.
resize_handle_ratio_small = 1/3 # When the range size is smaller than trice
                                # the handle size, use this ratio instead.

scroll_speed = 1                 # Speed to scroll.
zoom_speed = 1                   # Speed to zoom.
default_window_size = '1000x400' # Default window size in pixels.
max_recursion_depth = 10         # Max. depth to look for ReaSamplOmatics in send tracks
                                 # of the selected track.
tooltip_delay = 1.0              # Amount of seconds it takes for tooltips to show up.

# Configuration options - Appearance
highlight = 1            # Thickness of the highlights. Set to 0 for a "flat" look.
alpha = 0.7              # Alpha of the track colors.
                         # 0.2 looks nice with a dark background.
alpha_selected = 1       # Alpha of track when it is selected.
                         # Make sure it is different from alpha
text_color = '#F0F0F0'          # Text color of the sample ranges.
text_color_selected = '#404040' # Text color when the sample range is selected.
background_color = "#202020"    # Background color.
foreground_color = "#F0F0F0"    # Foreground color.
                                # Interchange the colors for light theme.
highlight_color = "#e0e0e0"     # Color of the highlights

solo_prefix = "[S] "  # Text indicators for solo and mute.
mute_prefix = "[M] "
name_by_general_midi_nocaps = 1  # Whether to capitalize the general MIDI note names.
default_color = "#77ff77"        # Color to use when parsing a track with the default color.

# Configuration options - Defaults in REAPER/SamplOmatic5000.
gain_for_minimum_velocity = 0.03162277489900589 # "Min vol" in REAPER.
                                                # Necessary for dynamics.


# Configuration options - Keybinds
keys_add = ['a']
keys_refresh = ['r']
keys_separate = ['g']
keys_scroll_center = ['z']
keys_close_ui = ['c']
keys_undo = ['Control-z']
keys_redo = ['Control-Z']

# Options
keys_freeze = ['f']
keys_stay_on_top = ['t']
keys_dnd_reaper = ['q']
keys_sync = []
keys_pitched = ['w']
keys_name_by_midi = []
keys_create_bus = []
keys_separate_overlap = ['e']

# Copy, paste and delete bindings
keys_copy = ['Control-c', 'y']
keys_paste = ['Control-v', 'p']
keys_delete = ['Delete', 'd']
keys_select_all = ['Control-a']

# Solo/mute bindings
keys_solo_toggle = ['m']
keys_unsolo_all = ['M']
keys_mute_toggle = ['s']
keys_unmute_all = ['S']
keys_reset_solo_and_mute = ['x']

# Param copy/paste bindings
keys_params_sample_copy = ['b']
keys_params_note_copy = ['B']
keys_params_paste = ['n']


# Some global variables
general_midi_drumkit = {
        27: "High Q", 28: "Slap", 29: "Scratch Push", 30: "Scratch Pull",
        31: "Sticks", 32: "Square Click", 33: "Metronome Click",
        34: "Metronome Bell", 35: "Bass Drum alt", 36: "Bass Drum",
        37: "Side Stick", 38: "Snare Drum", 39: "Hand Clap",
        40: "Snare Drum alt", 41: "Low Tom alt", 42: "Closed Hi-hat",
        43: "Low Tom", 44: "Pedal Hi-hat", 45: "Mid Tom alt",
        46: "Open Hi-hat", 47: "Mid Tom", 48: "High Tom alt",
        49: "Crash Cymbal", 50: "High Tom", 51: "Ride Cymbal",
        52: "Chinese Cymbal", 53: "Ride Bell", 54: "Tambourine",
        55: "Splash Cymbal", 56: "Cowbell", 57: "Crash Cymbal alt",
        58: "Vibra Slap", 59: "Ride Cymbal alt", 60: "High Bongo",
        61: "Low Bongo", 62: "Mute High Conga", 63: "Open High Conga",
        64: "Low Conga", 65: "High Timbale", 66: "Low Timbale",
        67: "High Agogo", 68: "Low Agogo", 69: "Cabasa", 70: "Maracas",
        71: "Short Whistle", 72: "Long Whistle", 73: "Short Guiro",
        74: "Long Guiro", 75: "Claves", 76: "High Wood Block",
        77: "Low Wood Block", 78: "Mute Cuica", 79: "Open Cuica",
        80: "Mute Triangle", 81: "Open Triangle", 82: "Shaker",
        83: "Jingle Bell", 84: "Belltree", 85: "Castanets",
        86: "Mute Surdo", 87: "Open Surdo"
    }
freeze = False
stay_on_top = True
running = True
current_track = None
current_track_routing = None
samploranges = []
last_touched = None
root = None
root = None
scrollbar = None
canvas = None
window = None
pianoroll_frame = None
pixel = None
track_name_text = None
track_name_label = None
render_groups = []
adjust_for_highlight = 2
right_click_menu = None
internal_script_active = False
on_macOS = False

# Constants
total_notes = 128

def rgb(rgb, a = 1):
    return "#%02x%02x%02x" % (int(rgb[0]*a), int(rgb[1]*a), int(rgb[2]*a))

def rgb2tuple(t):
    return (eval(f"0x{t[1:3]}"), eval(f"0x{t[3:5]}"), eval(f"0x{t[5:7]}"))

# The main note range class.
class SamploRange():
    def __init__(self, window, fx, color=(255, 255, 255), note_start=-1, note_end=-1, name=None):
        self.window = window
        self.max_height = -1
        self.fx = fx

        if fx:
            with rp.inside_reaper():
                self.index = fx.index
                self.start = round(fx.params["Note range start"] * 127)
                self.end = round(fx.params["Note range end"] * 127)
                self.mute = not fx.is_enabled
        else:
            self.index = -1
            self.start = note_start
            self.end = note_end
            self.mute = False
        self.solo = False

        # Filename (only used for drag-and-drop functionality)
        self.filename = None

        # Create the moveable widget.
        global alpha
        font = tkfont.Font(size=8)
        self.color = color if color != (0, 0, 0) else rgb2tuple(default_color)
        self.widget = tk.Canvas(self.window,
                                highlightthickness=highlight,
                                highlightbackground=rgb(self.color),
                                bg=rgb(self.color, alpha),
                                bd=0)
        self.widget.bind("<B1-Motion>", self.mouse)
        self.widget.bind("<ButtonRelease-1>", self.button_release)
        self.widget.bind("<Motion>", self.motion)
        self.widget.bind('<Double-Button-1>', lambda e: self.show(True))
        self.widget.bind('<Alt-1>' if not on_macOS else '<Option-1>', lambda e: self.set_alt())
        self.widget.bind('<Button-1>', lambda e: self.select())
        self.widget.bind('<Control-1>', lambda e: self.select(True))

        self.tooltip = None
        if tooltip_available:
            self.tooltip = ToolTip(self.widget, delay=tooltip_delay,
                    msg=f"Drag to move.\n"
                         "Drag edges to resize.\n"
                         "Alt+drag to stretch.\n\n"
                         "Click to open UI\n"
                         "Ctrl+click to add to\nselection.")

        # Selection.
        self.selected = False
        self.select_multiple = False

        # Text.
        self.text_hor = None
        self.text_ver = None
        self.current_name = name
        self.changed_name = False

        # Render group information.
        self.render_group = None
        self.layer_count = 1
        self.layer = 0

        # Track routing
        self.track_routing = None

        self.redraw()

        self.mouse_start_x = 0
        self.mouse_start_y = 0
        self.mouse_current_x = 0
        self.mouse_current_y = 0

        self.in_motion = False
        self.resize_side = 0
        self.resize_start = 0
        self.resize_end = 0
        self.alt = False

        self.prev_amount = -1000
        self.keep_ui_state = 0

    # # Drawing # #
    def redraw(self):
        # Position and sizes.
        width = int(width_per_note * (self.end - self.start + 1))
        self.max_height = int(window.winfo_height() - piano_roll_height)
        height = self.max_height // self.layer_count

        x_pos = int(width_per_note * self.start)
        y_pos = self.layer * height

        # The last layer should be a bit larger, when
        # `layer_count` does not divide `max_height`.
        if self.layer == self.layer_count - 1:
            height += self.max_height - self.layer_count * height

        # Adjust for the highlight offsets.
        width -= adjust_for_highlight * highlight
        height -= adjust_for_highlight * highlight

        # Drawing.
        self.widget.place(x=x_pos, y=y_pos)
        self.widget.configure(width=width, height=height)

        self.draw_name()
        self.draw_color()

    def draw_color(self):
        # Main color.
        if self.mute and not self.solo:
            color = (70, 70, 70)
        else:
            color = self.color if self.color != (0, 0, 0) else rgb2tuple(default_color)
        if self.selected:
            color_hex = rgb(color, alpha_selected)
        else:
            color_hex = rgb(color, alpha)

        # Highlight color
        if self.solo:
            hightlight_hex = rgb((240,240,240))
        elif self.selected:
            hightlight_hex = rgb(color, 0.5)
        else:
            hightlight_hex = rgb(color)

        # Text color:
        if not self.solo and self.mute:
            text_hex = text_color
        elif self.selected:
            text_hex = text_color_selected
        else:
            text_hex = text_color

        self.widget.configure(highlightbackground=hightlight_hex,
                              bg=color_hex)
        self.widget.itemconfig(self.text_hor, fill=text_hex)
        self.widget.itemconfig(self.text_ver, fill=text_hex)

    def get_name(self):
        global name_by_general_midi
        if name_by_general_midi.get():
            if self.start in general_midi_drumkit:
                name = general_midi_drumkit[self.start]
            else:
                name = default_fx_name
            if name_by_general_midi_nocaps:
                name = name.lower()
            if self.layer_count > 1:
                name += f" {self.layer+1}"
        elif self.current_name:
            name = self.current_name
        elif self.fx:
            name = self.fx.name
        else:
            name = default_fx_name

        # Add solo / mute indicators.
        if name.startswith(solo_prefix):
            name = name[len(solo_prefix):]
        if name.startswith(mute_prefix):
            self.widget.itemconfig(self.text_hor, text=name)
            name = name[len(mute_prefix):]
        if self.solo:
            name = solo_prefix + name
        elif self.mute:
            name = mute_prefix + name

        return name


    def draw_name(self):
        offscreen = -50
        name = self.get_name()

        # Initialise the text.
        if not self.text_hor:
            global text_color
            self.text_hor = self.widget.create_text(1, 0, text=name,
                    anchor="nw", fill=text_color)
            self.text_ver = self.widget.create_text(offscreen, 0, text=name,
                    anchor="nw", angle=90, fill=text_color)
            self.current_name = name

        # Update name if necessary.
        if self.current_name != name:
            self.widget.itemconfig(self.text_hor, text=name)
            self.widget.itemconfig(self.text_ver, text=name)
            self.current_name = name
            self.changed_name = True

        # Compute the bounding box.
        box = self.widget.bbox(self.text_hor)
        text_length = box[2] - box[0]
        text_height = box[1] - box[3]
        width = int(width_per_note * (self.end - self.start + 1))

        if text_length + 5 > width:
            # Place text vertically.
            self.widget.moveto(self.text_hor, 0, offscreen)

            # Make sure it aligns to the bottom if the text does not fit.
            pos_adjust = min(0, self.widget.winfo_reqheight() - text_length)
            if not pos_adjust:
                self.widget.moveto(self.text_ver, 0, 2)
            else:
                self.widget.moveto(self.text_ver, 0, pos_adjust - 2)
        else:
            # Place text horizontally.
            self.widget.moveto(self.text_hor, 3, 0)
            self.widget.moveto(self.text_ver, offscreen, 0)

    # # Event Handlers # #

    def set_alt(self):
        self.alt = True

    # On (double) click, show ui window.
    def show(self, exclusive=False):
        global samploranges

        if not self.fx:
            return

        with rp.inside_reaper():
            if exclusive:
                for samplorange in samploranges:
                    if not samplorange.fx.parent == self.fx.parent:
                        samplorange.fx.close_ui()
            else:
                self.fx.open_ui()

    def select(self, keep_selection=False, retrigger=True):
        if not self.select_multiple and not keep_selection:
            deselect_all()
        if keep_selection:
            global last_touched
            if last_touched:
                last_touched.select_multiple = True
            self.select_multiple = True

        if retrigger and keep_selection and self.selected:
            self.selected = False
        else:
            self.selected = True

        self.redraw()

        # Necessary on some systems to close the popup menu.
        popup_close()

    def deselect(self):
        self.selected = False
        self.select_multiple = False
        self.draw_color()

    # Mouse motion, saves x and y position of the cursor.
    def motion(self, event):
        self.mouse_current_x = event.x
        self.mouse_current_y = event.y

    # On button release, reset moving/resizing parameters, and update
    # REAPER. Also set this instance to the last touched range.
    def button_release(self, event=None):
        if event and not self.in_motion:
            self.show()

        root.config(cursor="arrow")

        self.in_motion = False
        self.resize_side = 0
        root.after(10, self.update_reaper)
        prev_amount = -1000
        self.alt = False


        # Forward the changes to the other instances of the selected group.
        # (Only the original receives the event)
        if event:
            if self.select_multiple:
                global samploranges
                for srange in samploranges:
                    if srange != self and srange.selected:
                        srange.button_release()

        global last_touched
        last_touched = self

    # Helper function to get event info.
    def event_info(self, event):
        c = event.widget
        x, y = c.winfo_x(), c.winfo_y()
        w, h = c.winfo_width(), c.winfo_height()
        x_add, y_add = event.x, event.y
        x_max, y_max = self.window.winfo_width(), self.window.winfo_height()
        return c, x, y, w, h, x_add, y_add, x_max, y_max

    # Handler for mouse click and drag. Depending on location, calls
    # resize or move.
    def mouse(self, event):
        c, x, y, w, h, x_add, y_add, x_max, y_max = self.event_info(event)

        if not self.in_motion:
            self.in_motion = True
            self.mouse_start_x = self.mouse_current_x
            self.mouse_start_y = self.mouse_current_y
            self.resize_start = self.start
            self.resize_end = self.end

            # We need to set the resize begin values for all
            # sample ranges to make resizing with multiple
            # selections work properly.
            global samploranges
            for srange in samploranges:
                srange.resize_start = srange.start
                srange.resize_end = srange.end

            # Check if we are grabbing the resize handles.
            resize_width = resize_handle_width

            # For small note ranges, use a relative size.
            if w < 3 * resize_handle_width:
                resize_width = resize_handle_ratio_small * w

            if self.mouse_start_x >= w - resize_width:
                self.resize_side = 1
            elif self.mouse_start_x < resize_width:
                self.resize_side = -1

        if self.alt:
            try:
                root.config(cursor="sb_right_arrow")
            except:
                pass
            self.resize_alt(event)
        elif self.resize_side != 0:
            if self.resize_side < 0:
                try:
                    root.config(cursor="sb_left_arrow")
                except:
                    pass
            else:
                try:
                    root.config(cursor="sb_right_arrow")
                except:
                    pass
            self.resize(event)
        else:
            root.config(cursor="fleur")
            self.move(event)

    # # Resizing and moving # #

    def check_change(self, amount):
        global render_groups, name_by_general_midi

        if amount != self.prev_amount:
            move_through_groups(render_groups, self)
            if name_by_general_midi.get():
                self.draw_name()

        self.prev_amount = amount

    # Resize and move the selected note ranges such that
    # the do not overlap.
    def resize_alt(self, event):
        global samploranges
        selected = [s for s in samploranges if s.selected]

        if len(selected) == 0:
            selected = [self]

        selected.sort(key=lambda s: s.start)
        base = selected[0].resize_start * width_per_note
        base_note = base // width_per_note
        base_width = selected[0].end - selected[0].resize_start + 1

        # Find the scale such that
        cursor_pos = event.x + self.start * width_per_note
        cursor_pos_start = self.resize_start * width_per_note + self.mouse_current_x
        scale = (cursor_pos - base) / (cursor_pos_start - base)

        if scale <= 0:
            return

        for srange in selected:
            note_range = [(srange.resize_start - base_note) * scale + base_note,
                          (srange.resize_end + 1 - base_note) * scale + base_note]
            start = int(min(note_range))
            end = int(max(note_range) - 1)
            width = end - start

            if srange.start != start or srange.end != end:
                srange.move_value(start - srange.start)
                srange.resize_value(1, width - (srange.resize_end - srange.start))

    # Resize the note range, based on TKinter mouse event.
    def resize(self, event):
        c, x, y, w, h, x_add, y_add, x_max, y_max = self.event_info(event)

        resize_amount = 0

        if self.resize_side > 0:
            # Resize to the right
            x_new = event.x
            end_new = self.start + max(0, math.floor(x_new / width_per_note))
            resize_amount = end_new - self.resize_end
        else:
            # Resize to the left
            x_new = event.x + (self.start - self.resize_start) * width_per_note
            start_new = min(self.end - self.resize_start,
                            math.floor(x_new / width_per_note))
            resize_amount = start_new

        self.resize_value(self.resize_side, resize_amount)

        # Forward the changes to the other instances of the selected group.
        if self.select_multiple:
            global samploranges
            for srange in samploranges:
                if srange != self and srange.selected:
                    srange.resize_value(self.resize_side, resize_amount)


    # Move based on given amount.
    def resize_value(self, side, amount):
        # Move the block if resizing on the left.
        if side > 0:
            self.end = max(self.start, self.resize_end + amount)
        else:
            self.start = min(self.end, self.resize_start + amount)
            self.widget.place(x=self.start * width_per_note)

        # Redraw the size.
        self.width = int(width_per_note * (self.end - self.start + 1))
        self.widget.configure(width=self.width - adjust_for_highlight * highlight)

        self.check_change(amount)

    # Replace the widget to the correct place according to its
    # `start` and `end` values.
    def resize_place(self):
        self.widget.place(x=self.start * width_per_note)
        self.widget.configure(width=self.width - adjust_for_highlight * highlight)

    # Move the note range, based on TKinter mouse event.
    def move(self, event):
        c, x, y, w, h, x_add, y_add, x_max, y_max = self.event_info(event)

        x_new = x - self.mouse_current_x + event.x
        note_set = round(x_new / width_per_note)
        note_move = note_set - self.start
        self.move_value(note_move)

        # Forward the changes to the other instances of the selected group.
        if self.select_multiple:
            global samploranges
            for srange in samploranges:
                if srange != self and srange.selected:
                    srange.move_value(note_move)

    # Move based on given amount.
    def move_value(self, amount):
        # Determine the new note range
        note_diff = self.end - self.start
        self.start += amount
        self.end = self.start + note_diff

        # Redraw
        self.widget.place(x=self.start * width_per_note)

        self.check_change(amount)


    # # Solo/mute # #
    def set_mute(self, mute):
        self.mute = mute
        self.update_reaper_mute()
        self.redraw()

    def set_solo(self, solo):
        self.solo = solo
        self.update_reaper_mute()
        self.redraw()

    # # REAPER communication # #
    def update_reaper_mute(self):
        global samploranges

        if self.solo:
            self.fx.enable()
        else:
            if self.mute:
                self.fx.disable()
            else:
                self.fx.enable()

    @rp.inside_reaper()
    def update_reaper(self):
        if self.fx:
            if self.changed_name:
                name = self.current_name
                if name.startswith(solo_prefix):
                    name = name[len(solo_prefix):]
                elif name.startswith(mute_prefix):
                    name = name[len(mute_prefix):]
                set_fx_name(self.fx, name)
                self.changed_name = False

            with rp.undo_block('Multi-Sampler: update note range'):
                params = self.fx.params
                difference = self.start - params["Note range start"] * 127

                params["Note range start"] = self.start / 127
                params["Note range end"] = self.end / 127
                params["Pitch for start note"] += difference / 160

# # # Layered rendering. # # #

# The group class describes a selection of overlapping SamploRanges.
# It is used only for the `create_layers` functionality, which
# describes a way to render the SamploRanges without overlap.
class SamploGroup():
    def __init__(self):
        self.sranges = []
        self.start = float('inf')
        self.end = -float('inf')
        self.layers = None

    def add(self, srange):
        self.sranges.append(srange)
        self.start = min(self.start, srange.start)
        self.end = max(self.end, srange.end)

    def remove(self, srange):
        try:
            self.sranges.remove(srange)
        except:
            pass

        if len(self.sranges) > 0:
            self.start = min(x.start for x in self.sranges)
            self.end = max(x.end for x in self.sranges)

    # Determines valid subgroups in the group, and returns them.
    # Should always be called after `remove` has been called.
    def split(self):
        groups_split = []

        for srange in self.sranges:
            insert_in_groups(groups_split, srange, False)

        return groups_split

    def merge(self, group):
        self.sranges += group.sranges
        self.start = min(self.start, group.start)
        self.end = max(self.end, group.end)

    def intersect(self, srange):
        if srange.end < self.start:
            return False
        elif self.end < srange.start:
            return False
        return True

    def create_layers(self):
        self.layers = []

        self.sranges.sort(key=lambda x: x.start)
        group_todo = list(self.sranges)

        # Keep creating ranges until no ranges are left.
        while group_todo:
            layer = [group_todo[0]]
            group_todo = group_todo[1:]

            # Create a layer of non-overlapping (but as close together
            # as possible) closest ranges. And remove the added ranges
            # from the todo list.
            for srange in list(group_todo):
                if srange.start > layer[-1].end:
                    layer.append(srange)
                    group_todo.remove(srange)

            self.layers.append(layer)

    def get_layer(self, srange):
        for n, layer in enumerate(self.layers):
            if srange in layer:
                return n
        return -1

    def update_srange_layers(self):
        self.create_layers()
        for srange in self.sranges:
            srange.render_group = self
            srange.layer_count = len(self.layers)
            srange.layer = self.get_layer(srange)
            srange.redraw()


def insert_in_groups(groups, srange, update_srange=True):
    intersect = False

    # Try to insert into any of the existing groups.
    for group in groups:
        if group.intersect(srange):
            group.add(srange)
            intersect = True

            if update_srange:
                srange.render_group = group
            break

    # Create new group if necessary.
    if not intersect:
        group_new = SamploGroup()
        group_new.add(srange)
        groups.append(group_new)

        if update_srange:
            srange.render_group = group_new


# The logic for updating the groups after updating the position
# of the specified SamploRange. It has the following steps:
#  (1) First, the range is removed from the current group
#  (2) This potentially splits the group, which is done in the
#      first section.
#  (3) Then the range is reinserted.
#  (4) Finally, it merges all groups that overlap with the (new)
#      group of the range
def move_through_groups(groups, srange):
    if srange.render_group is None or srange.render_group in groups:
        print


    assert srange.render_group is None or srange.render_group in groups

    # Remove from the current group, split the group if necessary.
    if srange.render_group:
        srange.render_group.remove(srange)

        if len(srange.render_group.sranges) == 0:
            # Remove if the group is empty.
            groups.remove(srange.render_group)
        else:
            # Split into new groups if necessary.
            groups_split = srange.render_group.split()
            if len(groups_split) > 1:
                groups.remove(srange.render_group)
                groups += groups_split

                # Update the layer information in the sranges.
                for group in groups_split:
                    group.update_srange_layers()
            else:
                srange.render_group.update_srange_layers()

    srange.render_group = None

    # Insert into groups again.
    if not srange.render_group:
        insert_in_groups(groups, srange)

    assert srange.render_group != None

    # Merge groups if necessary.
    for group in list(groups):
        if group == srange.render_group:
            continue

        # Merge if the groups overlap.
        if group.intersect(srange.render_group):
            group.merge(srange.render_group)

            groups.remove(srange.render_group)

            # Update all references.
            for s in srange.render_group.sranges:
                s.render_group = group

    # Update the layer information in the sranges.
    srange.render_group.update_srange_layers()


# # # Setup functions # # #

# Helper function for below. Find the location in the chunk
# corresponding to the given FX. Start search at `loc`.
def find_fx_in_chunk(chunk, fx):
    loc = chunk.find('<FXCHAIN')

    # Go through the FX until arriving at the correct one.
    for _ in range(fx.index + 1):
        loc = chunk.find('\nBYPASS ', loc + 1)
    return loc

fx_mode_sample_data = "AAAAAAAAAPA/AAAAAAAA4D8AAAAAAADwPwAAAAAAAAAA" \
                      "AAAAAAAA8D+amZmZmZmxP83MzMzMzOs/AAAAAAAAAAAc" \
                      "x3Ecx3HcP/yp8dJNYkA//Knx0k1iQD8AAAAAAAAAAAAA" \
                      "AAAAAAAAAAAAAAAAAAAAAAAAAADwPwAAAAAAAOA/AQAA" \
                      "AAAAAAAAAAAAAAAAAAAA8D9AAAAAVVVVVVVVxT//////" \
                      "CAQCgUAggD8AAAAAAADwPwAAAAAAAPA/AAAAAAAAAAAA" \
                      "AAAAAAAAAAAAAAAA"

fx_mode_note_data = "AAAAAAAAAPA/AAAAAAAA4D8AAAAAAADwPwAAAAAAAAAAAAAAA" \
                    "AAA8D+amZmZmZmxP83MzMzMzOs/AAAAAAAAAAAcx3Ecx3HcP/" \
                    "yp8dJNYkA//Knx0k1iQD8AAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
                    "AAAAAAAAAAADwPwAAAAAAAOA/AgAAAAAAAAAAAAAAAAAAAAAA" \
                    "8D9AAAAAVVVVVVVVxT//////CAQCgUAggD8AAAAAAADwPwAAA" \
                    "AAAAPA/AAAAAAAAAAAAAAAAAAAAAAAAAAAA"

# Function which changes the mode of ReaSamplOmatic5000 instance
# to `Note (Semitone shifted)`. Also resets all other parameters,
# so beware!
# Perhaps a ReaScript API function will one day exists for this.
def set_fx_mode(fx):
    track = fx.parent
    chunk = rp.reascript_api.GetTrackStateChunk(track.id, '', 2**25, False)[2]

    loc = find_fx_in_chunk(chunk, fx)

    for _ in range(3):
        loc = chunk.find("\n", loc + 1)

    data_start = loc + 1
    data_end = chunk.find("\n", loc + 1)

    print(chunk[data_start:data_end])

    chunk_new = chunk[:data_start] + fx_mode_note_data + chunk[data_end:]

    # Update the chunk.
    rp.reascript_api.SetTrackStateChunk(track.id, chunk_new, False)

# Helper function for below. Finds the first FX name in RPPXML of the
# track, starting at location `loc`.
def find_fx_name(chunk, loc):
    token_number = 4

    # Go to the next token.
    for _ in range(token_number):
        # Go to the start of the token
        loc = chunk.find(" ", loc + 1)
        name_start = loc + 1

        # Go to the end.
        if chunk[name_start] == '"':
            loc = chunk.find('"', loc + 2)
        else:
            loc = chunk.find(' ', loc + 1) - 1

        name_end = loc + 1

    return name_start, name_end


# Changes the state chunk of the track to update the FX name.
@rp.inside_reaper()
@rp.undo_block('Multi-Sampler: set name')
def set_fx_name(fx, new_name):
    track = fx.parent
    chunk = rp.reascript_api.GetTrackStateChunk(track.id, '', 2**25, False)[2]

    loc = find_fx_in_chunk(chunk, fx)

    # Find the name.
    loc = chunk.find("\n", loc + 1)
    name_start, name_end = find_fx_name(chunk, loc)

    # Enter the name in the chunk.
    if " " in new_name:
        new_name = f'"{new_name}"'
    chunk_new = chunk[:name_start] + new_name + chunk[name_end:]

    # Update the chunk.
    rp.reascript_api.SetTrackStateChunk(track.id, chunk_new, False)

@rp.inside_reaper()
@rp.undo_block('Multi-Sampler: add ReaSamplOmatic5000')
def add_in_reaper(samplorange, track, note_start, note_end,
            gain_for_minimum_velocity, create_pitched):
    samplomatic = track.add_fx("ReaSamplOmatic5000")

    if create_pitched:
        set_fx_mode(samplomatic)

    if samplorange:
        samplorange.fx = samplomatic
        samplorange.index = samplomatic.index

        samplorange.track_routing = current_track_routing
        samplorange.track_routing.samplorange_count += 1

    params = samplomatic.params
    params["Obey note-offs"] = create_pitched
    params["Gain for minimum velocity"] = gain_for_minimum_velocity
    params["Note range start"] = note_start / 127
    params["Note range end"] = note_end / 127

    global name_by_general_mid
    if name_by_general_midi.get():
        if samplorange.start in general_midi_drumkit:
            name = general_midi_drumkit[samplorange.start]
        else:
            name = default_fx_name
        if name_by_general_midi_nocaps:
            name = name.lower()
        set_fx_name(samplomatic, name)
    elif samplorange and samplorange.current_name:
        set_fx_name(samplomatic, samplorange.current_name)
    else:
        set_fx_name(samplomatic, default_fx_name)

    global samploranges
    soloing = any(s.solo for s in samploranges)
    if soloing:
        samplomatic.disable()
    
    # TODO: Call the detect-pitch function
    # This seems to be impossible in the ReaScript API for the moment.
    # Perhaps one day...


# Add new ReaSamplOmatic5000 instance.
def setup(track, note_start = -1, note_end = -1):
    global root, current_track, samploranges, window, last_touched

    # The default note ranges.
    if note_start < 0 and last_touched:
        note_start = last_touched.end + 1
    if note_start < 0:
        note_start = default_note_start
    if note_end < 0:
        note_end = note_start

    # Add the widget in the GUI
    if track == current_track:
        samplorange = SamploRange(window, None, track.color, note_start, note_end)
        samploranges.append(samplorange)
        last_touched = samplorange

        global render_groups
        move_through_groups(render_groups, samplorange)
    else:
        samplorange = None

    # Add the instance in REAPER.
    root.after(50, add_in_reaper, samplorange, track, note_start, note_end,
               gain_for_minimum_velocity, create_pitched.get())


# If no track is selected, create a new one. Then add new ReaSamplOmatic5000
# instances to all selected tracks.
def init(insert_at_cursor=False):
    global current_track, track_name_text, root

    with rp.inside_reaper():
        project = rp.Project()

        # Set all selected tracks. Of none are selected, create a new one.
        tracks = project.selected_tracks if not freeze.get() else [current_track]
        if len(tracks) == 0:
            tracks = [project.add_track()]
            tracks[0].name = default_multisampler_name
            track_name_text.set(default_multisampler_name)
            tracks[0].select()
            current_track = tracks[0]
            parse_current()


    for track in tracks:
        if not insert_at_cursor:
            setup(track)
        else:
            scroll_pos = canvas.xview()[0] * 128
            cursor_x = root.winfo_pointerx() - root.winfo_rootx()
            note = int(scroll_pos + cursor_x // width_per_note)
            setup(track, note, note)


def refresh():
    global current_track
    rp.reconnect()
    project = rp.Project()
    tracks = project.selected_tracks
    if len(tracks) > 0:
        current_track = tracks[0]
        parse_current()
    else:
        clear_samploranges()



# # # Separate functionality # # #

# Helper function for below.
def separate_track(track, bus):
    global samploranges, create_bus_on_separate, separate_overlap
    project = rp.Project()

    track_groups = {}
    track_index = track.index

    samploranges_selected = [s for s in samploranges if s.selected]
    if len(samploranges_selected) > 0:
        samploranges_separate = samploranges_selected
    else:
        samploranges_separate = samploranges

    samploranges_separate.sort(key=lambda x: -x.fx.index)

    for srange in samploranges_separate:
            index_add = 1 if not bus else 2

            if not separate_overlap.get():
                if not srange.render_group in track_groups:
                    track_groups[srange.render_group] = project.add_track(
                            index=track_index+index_add, name=f"{srange.fx.name}")
                    send = track.add_send(track_groups[srange.render_group])
                track_new = track_groups[srange.render_group]
            else:
                track_new = project.add_track(index=track_index+index_add,
                                              name=f"{srange.fx.name}")
                send = track.add_send(track_new)

            if create_bus_on_separate.get():
                # Select the track.
                track_new.select()

            # Move the fx to the tracks.
            srange.fx.move_to_track(track_new)


# Split the ReaSamplOmatic5000 instances over separate tracks.
# If 'create bus' is ticked, put them in a folder too.
def separate():
    global root, current_track
    if not current_track:
        return

    track_name_text.set("   separating...   ")
    root.after(100, separate_samploranges)

@rp.inside_reaper()
@rp.undo_block('Multi-Sampler: separate')
def separate_samploranges():
    global current_track, create_bus_on_separate
    project = rp.Project()

    bus = None
    if create_bus_on_separate.get():
        # Clear the selection for folder creation.
        project.unselect_all_tracks()

        # Add a bus track.
        bus = project.add_track(index=current_track.index+1,
                                name=f"bus - {current_track.name}")
        bus.select()

    # Create the tracks for all ReaSamplOmatic5000s.
    separate_track(current_track, bus)

    # Create the folder.
    if create_bus_on_separate.get():
        try:
            project.perform_action(rp.reascript_api.NamedCommandLookup("_SWS_MAKEFOLDER"))

            # Go back to selecting the original track.
            project.unselect_all_tracks()
            current_track.select()
        except:
            print("Install the SWS extension for automatic folder creation")

    parse_current()


# # # Drag and drop # # #

@rp.inside_reaper()
def set_samples(fx, filenames):
    track = fx.parent

    for i, filename in enumerate(filenames):
        rp.reascript_api.TrackFX_SetNamedConfigParm(track.id,
                fx.index, f"FILE{i}", filename)

mouse_pos = [-1, -1]
samploranges_drag = None
def set_mouse_pos(event):
    global mouse_pos
    mouse_pos = [event.x, event.y]

def drag_split(string):
    split = re.findall(r'\{.*?\}', string)

    for i, substring in enumerate(split):
        string = string.replace(substring, "")
        split[i] = split[i][1:-1]

    string = string.strip()
    split += string.split()

    split.sort()
    return split

def drop_enter(event):
    global samploranges, render_groups, samploranges_drag, current_track, check_loop, root

    if not current_track:
        return

    if not event.data:
        samploranges_drag = None
        rp.reaper.show_message_box(
                "No data in drag and drop event.\n\n" \
                "Consider enabling drag and drop from REAPER \n (Check `D\&D REAPER`)",
                "Multi Sampler error: drag and drop")
        return

    samploranges_drag = []

    for filepath in drag_split(event.data):
        file = os.path.basename(filepath)

        # Add the widget in the GUI
        samploranges_drag.append(SamploRange(window, None, (180,180,180),
                                             -2, -2, file))
        samploranges_drag[-1].filename = filepath
        samploranges.append(samploranges_drag[-1])
        last_touched = samploranges_drag[-1]

        move_through_groups(render_groups, samploranges_drag[-1])

    # return event.action

def drop_position(event):
    global root, width_per_note, samploranges_drag

    if not current_track:
        return

    if samploranges_drag == None:
        drop_enter(event)

    if not samploranges_drag:
        return

    scroll_pos = canvas.xview()[0] * 128 * width_per_note
    x_pos = event.x_root - root.winfo_x() + scroll_pos
    note = int(x_pos / width_per_note)

    for i, srange in enumerate(samploranges_drag):
        srange.start = note + i
        srange.end = note + i

        move_through_groups(render_groups, srange)

    return event.action

def drop_leave(event):
    global samploranges, samploranges_drag

    if not current_track or samploranges_drag == None:
        return

    for srange in samploranges_drag:
        delete_in_render_groups(srange)

        srange.widget.destroy()
        if srange.tooltip:
            srange.tooltip.destroy()
        samploranges.remove(srange)

    samploranges_drag = None

    return event.action

def drop(event):
    global samploranges_drag, current_track, root

    if not current_track:
        track_name_text.set("Please select a track to drag and drop to.")
        root.after(2000, dnd_remove_warning)
        return event.action

    # Add the note ranges in REAPER.
    root.after(50, drop_reaper)
    return event.action

def dnd_remove_warning():
    if track_name_text.get() == "Please select a track to drag and drop to.":
        track_name_text.set("")

@rp.inside_reaper()
def drop_reaper():
    global samploranges_drag, current_track

    for srange in samploranges_drag:
        srange.color = current_track.color
        add_in_reaper(srange, current_track, srange.start,
                      srange.end, gain_for_minimum_velocity,
                      create_pitched.get())
        set_samples(srange.fx, [srange.filename])
        srange.redraw()
    samploranges_drag = None





# # # Track parsing # # #

# Return true if the given fx is a ReaSamplOmatic instance.
@rp.inside_reaper()
def is_samplomatic(fx):
    try:
        fx.params["Note range start"]
        return True
    except Exception as e:
        return False
    # fx_name = rp.reascript_api.TrackFX_GetNamedConfigParm(
    #         fx.parent.id, fx.index, 'fx_name', '', 100000)[4]
    # return "ReaSamplOmatic5000" in fx_name


class Route(dict):
    samplorange_count = 0

# Recursively parse all ReaSamplOmatic5000 on the given track
# and all of its recursive MIDI sends.
def parse(track, no_reset=False, track_routing=None, recursion_depth=max_recursion_depth):
    global window, samploranges, render_groups, current_track_routing

    if recursion_depth == max_recursion_depth:
        print("Start parsing track...")

        # Remove the previous track info.
        if not no_reset:
            clear_samploranges()

        # Setup the routing dictionary.
        track_routing = Route()
    elif recursion_depth == 0:
        return

    project = rp.Project()

    # Parse the send tracks recursively.
    for send in list(track.sends):
        dest_track = send.dest_track
        track_routing[dest_track.id] = Route()
        if not send.midi_dest == (-1, -1):
            parse(dest_track, no_reset, track_routing[dest_track.id], recursion_depth - 1)

    # Create Range elements for all Samplomatics on the track.
    fxs = track.fxs
    for fx in list(fxs):
        if is_samplomatic(fx):
            if not no_reset:
                srange = SamploRange(window, fx, track.color)
                samploranges.append(srange)

                # Add to the render groups.
                move_through_groups(render_groups, srange)

                # Routing info
                srange.track_routing = track_routing
                srange.track_routing.samplorange_count += 1

    if recursion_depth == max_recursion_depth:
        current_track_routing = track_routing
        print("Done!")

# Simple in-between function to make sure all parsing happens
# inside REAPER via reapy (which is a lot faster).
@rp.inside_reaper()
def parse_reaper(track, no_reset=False):
    global track_name_text
    parse(track, no_reset)
    track_name_text.set(track.name)

# Call the recursive `parse` on the currently selected track.
# Set `no_reset` to True to not reset all samploranges, but to
# simply update them if any changed might be present.
def parse_current(no_reset=False):
    global root, current_track, track_name_text
    if current_track:
        parse_reaper(current_track, no_reset)
    else:
        track_name_text.set("")


# Check if the selection has changed, and loop.
slow_counter = 0
slow_counter_max = 10
def sync():
    global root, current_track, freeze, slow_counter, samploranges, samploranges_drag
    into_focus = False

    if stay_on_top.get() != root.attributes('-topmost'):
        root.attributes('-topmost', stay_on_top.get())

    if sync_with_reaper.get() and samploranges_drag == None:
        # Run the slow reaper check when the window comes into focus.
        if root.focus_displayof() != None and slow_counter > 0:
            reaper_sync_slow()
            slow_counter = 0
            into_focus = True

        # If not focused, up the counter.
        if root.focus_displayof() == None:
            slow_counter += 1

        # Run the quicker REAPER check depending on whether dnd is enabled.
        if allow_reaper_drag_and_drop.get():
            # Run the external REAPER checks only when the window come into focus.
            if into_focus:
                reaper_sync()
        else:
            # Run the external REAPER checks only when the window is not focused.
            if root.focus_displayof() == None:
                reaper_sync()

    # Necessary on some systems to close the popup menu.
    if root.focus_displayof() == None:
        popup_close()

    check_loop = root.after(100, sync)


# Recusively checks if the routing is still correct and if all tracks
# still have the same mount of ReaSamplOmatic5000 instances.
def no_routing_or_fx_change(track, routing):
    midi_sends = [send for send in track.sends if not send.midi_dest == (-1, -1)]

    # Amount of routes should be the same.
    if len(routing) != len(midi_sends):
        return False

    # Amount of ReaSamplOmatic5000 instances should be the same
    samplorange_count = len([fx for fx in track.fxs if is_samplomatic(fx)])
    if samplorange_count != routing.samplorange_count:
        return False

    # Recursively check the sends.
    for send in midi_sends:
        track_id = send.dest_track.id

        # It should have the same tracks.
        if not track_id in routing:
            return False

        # Continue recursively.
        if not no_routing_or_fx_change(send.dest_track, routing[track_id]):
            return False

    return True


# Remove all sample ranges currently present.
def clear_samploranges():
    global samploranges, render_groups

    for srange in samploranges:
        srange.widget.destroy()
        if srange.tooltip:
            srange.tooltip.destroy()

    samploranges = []
    render_groups = []


@rp.inside_reaper()
def reaper_sync():
    global current_track, samploranges, track_name_text

    project = rp.Project()
    tracks = project.selected_tracks
    n_tracks = len(tracks)

    # Check for track changes if not frozen.
    if not freeze.get():
        # Only show track info is precisely one is selected.
        if n_tracks != 1:
            current_track = None
            track_name_text.set("")
            last_touched = None

            # Remove the previous track info.
            clear_samploranges()

            return

        # Check if the track has changed.
        if current_track != tracks[0]:
            current_track = tracks[0]
            track_name_text.set(str(current_track.name).strip())

            parse_current()
            return

    # Check for ReaSamplOmatic5000 changes
    global alpha
    soloing = any(s.solo for s in samploranges)
    for srange in samploranges:
        if srange.fx == None:
            continue

        # Check for track color changes.
        color = srange.fx.parent.color
        if color != (0, 0, 0) and srange.color != color:
            srange.color = color
            srange.widget.configure(highlightbackground=rgb(color),
                                    bg=rgb(color, alpha))

        # Check for name changes.
        if srange.current_name != srange.fx.name:
            srange.current_name = None
            srange.draw_name()

        # Check bypass changes.
        if soloing:
            if srange.solo and not srange.fx.is_enabled:
                srange.fx.enable()
            elif not srange.solo and srange.fx.is_enabled:
                srange.fx.disable()
        else:
            if srange.fx.is_enabled == srange.mute:
                srange.set_mute(srange.mute)



# Check for changes in REAPER which take a bit more time.
# Only called when not interacting with the UI.
@rp.inside_reaper()
def reaper_sync_slow():
    global current_track, current_track_routing, samploranges

    if not current_track:
        return

    # Check for track routing changes and if any ReaSamplOmatic5000's
    # were added or removed.
    if not no_routing_or_fx_change(current_track, current_track_routing):
        parse_current()
    elif False: # Disabled: too slow on Windows and not necessary.
        # Check for note range changes.
        for srange in samploranges:
            is_different = False

            params = srange.fx.params
            start = round(params["Note range start"] * 127)
            if srange.start != start:
                srange.start = start
                is_different = True

            end = round(params["Note range end"] * 127)
            if srange.end != end:
                srange.end = end
                is_different = True

            # Redraw if necessary.
            if is_different:
                srange.redraw()



# # # Event handling - window resize and zoom # # #

# After resizing the window, all note sizes should be updated, which
# this function does. (The rest is done automatically by tkinter.)
def resize(event, canvas, window_id):
    global sampomatics, window, root, prev_geom, help_icon

    # Resize the window.
    canvas.itemconfigure(window_id, height=canvas.winfo_height())

    # Place the help icon.
    help_icon.place(x=root.winfo_width() - 28)

    # If necessary, resize (redraw) all notes.
    max_height = int(window.winfo_height() - piano_roll_height)
    if samploranges and samploranges[0].max_height != max_height:
        for samplerange in samploranges:
            samplerange.redraw()


# Zoom the note sizes. Update the piano roll and SamploRanges.
# Also try to keep the zoom centered.
# (this does not look very smooth, maybe it can be improved)
def zoom(zoom):
    global width_per_note, canvas, root

    canvas.forget()

    # Set the new size
    width_per_note_old = width_per_note
    width_per_note += zoom
    width_per_note = max(5, width_per_note)

    # Update the sizes
    global pianoroll_frame, samploranges
    for samplorange in samploranges:
        samplorange.redraw()
    for note_widget in pianoroll_frame.winfo_children():
        note_widget.configure(width=width_per_note -
                              adjust_for_highlight * highlight)

    # Move the canvas view
    global scrollbar
    scroll_pos = canvas.xview()[0] * 128 * width_per_note_old
    x_pos_before = root.winfo_pointerx() - root.winfo_rootx() + scroll_pos
    x_pos_before = (x_pos_before // width_per_note_old) * width_per_note_old
    x_pos_after = x_pos_before + (x_pos_before / width_per_note_old) * zoom

    canvas.configure(xscrollincrement=1)
    canvas.xview_scroll(round(x_pos_after - x_pos_before), "units")
    canvas.configure(xscrollincrement=0)

    canvas.pack(side="top", fill="both", expand=True)

# Zoom the pianoroll view.
def zoom_pianoroll(zoom):
    global piano_roll_height, pianoroll_frame, samploranges

    piano_roll_height += 2 * zoom
    piano_roll_height = max(5, piano_roll_height)

    for samplorange in samploranges:
        samplorange.redraw()
    for note_widget in pianoroll_frame.winfo_children():
        note_widget.configure(height=piano_roll_height -
                              adjust_for_highlight * highlight)


# # # Copy, paste and delete # # #

clipboard = []
def copy():
    global samploranges, clipboard
    clipboard = [srange for srange in samploranges if srange.selected]

@rp.inside_reaper()
@rp.undo_block('Multi-Sampler: paste sample ranges')
def paste():
    global clipboard, window, render_groups
    deselect_all()

    for srange in clipboard:
            if not srange in samploranges:
                print("FX {srange.fx.name} has been removed, skipping...")
                continue

            # Paste in REAPER
            track = srange.fx.parent
            fx_index = len(track.fxs)
            srange.fx.copy_to_track(track, index=fx_index)

            # Add the sample range
            srange_copy = SamploRange(window, track.fxs[fx_index], track.color)
            srange_copy.track_routing = srange.track_routing
            srange_copy.track_routing.samplorange_count += 1
            samploranges.append(srange_copy)

            # Add to the render groups.
            move_through_groups(render_groups, srange_copy)
            srange_copy.select(len(clipboard) > 1)

            srange_copy.update_reaper()
            srange.update_reaper()

def delete_in_render_groups(srange):
    global render_groups

    srange.end = -100
    srange.start = -100
    move_through_groups(render_groups, srange)
    render_groups.remove(srange.render_group)

@rp.inside_reaper()
@rp.undo_block('Multi-Sampler: delete sample ranges')
def delete():
    global samploranges, render_groups
    for srange in list(samploranges):
        if srange.selected:
            try:
                track = srange.fx.parent
                fx_index = srange.fx.index

                # Delete in REAPER.
                srange.fx.delete()

                # Update the routing info
                srange.track_routing.samplorange_count -= 1

                # Make sure the other sample ranges have the
                # correct FX indices.
                for s in samploranges:
                    if s.fx.parent == track:
                        if s.fx.index > fx_index:
                            s.fx = track.fxs[s.fx.index-1]

                # Delete in the groups.
                delete_in_render_groups(srange)

                # Delete in tkinter and the samploranges list
                srange.widget.destroy()
                if srange.tooltip:
                    srange.tooltip.destroy()
                samploranges.remove(srange)
            except:
                print(f"Could not delete FX {srange.fx.name}")


# Deselects all samploranges.
def deselect_all(exclude=None):
    global samploranges
    for srange in samploranges:
        if srange != exclude:
            srange.deselect()

    # Turn off all messages.
    note_all_off()

    # Necessary on some systems to close the popup menu.
    popup_close()

rectangle_base = [0, 0]
rectangle_add = [0, 0]
selection_box = None
rectangle_only_hor = False
already_selected = []
keep_selection = False
def rectangle_select_start(event, keep_select=False):
    global rectangle_base, rectangle_add, already_selected, rectangle_only_hor, \
           keep_selection, selection_box, window, track_name_label, width_per_note, \
           piano_roll_height
    rectangle_base = [event.x, event.y]

    keep_selection = keep_select

    # When the event is started not on the main canvas,
    # we need to adjust the location.
    rectangle_add = [0, 0]
    rectangle_only_hor = False
    if isinstance(event.widget, tk.Label):
        # Instance is the label.
        scroll_pos = canvas.xview()[0] * 128 * width_per_note
        rectangle_add[0] = round(scroll_pos)
        rectangle_add[1] = -track_name_label.winfo_height()
    elif event.widget.winfo_height() == piano_roll_height and event.widget.winfo_y() == 0:
        # Pianoroll buttons
        rectangle_add[0] = event.widget.winfo_x()
        rectangle_only_hor = True
    elif not event.widget is window:
        rectangle_add[0] = event.widget.winfo_x()
        rectangle_add[1] = event.widget.winfo_y()

    popup_close()
    selection_box = None

def rectangle_intersect(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

def rectangle_select(event):
    global rectangle_base, rectangle_add, rectangle_only_hor, selection_box, \
           keep_selection, already_selected, samploranges, canvas

    if not selection_box:
        root.config(cursor="plus" if keep_selection else "arrow")
        if not keep_selection:
            deselect_all()
        already_selected = [s for s in samploranges if s.selected]

    a = rectangle_add
    x = [rectangle_base[0] + a[0], event.x + a[0]]
    y = [rectangle_base[1] + a[1], event.y + a[1]]
    if not rectangle_only_hor:
        selection_box = [min(x), min(y), max(x), max(y)]
    else:
        selection_box = [min(x), 0, max(x), canvas.winfo_height() * 2]

    for srange in samploranges:
        if srange in already_selected:
            continue

        x, y = srange.widget.winfo_x(), srange.widget.winfo_y()
        w, h = srange.widget.winfo_width(), srange.widget.winfo_height()
        box = [x, y, x + w, y + h]

        # Check if in rectangle box.
        if rectangle_intersect(selection_box, box):
            srange.select(True, False)
        else:
            srange.deselect()

def select_all():
    for srange in samploranges:
        srange.selected = False
        srange.select(True)

def close_ui_selected():
    selected = [s for s in samploranges if s.selected]
    if len(selected) > 0:
        for srange in selected:
            srange.fx.close_ui()
    else:
        for srange in samploranges:
            srange.fx.close_ui()

# # # Copy / paste parameters # # #

params_copy = None
copy_fx_samples = False
params_sample = [
    "Attack", "Decay", "Sustain", "Release",
    "Use note-off release override", "Release (note-off)",
    "Volume", "Gain for minimum velocity", "Pan",

    "Obey note-offs",
    "Loop (requires note-offs)", "Loop start offset",
    "Sample start offset", "Sample end offset",
    "Crossfade loop length",

    "Sample"]

params_note = [
     "Note range start", "Note range end",
     "Pitch for start note", "Pitch for end note",
     "Pitch adjust", "Pitchbend range", "Portamento",

     "MIDI channel", "Max voices",
     "Minimum velocity", "Maximum velocity",

     "Probability of hitting", "Round-robin mode"]

def copy_params(params):
    global params_copy, fx_copy_source, copy_fx_samples
    selected = [s for s in samploranges if s.selected]

    if len(selected) != 1:
        rp.reaper.show_message_box("You need to select a single sample range to copy parameters.",
                "Multi Sampler error: copying parameters", )
        return

    fx_copy_source = selected[0].fx

    try:
        params_input = rp.reaper.get_user_inputs(
            "Fill in anything to copy, leave empty to skip", params)

        if "Sample" in params_input:
            copy_fx_samples = True
            del params_input["Sample"]
        else:
            copy_fx_samples = False

        params = (p[0] for p in params_input.items() if p[1] != "")
        params_copy = {p: fx_copy_source.params[p] for p in params}
    except RuntimeError:
        print("Input aborted")

@rp.inside_reaper()
@rp.undo_block('Multi-Sampler: paste parameters')
def paste_params():
    global params_copy, fx_copy_source, copy_fx_samples, samploranges

    if not params_copy and not copy_fx_samples:
        return

    selected = (s for s in samploranges if s.selected)

    for srange in selected:
        for p, value in params_copy.items():
            srange.fx.params[p] = value

        # Copy the sample.
        if copy_fx_samples:
            track_source = fx_copy_source.parent
            i = 0
            while filename := rp.reascript_api.TrackFX_GetNamedConfigParm(
                    track_source.id, fx_copy_source.index,
                    f"FILE{i}", "", 2**25)[4]:
                rp.reascript_api.TrackFX_SetNamedConfigParm(srange.fx.parent.id,
                        srange.fx.index, f"FILE{i}", filename)
                i += 1


    reaper_sync_slow()

# # # Popup menu # # #

def popup_menu(event):
    global root
    root.config(cursor="arrow")

    global right_click_menu

    if selection_box == None:
        try:
            right_click_menu.post(event.x_root, event.y_root)
        finally:
            right_click_menu.grab_release()

def popup_close(event=None):
    global right_click_menu
    if event:
        event.widget.unpost()
    elif right_click_menu:
        right_click_menu.unpost()

# # # Mute / solo # # #

@rp.undo_block('Multi-Sampler: toggle mute')
@rp.inside_reaper()
def mute_selection(reset=False):
    global samploranges
    selection = [s for s in samploranges if s.selected]

    mute = not all([s.mute for s in selection])

    if reset:
        for srange in samploranges:
            srange.set_mute(False)
    else:
        for srange in samploranges:
            if srange.selected:
                srange.set_mute(mute)

@rp.undo_block('Multi-Sampler: toggle solo')
@rp.inside_reaper()
def solo_selection(reset=False):
    global samploranges
    selection = [s for s in samploranges if s.selected]

    solo = not all(s.solo for s in selection)

    if reset:
        for srange in samploranges:
            srange.set_solo(False)
    else:
        for srange in samploranges:
            if srange.selected:
                srange.set_solo(solo)

    sranges_not_solo = [s for s in samploranges if not s.solo]
    mute_others = len(sranges_not_solo) != len(samploranges)
    for srange in sranges_not_solo:
        if mute_others or srange.mute:
            srange.fx.disable()
        else:
            srange.fx.enable()

def reset_solo_mute():
    solo_selection(True)
    mute_selection(True)


# # # REAPER forwarding # # #
def undo():
    global root
    with rp.inside_reaper():
        project = rp.Project()
        project.perform_action(40029) # Action ID for undo.
    reaper_sync()
    reaper_sync_slow()

def redo():
    global root
    with rp.inside_reaper():
        project = rp.Project()
        project.perform_action(40030) # Action ID for redo.
    reaper_sync()
    reaper_sync_slow()


# # # MIDI routing # # #

# Send the MIDI note on the selected MIDI channel.
def play_note(note, on, event=None):
    # Color the pianoroll note accordingly.
    black = (note % 12) in [1,3,6,8,10]
    if on:
        event.widget.configure(bg='gray' if black else 'lightgray')
    else:
        event.widget.configure(bg='black' if black else 'white')


    # Turn of all MIDI notes.
    note_all_off()

    msg = None
    if on:
        msg = [144, note, int(event.y / piano_roll_height * 128)]
    else:
        msg = [128, note, 0]

    rp.reascript_api.StuffMIDIMessage(0, *msg)

    # Necessary on some systems to close the popup menu.
    popup_close()

def note_all_off():
    rp.reascript_api.StuffMIDIMessage(0, 176, 123, 0)

# # # GUI setup # # #

def close():
    global running, root
    running = False
    root.destroy()

# The main GUI construction function.
def guimain():
    global root, window, canvas, scrollbar, pixel, select_rect
    global track_name_text, track_name_label, check_loop

    # Create the top level (root) window.
    if dnd_available:
        root = tkinterdnd2.Tk(className='samplomatic5000 multi')
    else:
        root = tk.Tk(className='samplomatic5000 multi')
    root.geometry(default_window_size)
    root.tk_setPalette(background=background_color,
                                   foreground=foreground_color,
                                   highlightBackground=highlight_color)

    # Create the virtual pixel
    pixel = tk.PhotoImage(width=1, height=1)

    # Create the buttons.
    buttons = tk.Frame(root)
    buttons.pack(side="top", anchor="nw")
    grid_index = -1

    btn_init = tk.Button(buttons, text="Add", width=6, height=1, command=init, 
                         highlightbackground=background_color)
    btn_init.grid(column=(grid_index := grid_index + 1), row=0, padx=4, pady=4)
    if tooltip_available:
        ToolTip(btn_init, delay=tooltip_delay, msg=
                "Add a new ReaSamplOmatic5000 instance to the currently "
                "selected tracks. If no tracks are selected, create a new "
                "one.")

    btn_separate = tk.Button(buttons, text="Separate", width=6,
                             height=1, command=separate,
                             highlightbackground=background_color)
    btn_separate.grid(column=(grid_index := grid_index + 1), row=0,
                      padx=4, pady=4)
    if tooltip_available:
        ToolTip(btn_separate, delay=tooltip_delay, msg=
                "For all selected sample ranges, move the "
                "ReaSamplOmatic5000 instance to a\nnew track,"
                "and add MIDI routing from the selected track."
                "You can keep managing\nthe instances from the "
                "current track.\n\n"
                "This allows you to create groups with separate "
                "FX processing.\n\n"
                "Note ranges are given the same color as the track.\n\n"
                "See `Separate overlap` and `Create bus` for options.")

    # Buttons to zoom in and out.
    btn_zoom_in  = tk.Button(buttons, text="+", width=1, height=1,
                             command=lambda: zoom(1),
                             highlightbackground=background_color)
    btn_zoom_out = tk.Button(buttons, text="-", width=1, height=1,
                             command=lambda: zoom(-1),
                             highlightbackground=background_color)
    btn_zoom_in.grid(column=(grid_index := grid_index + 1), row=0,
                     padx=4, pady=4)
    btn_zoom_out.grid(column=(grid_index := grid_index + 1), row=0,
                      padx=4, pady=4)
    if tooltip_available:
        ToolTip(btn_zoom_in, msg="Zoom in.\n\nAlternatively, hold ctrl and scroll.",
                delay=tooltip_delay)
        ToolTip(btn_zoom_out, msg="Zoom out.\n\nAlternatively, hold ctrl and scroll.",
                delay=tooltip_delay)

    # Create the checkboxes.
    global create_pitched, create_bus_on_separate, freeze, allow_reaper_drag_and_drop, \
           stay_on_top, separate_overlap, name_by_general_midi, sync_with_reaper
    create_pitched             = tk.IntVar(value=create_pitched)
    create_bus_on_separate     = tk.IntVar(value=create_bus_on_separate)
    freeze                     = tk.IntVar(value=freeze)
    stay_on_top                = tk.IntVar(value=stay_on_top)
    sync_with_reaper           = tk.IntVar(value=sync_with_reaper)
    allow_reaper_drag_and_drop = tk.IntVar(value=allow_reaper_drag_and_drop)
    separate_overlap           = tk.IntVar(value=separate_overlap)
    name_by_general_midi       = tk.IntVar(value=name_by_general_midi)

    # Create the check variables.
    sep = "|"
    check_row = 0
    checks = [("Freeze", freeze,
                  "When set, don't change tracks when changing selection"),
              ("Sync", sync_with_reaper,
                  "If this is turned off, no automatic syncing is done with REAPER "
                  "anymore. To reflect changes done in REAPER, such as renaming "
                  "and rerouting, you need to manually use the `refresh' action."
                  "\n\nIf you notice REAPER hang once in a while turning this off "
                  "might be a good idea. Especially on Windows syncing can be very "
                  "slow."),
              sep,
              ("On top", stay_on_top,
                  "When set, stay on top of all other windows."),
              sep,
              ("D&D REAPER", allow_reaper_drag_and_drop,
                  "When set, allow drag and drop from the REAPER media explorer. "
                  "However, since REAPER is frozen during drag and drop, "
                  "communication with REAPER needs to be disabled. To this end, "
                  "this window is then only updated when it is in focus." ),
              ("Pitched", create_pitched,
                  "When set, newly added ReaSamplOmatic5000's are set to the "
                  "`Note (Semitone shifted)` mode, instead of `Sample "
                  "(Ignores MIDI note)`. \nAlso, `Obey note-offs` is enabled."
                  "\n\nEnable this option when adding pitched samples, and disable "
                  "when adding (unpitched) percussion."
                  ),
              ("Name by MIDI", name_by_general_midi,
                  "When set, the ReaSamplOmatic5000 instances are "
                  "automatically given names based on their start note. "
                  "Namely, they are named after the general MIDI Drumkit names."
                  "\n\nThey are also automatically numbered when samples overlap."),
              sep,
              ("Create bus", create_bus_on_separate,
                  "When set, a bus track is automatically created when using "
                  "the separate functionality. You can make this the parent of "
                  "a folder containing the new tracks to mix everything "
                  "together again."
                  "\n\nFolder creation is automatic if you have the SWS extension "
                  "installed."),
              ("Separate overlap", separate_overlap,
                  "When set, samples that overlap are separated as normal when "
                  "using the separate functionality: each is added to its own "
                  "track. When not set, overlapping samples are instead added "
                  "to the same track."),
             ]

    if check_row != 0:
        grid_index = -1

    for check in checks:
        if isinstance(check, str):
            # Add a separator.
            sep = tk.StringVar(value=check)
            separator = tk.Label(buttons, textvariable=sep,
                                 highlightthickness=0, fg='gray')
            separator.grid(column=(grid_index := grid_index + 1),
                           row=check_row, padx=0, pady=0)
        else:
            # Add the check button.
            name, var, tooltip = check
            check = tk.Checkbutton(buttons, text=name, var=var,
                                   highlightthickness=0, fg='gray')
            check.grid(column=(grid_index := grid_index + 1), row=check_row, padx=4, pady=4)

            # Create the tooltip
            if tooltip_available:
                ToolTip(check, msg=tooltip, delay=tooltip_delay)

    # Create the help tooltip.
    global help_icon
    help_icon = tk.Button(root, text="?",
                highlightthickness=0, fg='white', compound="c",
                highlightbackground=background_color)
    help_icon.place(x=100, y=8, height=20, width=20)
    help_icon.tkraise()
    help_icon.place(x=root.winfo_width() - 20)

    help_icon.bind("<Button-1>", lambda e:
        webbrowser.open("https://github.com/maximvdberg/reasamplomatic5000-multi"))

    if tooltip_available:
        ToolTip(help_icon, delay=0.0,
                msg="Tooltips are available!\n"
                    "Hover over anything for more info.\n"
                    "\n"
                    "Click here to open the GitHub page, to\n"
                    " - find a list of keyboard shortcuts,\n"
                    " - open an issue to report bugs and\n"
                    "   make feature requests.\n"
                    "\n"
                    "Right click+drag for rectangle select.\n"
                    "Hold ctrl to add to selection.\n"
                    "\n"
                    "Hold ctrl and scroll to zoom. You can \n"
                    "also change the piano roll size if you \n"
                    "hover over it.\n"
                    "\n"
                    "Right click to open the action menu.\n"
                    " - Most actions apply to the selection,\n"
                    "   not the item under the cursor!\n"
                    " - Reset mute/solo removes all applied\n"
                    "   mutes and solos (ignoring selection).\n"
                    " - Refresh reloads the multi sampler.\n"
                    "   Use when de-synced with REAPER.\n"
                    "\n"
                    " Copy/paste params lets you copy any\n"
                    " parameters of a specific instance of\n"
                    " ReaSamplOmatic5000 to a selection.\n"
                    " A popup will open where you can select\n"
                    " which parameters to copy. Two sets\n"
                    " are available:\n"
                    "  - sample, concerning sample params\n"
                    "  - note, concerning note/midi params"
                )

    # Create the track label
    track_name_text = tk.StringVar()
    track_name_label = tk.Label(root, textvariable=track_name_text, anchor='w')
    track_name_label.pack(side="top", fill='x')
    track_name_text.set("")

    # Create the internal level, were we will draw everything
    container = tk.Frame(root, highlightthickness=0)
    canvas = tk.Canvas(container, highlightthickness=0)

    scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    window = tk.Frame(canvas, takefocus=True)

    window_id = canvas.create_window((0, 0), window=window, anchor="nw")
    canvas['xscrollcommand'] = scrollbar.set

    # Create the pianoroll
    gui_pianoroll()

    # Button mapping
    # General keybindings.
    for k in keys_add:
        canvas.bind_all(f"<{k}>", lambda e: init())
    for k in keys_refresh:
        canvas.bind_all(f"<{k}>", lambda e: refresh())
    for k in keys_separate:
        canvas.bind_all(f"<{k}>", lambda e: separate())
    for k in keys_scroll_center:
        canvas.bind_all(f"<{k}>", lambda e, c=canvas: c.xview_moveto(36/128))
    for k in keys_close_ui:
        canvas.bind_all(f"<{k}>", lambda e: close_ui_selected())
    for k in keys_undo:
        canvas.bind_all(f"<{k}>", lambda e: undo())
    for k in keys_redo:
        canvas.bind_all(f"<{k}>", lambda e: redo())

    window.bind("<Button-1>", lambda e: deselect_all())

    # Option toggles.
    for k in keys_freeze:
        canvas.bind_all(f"<{k}>",
            lambda e: freeze.set(not freeze.get()))
    for k in keys_stay_on_top:
        canvas.bind_all(f"<{k}>",
            lambda e: stay_on_top.set(not stay_on_top.get()))
    for k in keys_dnd_reaper:
        canvas.bind_all(f"<{k}>",
            lambda e: allow_reaper_drag_and_drop.set(
                not allow_reaper_drag_and_drop.get()))
    for k in keys_sync:
        canvas.bind_all(f"<{k}>",
            lambda e: sync_with_reaper.set(not sync_with_reaper.get()))
    for k in keys_pitched:
        canvas.bind_all(f"<{k}>",
            lambda e: create_pitched.set(not create_pitched.get()))
    for k in keys_name_by_midi:
        canvas.bind_all(f"<{k}>",
            lambda e: name_by_general_mid.set(
                not name_by_general_mid.get()))
    for k in keys_create_bus:
        canvas.bind_all(f"<{k}>",
            lambda e: create_bus_on_separate.set(
                not create_bus_on_separate.get()))
    for k in keys_separate_overlap:
        canvas.bind_all(f"<{k}>",
            lambda e: separate_overlap.set(
                not separate_overlap.get()))

    # Copy, paste and delete bindings.
    for k in keys_copy:
        canvas.bind_all(f"<{k}>", lambda e: copy())
    for k in keys_paste:
        canvas.bind_all(f"<{k}>", lambda e: paste())
    for k in keys_delete:
        canvas.bind_all(f"<{k}>", lambda e: delete())
    for k in keys_select_all:
        canvas.bind_all(f"<{k}>", lambda e: select_all())

    # Solo/mute bindings
    for k in keys_solo_toggle:
        canvas.bind_all(f"<{k}>", lambda e: mute_selection())
    for k in keys_unsolo_all:
        canvas.bind_all(f"<{k}>", lambda e: mute_selection(True))
    for k in keys_mute_toggle:
        canvas.bind_all(f"<{k}>", lambda e: solo_selection())
    for k in keys_unmute_all:
        canvas.bind_all(f"<{k}>", lambda e: solo_selection(True))
    for k in keys_reset_solo_and_mute:
        canvas.bind_all(f"<{k}>", lambda e: reset_solo_mute())

    # Param copy/paste bindings
    for k in keys_params_sample_copy:
        canvas.bind_all(f"<{k}>", lambda e: copy_params(params_sample))
    for k in keys_params_note_copy:
        canvas.bind_all(f"<{k}>", lambda e: copy_params(params_note))
    for k in keys_params_paste:
        canvas.bind_all(f"<{k}>", lambda e: paste_params())


    # Right click popup menu.
    global right_click_menu
    m = tk.Menu(root, tearoff = 0)
    m.add_command(label = "Add note range", command=lambda: init(True))
    m.add_separator()
    m.add_command(label = "Toggle mute", command=mute_selection)
    m.add_command(label = "Toggle solo", command=solo_selection)
    m.add_command(label = "Reset mute/solo", command=reset_solo_mute)
    m.add_separator()
    m.add_command(label = "Copy", command=copy)
    m.add_command(label = "Paste", command=paste)
    m.add_command(label = "Delete", command=delete)
    m.add_separator()
    m.add_command(label = "Copy params (sample)",
            command=lambda: copy_params(params_sample))
    m.add_command(label = "Copy params (note)",
            command=lambda: copy_params(params_note))
    m.add_command(label = "Paste params", command=paste_params)
    m.add_separator()
    m.add_command(label = "Close UI", command=close_ui_selected)
    m.add_command(label = "Separate", command=separate)
    m.add_separator()
    m.add_command(label = "Refresh", command=refresh)
    m.bind("<FocusOut>", popup_close)

    right_click_menu = m
    if on_macOS:
        canvas.bind_all("<ButtonRelease-2>", popup_menu)
    else:
        canvas.bind_all("<ButtonRelease-3>", popup_menu)

    # Rectangle select
    if on_macOS:
        canvas.bind_all("<Button-2>",  lambda e: rectangle_select_start(e))
        canvas.bind_all("<Control-2>", lambda e: rectangle_select_start(e, True))
        canvas.bind_all("<B2-Motion>", rectangle_select)
    else:
        canvas.bind_all("<Button-3>",  lambda e: rectangle_select_start(e))
        canvas.bind_all("<Control-3>", lambda e: rectangle_select_start(e, True))
        canvas.bind_all("<B3-Motion>", rectangle_select)

    # Resizing
    window.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
    root.bind("<Configure>", lambda e, c=canvas, fid=window_id: resize(e, c, fid))

    # Scrolling with middle mouse button (doesn't seem to work very well though)
    if on_macOS:
        window.bind_all("<ButtonPress-2>", lambda e, c=canvas: c.scan_mark(e.x, e.y))
        window.bind_all("<B2-Motion>", lambda e, c=canvas: c.scan_dragto(e.x, 0, gain=1))
    else:
        window.bind_all("<ButtonPress-2>", lambda e, c=canvas: c.scan_mark(e.x, e.y))
        window.bind_all("<B2-Motion>", lambda e, c=canvas: c.scan_dragto(e.x, 0, gain=1))

    # Scrolling
    scroll_windows = lambda e, c=canvas: canvas.xview_scroll(int(-e.delta/abs(e.delta)*scroll_speed) , "units")
    scroll_linux = lambda direction, c=canvas: canvas.xview_scroll(direction*scroll_speed, "units")
    canvas.bind_all("<MouseWheel>", scroll_windows, add=True)
    canvas.bind_all("<Button-4>", lambda e, d=-1: scroll_linux(d), add=True)
    canvas.bind_all("<Button-5>", lambda e, d=1: scroll_linux(d), add=True)

    # Zooming (canvas)
    zoom_windows = lambda e: zoom(int(-e.delta/abs(e.delta)*zoom_speed))
    zoom_linux = lambda direction: zoom(direction*zoom_speed)
    canvas.bind_all("<Control-MouseWheel>", zoom_windows, add=True)
    canvas.bind_all("<Control-Button-4>", lambda e, d=1: zoom_linux(d), add=True)
    canvas.bind_all("<Control-Button-5>", lambda e, d=-1: zoom_linux(d), add=True)

    # Zooming (pianoroll)
    zoom_pianoroll_windows = lambda e: zoom_pianoroll(int(-e.delta/abs(e.delta)*zoom_speed))
    zoom_pianoroll_linux = lambda direction: zoom_pianoroll(direction*zoom_speed)
    if on_macOS:
        canvas.bind_all("<Mod2-MouseWheel>", zoom_pianoroll_windows, add=True)
        canvas.bind_all("<Mod2-Button-4>", lambda e, d=1: zoom_pianoroll_linux(d), add=True)
        canvas.bind_all("<Mod2-Button-5>", lambda e, d=-1: zoom_pianoroll_linux(d), add=True)
    else:
        canvas.bind_all("<Alt-MouseWheel>", zoom_pianoroll_windows, add=True)
        canvas.bind_all("<Alt-Button-4>", lambda e, d=1: zoom_pianoroll_linux(d), add=True)
        canvas.bind_all("<Alt-Button-5>", lambda e, d=-1: zoom_pianoroll_linux(d), add=True)

    # Drag-and-drop
    if dnd_available:
        container.drop_target_register(tkinterdnd2.DND_FILES)
        container.dnd_bind('<<DropEnter>>', drop_enter)
        container.dnd_bind('<<DropPosition>>', drop_position)
        container.dnd_bind('<<DropLeave>>', drop_leave)
        container.dnd_bind('<<Drop>>', drop)
        container.drag_source_register(1, tkinterdnd2.DND_FILES)


    # Packing
    container.pack(side="bottom", fill="both", expand=True)
    scrollbar.pack(side="bottom", fill="x")
    canvas.pack(side="top", fill="both", expand=True)

    # Setup the REAPER check loop.
    check_loop = root.after(100, sync)

    # Start the GUI loop.
    root.after(10, lambda c=canvas: c.xview_moveto(36/128)) # Scroll the view to C2
    root.update_idletasks()
    root.deiconify()
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


# Create the pianoroll GUI.
def gui_pianoroll():
    global pixel, window, pianoroll_frame

    w = width_per_note - adjust_for_highlight * highlight
    h = piano_roll_height - adjust_for_highlight * highlight

    pianoroll_frame = tk.Frame(window)
    pianoroll_frame.pack(anchor = "w", side=tk.BOTTOM)

    octaves = 10
    for note in range(128):
        black = (note % 12) in [1,3,6,8,10]
        color = 'black' if black else 'white'
        fg_color = 'white' if black else 'black'
        select_color = 'gray' if black else 'lightgray'
        note_button = tk.Label(pianoroll_frame,
                image=pixel,
                text=f"C{note//12-1}" if note % 12 == 0 else " ",
                width=w, height=h,
                padx=0, pady=0,
                highlightthickness=highlight,
                highlightbackground="#F0F0F0",
                bd=0,
                bg=color,
                fg=fg_color,
                compound="c")
        note_button.grid(column=note, row=0)
        note_button.bind("<Button-1>", lambda e, i=note: play_note(i, True, e))
        note_button.bind("<ButtonRelease-1>", lambda e, i=note: play_note(i, False, e))

        if tooltip_available:
            tooltip = ToolTip(note_button, delay=tooltip_delay,
                              msg=f"Press to send MIDI note {note} to reaper. "
                              "\n\nVertical position determines velocity.")

# # # Main # # #

if __name__ == "__main__":
    sep = "/"

    # Check system.
    creationflags = 0
    if sys.platform.startswith('win32'):
        # TODO: check other platforms which also need this.
        adjust_for_highlight = 2
        sep = "\\"
        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    elif sys.platform.startswith("darwin"):
        on_macOS = True

    if rp.is_inside_reaper():
        # raise Exception("Please run `launch-sampler.py` to launch the "
        #                 "multi-sampler from inside of REAPER.")
        # Open itself as a new process.
        path = f"{sep}Scripts{sep}ReaSamplOmatic5000 Multi{sep}Sampler{sep}reasamplomatic_multi.py"
        multisampler_process = subprocess.Popen(["python",  rp.reaper.get_resource_path() + path],
                start_new_session=True, creationflags=creationflags)
    else:
        rp.reconnect()

        # Setup the GUI.
        guimain()


