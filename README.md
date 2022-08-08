# ReaSamplOmatic5000 multi

 ReaSamplOmatic500 multi lets you arrange ReaSamplOmatic5000 instances on a piano roll. This project aims to give REAPER a sampler such as FL Studio's [DirectWave Sampler](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/DirectWave.htm)  or the [TX16Wx Software Sampler](https://www.tx16wx.com/), while also integrating with REAPER routing.

 The script is powered by the excellent [reapy](https://github.com/RomeoDespres/reapy), and uses [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI.

 You might also be interested in [MPL's ReaSamplomatic5000 manager](https://forums.cockos.com/showthread.php?t=207972), which is similar but focuses mainly on single-note (drum) samples. Definitely check out his useful [ReaSamplomatic5000 scripts](https://github.com/MichaelPilyavskiy/ReaScripts) too!

## Contents

1. [Dependencies and Installation](#dependencies-and-installation)
    * [Optional dependencies](#optional-dependencies)
    * [Getting the script](#getting-the-script)
2. [Usage notes](#usage-notes)
    * [Overview](#overview)
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

Alternatively, you can download the script from this repository, and run it with Python.

## Usage notes

### Overview 

After succesfull installation using ReaPack, you can find `Script: reasamplomatic_multi.py` in the actions menu. Simply run it (setting a keyshortcut is recommended) to launch the sampler. Note that on Windows it migh take a while to start up. Alternatively, you can run the script outside of REAPER with Python. 

After startup, the multi sampler will show all ReaSamplOmatic5000 instances on the selected track. Press `Add` to add one. Simply drag it with the mouse to move it, and drag the edges to resize. 

Use ctrl+click to add items to the selection. Right click and drag for a nice and quick rectangle select. Hold alt to stretch the items.

Right click anywhere to list a bunch of actions. Most actions will apply to your selection. 

Options are available at the top of the window. If you installed `tktooltip` (which is recommended), they all have a short description. 
For instance, check `freeze` to stay on the selected track, and not follow the selection any more. Check `sync` to disable syncing with REAPER, which might be [too slow on Windows](#performance-on-windows).

### Feature list

A short list of miscellaneous features:

 * __Zoom & resize__ Scroll the view with the mouse wheel, or click the middle mouse button and drag. Zoom with `ctrl+mousewheel`, or the `+` and `-` buttons. Zoom the piano roll with `alt+mousewheel`. The window is freely resizable (and you can change the default size in the script).
 * __Layering__ The note ranges align vertically such that they don't overlap. This allows for easy layering of multiple samples.
 * __Groups__ The multi sampler integrates with MIDI routing in REAPER. See [creating groups](#creating-groups) for more information.
 * __Parameter copy__ You can copy and paste specific parameters of the ReaSamplOmatic5000 instances. See [copying parameters](#copying-parameters) for more information.
 * __Drag and drop__ You can drag and drop samples into the window. Note that to drag and drop from the REAPER media explorer, you need to enable the `D&D REAPER` option. Go [here](#drag-and-drop-from-inside-reaper) to find out why.
 * __Solo and mute__ You can solo and mute note ranges.
 * __MIDI__ You can click on the notes on the piano roll to send MIDI data to REAPER. Velocity is dependent on the height of your mouse.
 * __Defaults__ If you want, you can change some default values at the top of the script (short descriptions are given). You can change behaviour as well as appearance.
 * __Colors__ The multi sampler also uses the track colors. You can set the `alpha` parameter at the top of the script to change how to colors are used.

### Creating groups

The `Separate` action takes all ReaSamplOmatic5000 instances on the current track, and separates them over new tracks. It adds a MIDI-route from the selected track to these tracks. This is useful for individual effects processing (for instance when sampling drums: for the bass drum, the snare, hi-hats, etc.). You can still edit the ranges in the original multi sampler window.

You can select any of these tracks and use the multi sampler on them individually. This acts essentially as a group, where you can add and tweak additional FX for this set of ReaSamplOmatic5000s as you please. Selecting the original parent track again gives you access to all groups at once. In fact, the GUI will show all ReaSamplOmatic5000 instances which are reached through MIDI routing from the selected track (up to a recursion limit, which you can change at the top of the script).

When the `Create bus` option is ticked, an additional bus track is created. You can make a folder of the created track with this as the parent track to mix everything together. If you have the [SWS extension](https://www.sws-extension.org/) installed, this is done automatically!

When the `Separate overlap` option is ticked, all ReaSamploMatic5000s with overlap will be send to the same track when separating. This is handy for instance when designing a snare consisting of multiple samples, which need to remain mixed together when applying FX.

### Copying parameters

The `Copy/paste params` actions lets you copy any parameters of a specific instance of ReaSamplOmatic5000 to a selection of instances. For instance, you can copy only the ADSR envelope, while leaving the other parameters unchanged.

To start, select a single note range and right click to open the action menu. Then select `Copy/paste params`. Two sets are available:

 - __sample__ concerning sample parameters, such as the ADSR, looping, etc.
 - __note__ concerning note and MIDI parameters, concerning note ranges, playback pitch, etc.
 
A popup will open where you can select which parameters to copy. Fill anything in for the fields you want to copy and simply leave the other ones empty. Afterwards you can select the target note ranges and use the `Paste params` action to copy the parameters to the selection. 
 
### Keyboard shortcuts

There are keyboard shortcuts for most actions. You can edit them and add more in the script file. 
You should use the tkinter syntax for this (I think the present bindings should provide a good example).

| Action               | Binding       |
| -------------------- | ------------- |
| add                  | `a`           |
| refresh              | `r`           |
| separate             | `g`           |
| scroll to center     | `z`           |
| close instance ui    | `c`           |
| undo                 | `ctrl+z`      |
| redo                 | `ctrl+Z`      |
|                      |               |
| copy                 | `ctrl+c`, `y` |
| paste                | `ctrl+v`, `p` |
| delete               | `Delete`, `d` |
| select all           | `ctrl+a`      |
|                      |               |
| solo toggle          | `m`           |
| unsolo all           | `M`           |
| mute toggle          | `s`           |
| unmute all           | `S`           |
| reset solo and mute  | `x`           |
|                      |               |
| params copy (sample) | `b`           |
| params copy (note)   | `B`           |
| params paste         | `n`           |


## Planned Features
 - [ ] Call "detect pitch" from the sampler. See [here](#no-automatic-pitch-detection).
 - [ ] A way to save user settings without requiring them to edit the script
 - [ ] Shortcut to zoom to fit all note ranges.
 - [ ] Testing! There are probably still many bugs, so please let me know if you find any. 

## Limitations

#### No automatic pitch detection

After changing the note range for pitched samples, you currently need to manually hit the "Detect pitch" button in each ReaSamplOmatic5000 instance. This is very impractical, and really limits the usability of the program. I already asked [in this thread](https://forum.cockos.com/showthread.php?t=19881), perhaps one day this option will be there.

#### Docking

As far as I know, Tk windows cannot be docked in REAPER, so docking the multi sampler is sadly not possible.

#### Drag and drop from inside REAPER

Since drag-and-dropping anything from REAPER freezes the REAPER window, communication with reapy will hang. So the loop which checks for changes in REAPER (such as switching tracks and name changes) will then hang too, which freezes everything.

This can be circumvented by disabling communication with REAPER whenever doing drag and drop. However, we don't know when the user might initiate drag and drop. As a workaround, we can disable REAPER communication altogether when the multi sampler window is not focused.

The option `D&D REAPER` does precisely this: turn it on to enable drag-and-drop from inside of REAPER, at the cost of the multi sampler only being updated when its window is focused.

If you know a more elegant solution to this, let me know!

#### Performance on Windows

Performance on Windows is sadly not amazing. 
Reapy uses Python sockets for communication with REAPER, which seem to be very slow on Windows. You'll notice REAPER regularly hanging for a bit, which is precisely when the multi sampler tries to sync with REAPER (if `D&D REAPER` is on, this happens when focusing the multi sampler window, as it then tries to sync with REAPER). I'm not an expert on this, perhaps someone knows how to make this faster. In any case, you can turn of `Sync` to disable automatic syncing with REAPER, and instead use the `Refresh` action (default shortcut is `r`).

Additionally, the Tk implementation on Windows is very inefficient in comparison to other platforms. I found the responsiveness of dragging/resizing to be somewhat sluggish, and start up times are quite long.

#### Flickering zoom

There is some flickering while zooming. I'm pretty sure this is a limitation on how tkinter works, as I don't think it is impossible to pause the render callback during resizing. Please tell me if you know of a way to circumvent this!


## License

The script is licensed under the GNU GPLv3, see [license](LICENSE).
