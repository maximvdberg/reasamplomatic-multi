# ReaSamplOmatic5000 multi

 ReaSamplOmatic500 multi lets you arrange ReaSamplOmatic5000 instances on a piano roll. This project aims to give REAPER a sampler such as FL Studio's [DirectWave Sampler](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/DirectWave.htm)  or the [TX16Wx Software Sampler](https://www.tx16wx.com/), while also integrating with REAPER routing.

 The script is powered by the excellent [reapy](https://github.com/RomeoDespres/reapy), and uses [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI.

 You might also be interested in [MPL's ReaSamplomatic5000 manager](https://forums.cockos.com/showthread.php?t=207972), which is similar but focuses mainly on single-note (drum) samples. Definitely check out his useful [ReaSamplomatic5000 scripts](https://github.com/MichaelPilyavskiy/ReaScripts) too!

## Contents

1. [Dependencies and Installation](#dependencies-and-installation)
    * [Optional dependencies](#optional-dependencies)
    * [Getting the script](#getting-the-script)
2. [Usage notes](#usage-notes)
    * [Features list](#feature-list)
    * [Creating groups](#creating-groups)
    * [Copying parameters](#copying-parameters)
    * [Keyboard shortcuts](#keyboard-shortcuts)
3. [Planned features](#planned-features)
4. [Limitations](#limitations)
5. [License](#license)

## Dependencies and Installation

You need to install `reapy` and `tkinter` for the program to work. To install `reapy`, see the instructions over [here](https://github.com/RomeoDespres/reapy#installation). Make sure you have Python installed and that it is detected by REAPER. `tkinter` should be installed by default.

### Optional dependencies

 - For drag-and-drop support, install the `tkinterdnd2` package.
 - To show useful tooltips on hover, you need to install `tktooltip`.

To install these dependencies, run the following in a terminal:

```
pip install mido tkinterdnd2 tktooltip
```

or use whatever Python package manager you have installed.

### Getting the script

You can add the following repository to [ReaPack](https://reapack.com/):

```
https://github.com/maximvdberg/reasamplomatic-multi/raw/master/index.xml
```

Alternatively, you can download the script from this repository, and run the it with Python.

## Usage notes

[will be written soon]

The multisampler will show all ReaSamplOmatic5000s from the selected track. Check `freeze` to stay on the selected track, and not follow the selection any more.

### Feature list

A short list of features and usage notes:

 * __Adding instances__ The `Add` button adds an instance of ReaSamplOmatic5000 on all selected tracks. If no track is selected, it creates a new track.
 * __Moving__ Move note ranges by clicking and dragging.
 * __Resizing__ Click the range edges and drag to resize them.
 * __Selecting__ You can select and edit multiple ranges by holding `ctrl` and clicking, or by selecting multiple ranges with the right mouse button.
 * __Copy/paste/delete__ Press `ctrl+c` and `ctrl+v` for copy and paste respectively.  Press `delete` or `d` to delete the selection.
 * __Layering__ The note ranges align vertically such that they don't overlap. This allows for easy layering of multiple samples.
 * __Groups__ The multi-sampler integrates with MIDI routing in REAPER. See [creating groups](#creating-groups) for more information.
 * __Open FX window__ You can click on any range to open up its FX-window. Double click to also close the windows of all other groups.
 * __Scroll & zoom__ Scroll the view with the mouse wheel, or click the middle mouse button and drag. Zoom with `ctrl+mousewheel`, or the `+` and `-` buttons. Zoom the piano roll with `alt+mousewheel`. The window is freely resizable (you can change the default size in the script).
 * __MIDI__ You can click on the notes on the piano roll to send MIDI data to reaper. Velocity is dependent on the height of your mouse. Read the script for details on how to set it up.
 * __Obey note-offs__ You can select whether newly added instances should obey note-offs or not (useful for sampling drums)
 * __Shortcuts__ You can press `r` as a shortcut for `Refresh`, `a` for `Add`, and `s` for `Separate`. Press `c` to scroll the view to C2.
 * __Defaults__ If you want, you can change some default values at the top of the script (short descriptions are given). You can change behaviour as well as appearance.
 * __Colors__ The multisampler also uses the track colors. You can set the alpha parameter at the top of the script to change how to colors are used.

### Creating groups

The `Separate` action takes all ReaSamplOmatic5000 instances on the current track, and separates them over new tracks. It adds a MIDI-route from the selected track to these tracks. This is useful for individual effects processing (for instance when sampling drums: for the bass drum, the snare, hi-hats, etc.). You can still edit the ranges in the original multi sampler window.

You can select any of these tracks and use the multisampler on them individually. This acts essentially as a group, where you can add and tweak additional FX for this set of ReaSamplOmatic5000s as you please. Selecting the original parent track again gives you access to all groups at once. In fact, the GUI will show all ReaSamplOmatic5000 instances which are reached through MIDI routing from the selected track (up to a recursion limit, which you can change at the top of the script).

When the `Create bus` option is ticked, an additional bus track is created. You can make a folder of the created track with this as the parent track to mix everything together. If you have the SWS extension installed, this is done automatically!

When the `Separate overlap` option is ticked, all ReaSamploMatic5000s with overlap will be send to the same track when separating. This is handy for instance when designing a snare consisting of multiple samples, which need to remain mixed together when applying FX.

### Copying parameters

[will be written soon]

### Keyboard shortcuts

[will be written soon]

## Planned Features
 - [ ] Call "detect pitch" from the sampler
 - [ ] A way to save user settings without requiring them to edit the script

Testing! Especially on different platforms, which hasn't been done yet.

## Limitations

#### Docking

As far as I know, tk windows cannot be docked in REAPER, so docking the multi sampler is sadly not possible.

#### No automatic pitch detection

After changing the note range for pitched samples, you currently need to manually hit the "Detect pitch" button in each ReaSamplOmatic5000 instance. This is very impractical, and really limits the usability of the program. I already asked [in this thread](https://forum.cockos.com/showthread.php?t=19881), perhaps one day this option will be there.

#### Drag and drop from inside REAPER

Since drag-and-dropping anything from REAPER freezes the REAPER window, communication with reapy will hang. So the loop which checks for changes in REAPER (such as switching tracks and name changes) will then hang too, which freezes everything.

This can be circumvented by disabling communication with REAPER whenever doing drag and drop. However, we don't know when the user might initiate drag and drop. As a workaround, we can disable REAPER communication altogether when the multi sampler window is not focused.

The option `D&D REAPER` does precisely this: turn it on to enable drag-and-drop from inside of REAPER, at the cost of the multi sampler only being updated when the its window is focused.

If you know a more elegant solution to this, let me know!

#### Flickering zoom

There is some flickering while zooming. I'm pretty sure this is a limitation on how tkinter works, as I don't think it is impossible to pause the render callback during resizing. Please tell me if you know of a way to circumvent this!

#### Bugs

There are probably a lot of bugs still. Please let me know if you find one! (and tell me how to reproduce it)


## License

The script is licensed under the GNU GPLv3, see [license](LICENSE).
