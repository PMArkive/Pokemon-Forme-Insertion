This program automates the forme insertion for XY, ORAS, and USUM that was initially developed by Axyn for XY.

The interface is rather primitive, I threw this together in two lengthy sessions over the course of two days, it's the fanciest GUI I've made by far thus far.

Instructions:

0) Keep an eye on the text window, if anything goes wrong you will (hopefully) see errors I can use to identify and fix the problem there, and you will also get some feedback on what it's doing.

1) Select game from dropdown menu.

2a) Select the paths to your extracted Model, Personal, Levelup, and Evolution GARC folders. The file dialog will tell you which GARC you are looking for based on your selected game. Following this, you can save your paths into a config file, so you can use those settings every time you work on this particular game.

2b) Alternately, simply load a previously made config.

3) Select the the base Species you are adding Forme(s) to. You can search for the desired Pokemon in the text box, choose it by double-clicking the menu below (I coded almost the entire thing before I learned that tkinter doesn't have a module for the modern "type into the dropdown menu to narrow things down" thing, so I used this hacky setup until one is added or I find a nicer implementation).

4) By default, this program will copy the Personal, Levelup, and Evolution files from the base forme of the selected species to set things up. If you want to copy any of those from a different Pokemon, deselect the "Same as species" options above the desired custom selector, and select the desired source. For Model, the models are all in the form <Pokemon name> <number>, where <Pokemon> 0 is the base forme. Consult a table of the model order to determine which one you want (I left it... barebones to make it easier to work with hacks with random formes already added). For the other three, you can select any source Forme, with the same format as pk3ds (base forme is just <Pokemon>, alt formes are <Pokemon> <number starting from 1>).

5) Enter the number of formes you want to add for the selected Pokemon

6) Hit "Insert Forme(s)"

7) Rebuild your Personal, Levelup, and Evolution GARCs, then *close Pk3ds* and return them to their appropriate locations in the romfs file structure.

8) Load Pk3ds and confirm that the formes are properly inserted. If so, you may now edit the new formes as desired.

9) The new model files (8 (gen VI) or 9 (gen VII) files) will be inserted after every other existing files for that Pokemon species. I recommend keeping track of what is where in a spreadsheet. You can edit them (note that in gen VII only texture files can be reinserted at this time), rebuild the model file, and reinsert that as well. However, the game will run and function without that - the newly added formes will default to using their base forme's model, texture, and animation files.