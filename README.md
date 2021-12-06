
# D2R: DS1info2Unity
Adds DS1-infos to UnityEditor.

technical: this tool converts .ds1 level info to .json. Provides 3D-reference objects in Unity-D2R-Scene-Editor for easier D2R map editing.

tldr: Helps you create D2R maps :)
![example](https://github.com/MilesTeg97/D2R-DS1info2Unity/blob/main/pngs/denent4_descr.png)

## Installation:
- Extract all files to your Win_DS1Edit folder.

(see guide "Unlock map editing for D2R" at https://www.d2rmodding.com/guides )

requires:
- python 3 (python.org) and numpy (command line: pip install numpy)
- [optional] json to improve performance: pip install ujson
- Win_DS1Edit. See guide "Unlock map editing for D2R" at https://www.d2rmodding.com/guides 
- Unity-D2R-Scene-Editor see https://github.com/pairofdocs/Unity-D2R-Scene-Editor

## Usage:
- copy the .ds1 and .json of the map to your Win_DS1Edit folder
- edit map in Win_DS1Edit, save & quit
- run the tool: 
     - click ds1info2unity.py and select MAPNAME.ds1
     - or via commandline: ds1info2unity.py MAPNAME.ds1

### Brief background
Diablo2 maps are in \*.ds1 file format. These can be edited using Paul Siramys awesome visual Win_DS1Edit.

D2R still uses these for e.g. floor tile calculation, game objects, and player collision info.

In addition D2R adds .json files which store most of the high def visual infos of the new game. One for each .ds1. 

##### Problem
Unity-D2R-Scene-Editor can only open and edit the .json files. Therefor you are editing "blindly" because all changes made in Win_DS1Edit (floor tile calculation, interactive objects, player collision info etc.) are invisible to Unity-D2R-Scene-Editor. 

##### Solution
ds1info2unity converts map information from .ds1 to .json and provides map makers with visual cue objects (read-only) where changes were made. (I'll add some screens later)


### FAQ

#### Why not build a fancy new editor for D2R?

A: D2R uses a hibrid map design (two completely different file formats). You would end up porting Paul Siramys editor (a huge achievement btw!) to Unity. It involes assembly code... it's difficult.

#### Why Win_DS1Edit for editing .ds1 ?
It's the only a full featured level editor for D2. It's stable and compatible with lots of modded maps from D2 era. 
Creating preset tilemaps ("floors") is relatively easy (or at least well documented). 

#### Credits
huge thanks to 
- Huge thanks to Paul Siramy for his great editor: Win_DS1Edit http://paul.siramy.free.fr/_divers/ds1/dl_ds1edit.html 
- pairofdocs & Shalzuth https://github.com/pairofdocs/Unity-D2R-Scene-Editor
- Bonesy for his great D2R tutorials
- www.d2mods.info aka Phrozen Keep community (especially for creating & hosting a superb knowledge base)
- the nice D2 modding community in general :)

### Copyrights

This tool uses a modified version of Paul Siramys Win_DS1Edit http://paul.siramy.free.fr/_divers/ds1/dl_ds1edit.html 
using the library Allegro v 4.4.2 see https://github.com/liballeg/allegro5/releases

Diablo II and Diablo II: Resurrected are copyrighted by Blizzard Entertainment, Inc. All rights reserved. Diablo II, Diablo II: Resurrected and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries.
All trademarks referenced here are the properties of their respective owners.

This project and its maintainers are not associated with or endorsed by Blizzard Entertainment, Inc.
