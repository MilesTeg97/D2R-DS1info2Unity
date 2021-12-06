# v0.1
# dependencies:
# tested with Python 3.9+
# 
# 
# you'll need numpy package: pip install numpy
# see also 
#
# https://www.python.org/
# https://numpy.org/install/
#
#
# maplist.txt 
# somemap.json
# somemap.ds1

# Win_DS1Edit needs to be closed!
#
# 1x normal Tile= 25x Subtiles in D2Legacy. 
# All 25 numbers are (thankfully!) ordered topleft-bottomright as 5x5 matrix
#
# as nonwalkable-info, cubes will indicate:
# walls, buildings in general


'''
    content:

        1. Settings
        2. Check prerequisites
        3. maplist.txt
        4. Win_DS1Export.exe
        5. Parse data
        5.1 Metadata / map size
        5.2 Walkable info
        5.2.1 optimize data
        5.4 Objects info
        6. JSON objects
        7. Results
'''

import numpy as np
try:
    import ujson as json
except ImportError:
    import json
import argparse
import sys
from io import StringIO
import os.path
import subprocess
from tkinter.filedialog import askopenfilename


# 1. Settings
#==============
#
# USER SETTINGS
#
#ds1name="TownWest.ds1"   # use argument instead

csvmap=1  # additionally write a numeric csv-"map" file
mergejson=1     # 1(default): merges json data with original json  2: not yet available
#debugfile='testbatch_debug.txt'

# argument parser
#print('Number of arguments: {}'.format(len(sys.argv)))
#print('Argument(s) passed: {}'.format(str(sys.argv)))

if len(sys.argv)==1:
        print("Please select a ds1 file")
        ds1name = askopenfilename(title="Select a DS1 File", initialdir=".", filetypes=[("DS1 File","*.ds1")])
elif not os.path.isfile(sys.argv[1]):
        print("Please select a ds1 file")
        ds1name = askopenfilename(title="Select a DS1 File", initialdir=".", filetypes=[("DS1 File","*.ds1")])
else: 
        ds1name=sys.argv[1]
ds1name=os.path.basename(ds1name)
#print(os.path.basename(your_path))

if ds1name.strip()=="":
    print("No file selected. [101]")
    exit()

if not os.path.isfile(ds1name):
    print("s.path.isf")
    exit()

# Developer Settings (Debugging etc)
#-------------------
nojumpext="_nojump.txt"
nowalkext="_nowalk.txt"
mapjsoninfo="_ds1info.json" # file affix
maplistfile="maplist.txt"
basename=ds1name.split(".")[0]   #ds1/json filename without extension


# Filenames
#----------------
#basename=os.path.splitext(ds1name)[0].strip() #should be the same as ds1...

basename=ds1name.split(".")[0]
cvsnojump=basename+nojumpext
cvsnowalk=basename+nowalkext
#debugfile='testbatch_debug.txt'
mapjsonfile=basename +".json"  #should be the same as ds1...

# FUNCTIONS
#
# File Backups
#-------------
# never delete files, only rename 
#
# https://stackoverflow.com/questions/13852700/create-file-but-if-name-exists-add-number
def uniquify(path):
    # replicates win 10 behavior
    filename, extension = os.path.splitext(path)
    counter = 2
    while os.path.isfile(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1
    return path

# if file exists, move to file#number backup
def uniquify_move(path):
    if os.path.isfile(path):
        os.rename(path, uniquify(path))

def f_exists(filelist):
    found=True
    for f in filelist:
        if not os.path.isfile(f):
            print("File "+f+" not found! [102]")
            found=False
    if not found:
        return False
    else:
        return True

# 2. Check prerequisites

# SIMPLE FILE-DEPENDENCY CHECK:
#-------------

files_needed=[ds1name, mapjsonfile, maplistfile, "Win_DS1Edit.exe", "Win_DS1Export.exe"]

if not f_exists(files_needed):
    print("Please make sure all files are in the same folder as this script. [103]")
    if not os.path.isfile(mapjsonfile):
        print("The .json files from D2R can be found at data\\hd\\env\\preset\\ ...")
    exit()
else:
    print("All files found. Dependencies OK.")

 
# 3. maplist.txt
#-------------
#
# Parse maplist file   (DS1Edit args)
print("Getting info for "+ ds1name +"...")

found=False
with open(maplistfile) as input_data:
    for line in input_data:
        #print(line)
        if line.startswith(ds1name.lower()):
            #print(line.split("\t")[1])
            maplist=line.split("\t")
            par1=maplist[3]
            par2=maplist[4].strip()
            print("Found "+ maplistfile+" in maplist. (LvlTypeID "+str(par1)+", LvlPrestDef "+str(par2)+")")
            found=True
if not found:
    print(ds1name+" not found! [104]\n\n")
    exit()

# 4. Win_DS1Export.exe
#---------------------
#
# a modified Win_DS1Edit that provides the data we will need (via stdout/debugfile)
#
print("Starting WinDS1Edit: A window will popup and close - that's ok.\n")
#cmd = "Win_DS1Export.exe "+ds1name+" "+par1+" "+par2.strip()+" > "
#+ " \"t_debug.txt\""
#print(cmd)
RunEditor=subprocess.run(["Win_DS1Export.exe ",ds1name,par1,par2.strip()],capture_output=True, text=True)
#,stdout="t_debug.txt")

#print("type runeditor:"+str(type(RunEditor.stdout)))
#print("runeditor:"+RunEditor.stdout)


debugfile=RunEditor.stdout
errorfile=RunEditor.stderr.splitlines()
for line in errorfile:
    #print("linestart")
    #print(line)
    if line.startswith("txt_read_in_mem"):
        if "Objects.txt not found" in line:
            print("\n\n\nObjects.txt not found!")
            print("Please configure your Win_DS1Edit first before using this tool. [105]")
            exit()
#print(errorfile)

# ----------------
# reads stdout / debug file

walkable=[]
metadatacsv=[]
gobjects=[]

#with open(debugfile) as input_data:
with StringIO(debugfile) as input_data:
    # Skips text before the beginning of the interesting block:
    for line in input_data:
        if line.strip() == 'StartReadoutMetaData':
            break
    # Reads text until the end of the block:
    for line in input_data:
        if line.strip() == 'EndReadoutMetaData':
            break
        metadatacsv.append(line.split(","))
    for line in input_data:
        if line.strip() == 'StartReadoutWalkable': 
            break
    for line in input_data:
        if line.strip() == 'EndReadoutWalkable':
            break
        walkable.append(line.split(","))
    # Skips text before the beginning of the interesting block:
    for line in input_data:
        if line.strip() == 'StartReadoutObjects': 
            break
    for line in input_data:
        if line.strip() == 'EndReadoutObjects':
            break
        #objdata+=line
        gobjects.append(line.split(","))


# 5.1 Metadata / map size
#--------------
#
# RECEIVE  METADATA
#
# array/ map size, 
#
act = w = h = 0

# normal map size provided by ds1Edit debug output
for row in metadatacsv:
    if row:
        w=int(row[2])
        h=int(row[3])
        # ds1name=row[4]
        # act=int(row[5])

# fallback for dynamic size calc

if w<3 or h<3:
    print("fallback: trying to calc height and width")
    for rowcheck in walkable:
        if rowcheck: 
            if int(rowcheck[1])>w:
                w=int(rowcheck[1])
            if int(rowcheck[2])>h:
                h=int(rowcheck[2])

yheight=h*5
xwidth =w*5
iyheight=yheight-1
ixwidth=xwidth-1

print("Map Size (tiles): ", w,"x", h )
print("Map Size (subtiles): ",xwidth,"x", yheight)

# 5.2 Walkable info
# ===================
#
# (this works... finally!)
#
# example-row: "xy i:,47,40,nw,0,nw,1,nw,2,nw,3,nw,4,nw,5,nw,6,nw,7,nw,8,nw,9,nw,10,nw,11,nw,12,nw,13,nw,14,nw,15,nw,16,nw,17,nw,18,nw,19,nw,20,nw,21,nw,22,nw,23,nw,24"
# (Written by patched DS1Editor to debug file)
#
#  xy= classic coords of normal tiles/cells in ds1.
# nj / nw = nojump/nowalk-info for subtile. 
# i = subtile-id from current xy-maintile.
# 3d bool array:
# 
# maparray 0 1 2
#  split into:
#
# nojump:  bool    multimap[0][y][x] ( neighbors[0][y][x] )
# nowalk:  bool    multimap[1][y][x] ( neighbors[1][y][x] )
#
# game-objects: bool objarray[y][x]
#
#
# bool multimap.zeros(([4],yheight, xwidth), dtype=bool)

#
# objarray int because of id info



multimap = np.zeros((2,yheight, xwidth), dtype=bool)
# bool  multimap np.zeros(([4],yheight, xwidth), dtype=bool)
#
#   [0] nojump,
# [1] no walk


cnt=0
cnt2=0
# converts walkable info to array
for row in walkable:
    if row:                 #filter blank lines...
        if len(row) > 3:     #skip cells w/o nowalk info
            #print(row[3])
            bx=int(row[1])*5
            by=int(row[2])*5
            for i in range(4, len(row)+1, 2):
                rowpure=int(row[i])         # values 0-24
                linecnt=rowpure//5          #   0//5 = 0 in python3
                subx=bx+rowpure%5
                suby=by+linecnt
                # print(row[1],row[2],row[3],row[4],", i",row[i],subx,suby,linecnt)
                '''
                if (maparray[suby][subx]!=0):
                    print("Tried to overwrite written value!! at x", row[1],", y", row[2],", i", i,", rowp", row[i+1], \
                           "rowval", rowval,", subx", subx,",suby", newy,", linecnt", linecnt, \
                           "!! array val already ", maparray[subx][newy] )
                    break
                    '''
                if int(row[i-1])==0:    #nojump flag
                    #maparray[suby][subx]=2
                    multimap[0][suby][subx]=1
                    cnt+=1
                else:                   #nowalk flag
                    #print(subx,suby)
                    #maparray[suby][subx]=1
                    multimap[1][suby][subx]=1  
                    cnt2+=1

print("Initial walk-mesh: "+ str(cnt+cnt2)+ " ("+str(cnt)+" nojump,"+ str(cnt2) +" nowalk flags)")
#https://stackoverflow.com/questions/26363579/how-to-find-neighbors-of-a-2d-list-in-python/26363975



# 5.2.1 OPTIMIZE WALKABLE DATA
# ========
# reduce amount of cubes (performance & practicality):
#
# I tried to use  scipy.signal.convolve2d  but it seemed to "aggressive" to me.
print("Optimizing walk-mesh data...")

skipnext=False   # for a small speedup

neighbors = np.zeros((2,yheight, xwidth), dtype=bool)
# bool  neighbors = np.zeros((2,yheight, xwidth), dtype=bool)
# a 2nd array that helps searching surrounding subtiles for cubes
# [0] neighbors nojump
# [1] neighbors nowalk


# OPTIMIZE1. FIND LARGE PATCHES OF SPACE 
#           AND REDUCE THEM TO OUTLINES

for i in range(0,2):   # 1st loop: jump, 2nd: walk
    # when multimap active: walkjump=1
    # for i in ... range(0,2)
    # replace multimap[i] with multimap[i]
    skipnext=0 
    for x in range(1,ixwidth):   #  ((ignore outer border and search for 1's (=true) ))  #last line bottom
        if not skipnext and multimap[i][iyheight][x]:
            if multimap[i][iyheight][x+1] and \
               multimap[i][iyheight-1][x+1]:
                if multimap[i][iyheight  ][x-1] and \
                   multimap[i][iyheight-1][x-1] and \
                   multimap[i][iyheight-1][x]:
                    neighbors[i][iyheight][x]=1
            else:
                skipnext=1
        else:
            skipnext=0
    skipnext=0
    for x in range(1,ixwidth):  #first line top
        if not skipnext and multimap[i][0][x]:
            if multimap[i][0][x+1] and \
               multimap[i][1][x+1]:
                if multimap[i][0][x-1] and \
                   multimap[i][1][x-1] and \
                   multimap[i][1][x]:
                    neighbors[i][0][x]=1
            else:
                skipnext=1
        else:
            skipnext=0
    skipnext=0
    #main stuff
    for y in range(1,iyheight):      #top2bottom
        for x in range(1,ixwidth):  #left2right
            if not skipnext and multimap[i][y][x]:
                if multimap[i][y-1][x+1] and \
                   multimap[i][y  ][x+1] and \
                   multimap[i][y+1][x+1]:
                    if multimap[i][y-1][x-1] and \
                       multimap[i][y  ][x-1] and \
                       multimap[i][y+1][x-1] and \
                       multimap[i][y-1][x]   and \
                       multimap[i][y+1][x]:
                        neighbors[i][y][x]=1
                else:
                    skipnext=1
            else:
                skipnext=0
        skipnext=0     #next line starts fresh...
    skipnext=0
    for y in range(1,iyheight):      #top2bottom  vert0  #sideborders
        if not skipnext and multimap[i][y][0]:
            if multimap[i][y+1][0] and \
               multimap[i][y+1][1]:
                if multimap[i][y-1][0]  and \
                   multimap[i][y-1][1] and \
                   multimap[i][y  ][1]:
                    neighbors[i][y][0]=1
            else:
                skipnext=1
        else:
            skipnext=0
    skipnext=0
    for y in range(1,iyheight):      #top2bottom  vertmax #sideborders
        if not skipnext and multimap[i][y][ixwidth]:
            if multimap[i][y+1][ixwidth] and \
               multimap[i][y+1][ixwidth-1]:
                if multimap[i][y-1][ixwidth] and \
                   multimap[i][y  ][ixwidth-1] and \
                   multimap[i][y-1][ixwidth-1]:                   
                    neighbors[i][y][ixwidth]=1
            else:
                skipnext=1
        else:
            skipnext=0


# writes back changes to multimap
# probably inefficient... but works...
cnt=0
for i in range(0,2):    # 0=nojump, 1=nowalk
    for y in range(0,yheight):
        for x in range(0,xwidth):
            if neighbors[i][y][x]:
                multimap[i][y][x]=0
                cnt+=1
#print("cnt4="+str(cnt))

# neighbors: 2nd array helps searching for surrounding subtiles
#search linesx
#neighbors[0][...]=neighbors[1][...]=0

#
# OPTIMIZE2. If horizontal&vertical line: delete every 2nd occurence
for i in range(0,2):    # 0=nojump, 1=nowalk
    skipnext=0
    for y in range(1,iyheight-1):      #top2bottom
        for x in range(1,ixwidth-1):  #left2right
            if not skipnext and multimap[i][y][x]:
                    if multimap[i][y][x+1] and multimap[i][y][x-1]:              # horizontal line?
                        neighbors[i][y][x]=1
                        skipnext=1
            else:
                skipnext=0
        skipnext=0              #next outer iteration starts fresh 
    skipnext=0      #search linesY
    for x in range(1,ixwidth-1):  #left2right
        for y in range(1,iyheight-1):      #top2bottom
            if not skipnext and multimap[i][y][x]:
                    if multimap[i][y+1][x] and multimap[i][y-1][x]:              # vert line?
                        neighbors[i][y][x]=1
                        skipnext=1
            else:
                skipnext=0
        skipnext=0              #next outer iteration starts fresh 
#    print("run"+str(walkjump))


# writeback collected info / cleanup crowded areas
# probably inefficient... but works...
cnt=0
for i in range(0,2):    # 0=nojump, 1=nowalk
    for y in range(0,yheight):
        for x in range(0,xwidth):
            if neighbors[i][y][x]:
                multimap[i][y][x]=0
                cnt+=1
            #print("maparrayidx", it.multi_index[0], it.multi_index[1])
#print("cnt5="+str(cnt))

# rotate/transform and flip to match json, obv.:
# (needs to reset all arrays because shape changes: h x w  to  w x h)
#neighbors=np.zeros((2, xwidth, yheight), dtype=np.int8)
neighbors=np.zeros((2, xwidth, yheight), dtype=bool)
#multimapr=np.zeros((2, xwidth, yheight), dtype=np.int8)
multimapr=np.zeros((2, xwidth, yheight), dtype=bool)

multimapr[0]=np.fliplr(np.rot90(multimap[0], axes=(1, 0)))
multimapr[1]=np.fliplr(np.rot90(multimap[1], axes=(1, 0)))



# finally, profit...
#nojump file

if csvmap:
    with open(cvsnojump, "wb") as output:
        #np.savetxt(output, multimap[0].astype(int), fmt='%i', delimiter=",")
        np.savetxt(output, multimapr[0].astype(int), fmt='%i', delimiter="")

# finally, profit...
#nowalk file
if csvmap:
    with open(cvsnowalk, "wb") as output:
        #np.savetxt(output, multimap[1].astype(int), fmt='%i', delimiter=",")
        np.savetxt(output, multimapr[1].astype(int), fmt='%i', delimiter="")



# 5.4 Objects info
#=================
#
# map objects to array (objarray)
#
# easier to handle for rotation and flipping
#
# example-rows: 
# object xy #drawing_order/uid dt1id type path act description_str:, 205, 50, 5, 1, 2, 0, 1, torch 1 tiki (37)
#
# (Written by patched DS1Editor to debug file)
#
#  xy= prob subtiles/cells.
# 'id' might be of interest for description...
#
# ToDo: get a list of all npcs (+commoners?) and draw them with the test-barb 
#  - shouldn't waste too much ressources if we use the same model f everything


cnt=1

objarray=np.zeros((yheight, xwidth), dtype=np.int8)
for row in gobjects:
    subx=int(row[1])
    suby=int(row[2])
    objarray[suby][subx]=cnt     # = pseudo-uid
    cnt+=1

if cnt==1:
    print("WARNING: No object info found!")

#rotate and flip to match json, obv.:
#   UNCOMMENTIN  FLIP ROTATE MIRROR    
objarrayr=np.zeros((xwidth, yheight), dtype=np.int8)
objarrayr=np.fliplr(np.rot90(objarray, axes=(1, 0)))


# 6. JSON objects
#====================
#
# done: 
# 1st: create json-entities/data *sigh* - done! yay!
# 2nd integrate in preset/map json - done! yay!
# 
# (far) future ideas: create lines(s. shapes?) by resizing the cubes to reduce # entities
#
# load entities from seperate json file? -> change unity SaveJson.cs ....
# add object infos from WinDS1E.... & link some basic models... XD
# ...like this is a tree, thats 
# ..... oh, how about tile info for roads-tiles? *sigh*
# ... special tiles... (entry)

cubetemplate="""[{"type":"Entity","name":"unitcube","id":1619649645900,"components":[{"type":"TransformDefinitionComponent","name":"test_cube_02_00_components_TransformDefinitionComponent","position":{"x":0.0,"y":0.0,"z":0.0},"orientation":{"x":0.0,"y":0.0,"z":0.0,"w":1.0},"scale":{"x":1.0,"y":1.0,"z":1.0},"inheritOnlyPosition":false},{"type":"ModelDefinitionComponent","name":"UnitCube_ModelDefinitionComponent","filename":"data/hd/env/model/utility/unitcube.model","visibleLayers":1,"lightMask":19,"shadowMask":3,"ghostShadows":false,"floorModel":false,"terrainBlendEnableYUpBlend":false,"terrainBlendMode":1}]}]"""

''' uncompressed:
[ {
			"type": "Entity",
			"name": "unitcube",
			"id": 1619649645900,
			"components": [
				{
					"type": "TransformDefinitionComponent",
					"name": "unitcube_00_components_TransformDefinitionComponent",
					"position": {
						"x": 0.0,
						"y": 0.0,
						"z": 0.0
					},
					"orientation": {
						"x": 0.0,
						"y": 0.0,
						"z": 0.0,
						"w": 1.0
					},
					"scale": {
						"x": 1.0,
						"y": 1.0,
						"z": 1.0
					},
					"inheritOnlyPosition": false
				},
				{
					"type": "ModelDefinitionComponent",
					"name": "UnitCube_ModelDefinitionComponent",
					"filename": "data/hd/env/model/utility/unitcube.model",
					"visibleLayers": 1,
					"lightMask": 19,
					"shadowMask": 3,
					"ghostShadows": false,
					"floorModel": false,
					"terrainBlendEnableYUpBlend": false,
					"terrainBlendMode": 1
				}
			]
		} ]
'''

finetuningx=1
finetuningy=1
cubecollector=[]


# NO JUMP NO WALK into JSON

# here, python raised hell to overwrite ALL entities with the last one...
linecnt=0
scaley=6



#protocube=json.loads(cubetemplate)

for i in range(0,2): 
    itcollect = np.nditer(multimapr[i], flags=['multi_index'])

    while not itcollect.finished:
        onecube=json.loads(cubetemplate)
        if i == 0:      #nojump
            scaley=2
            posy=3
            nfostr="nojump"
        elif i == 1:      #nowalk
            scaley=1
            posy=1
            nfostr="nowalk"
        if (i == 0 and itcollect[0] == 1) or (i == 1 and itcollect[0] == 1):
            onecube[0]['id']="123456700"+str(itcollect.iterindex)
            onecube[0]['name']=nfostr+"_" + str(linecnt)
            linecnt+=1
            #print(itcollect[0])
            #print(itcollect.multi_index[0],'nj')
            onecube[0]['components'][0]['position']['x']=(itcollect.multi_index[0]+finetuningx)*2
            onecube[0]['components'][0]['position']['y']=posy
            onecube[0]['components'][0]['position']['z']=(itcollect.multi_index[1]+finetuningy)*2
            onecube[0]['components'][0]['scale']['y']=scaley
            cubecollector+=[onecube[0]]
        is_not_finished = itcollect.iternext()

print("Reduced nowalk/nojump to:    " + str(linecnt) + "  (=" + str(len(cubecollector)) + " 3D-Objects)")

# OBJECTS to JSON


linecnt=1
rowid=1
itcollectobj = np.nditer(objarrayr, flags=['multi_index'])
while not itcollectobj.finished:
    if itcollectobj[0] >0:
        rowid=itcollectobj[0]-1
        #rowid=0
        #onecube=json.loads(cubetemplate)
        onecube=json.loads(cubetemplate)
        onecube[0]['id']="123456700"+gobjects[rowid][3]
        onecube[0]['name']= "ds1obj_"+gobjects[rowid][8] + "__#" + gobjects[rowid][3] + "__x" + gobjects[rowid][1] + "y"+gobjects[rowid][2]
        linecnt+=1
        #print(itcollect[0])
        #print(itcollect.multi_index[0],'nj')
        onecube[0]['components'][0]['position']['x']=(itcollectobj.multi_index[0]+finetuningx)*2
        onecube[0]['components'][0]['position']['y']=2
        onecube[0]['components'][0]['position']['z']=(itcollectobj.multi_index[1]+finetuningy)*2
        onecube[0]['components'][0]['scale']['x']=3
        onecube[0]['components'][0]['scale']['y']=scaley
        onecube[0]['components'][0]['scale']['z']=3
        cubecollector+=[onecube[0]]
    is_not_finished = itcollectobj.iternext()

print("Game objects added: ", linecnt, "\n")

# 7. Results

#merge with level json?
if mergejson:
    mapjsonfileout=basename+"_unity.json"
    with open(mapjsonfile) as f:
        jsonlevel = json.load(f)
        #mapjsonfileout= jsonlevel
        print("Data gets merged into ", mapjsonfileout)
else:
    jsonlevel=json.loads("{\"entities\": []}")  # empty file for discrete output (no other level data)
    mapjsonfileout=basename+mapjsoninfo
    print("Infos are saved to ", mapjsonfileout)

jsonlevel['entities']+=cubecollector
with open(mapjsonfileout, 'w') as f:
    json.dump(jsonlevel, f)
print("Script finished.")