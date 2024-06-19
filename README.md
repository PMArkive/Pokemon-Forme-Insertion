This program automates the forme insertion for XY, ORAS, and USUM that was initially developed by Axyn for XY.

The interface is rather primitive, I threw this together in two lengthy sessions over the course of two days, it's the fanciest GUI I've made by far thus far.

Notes and Warnings:

1) Keep an eye on the text window, if anything goes wrong you will (hopefully) see errors I can use to identify and fix the problem there, and you will also get some feedback on what it's doing.

2) The first time you create your csv file, you might need to save it and reload in order for the additions to populate properly in the window. 

3) If you are coming from a pre 2.0 version, you will be prompted to create a csv when you load your old config file.


Preparation:

0) If you have previously followed steps 1 to 4, you can just use "Load CFG" to load your previously saved config and CSV file. (If you are upgrading from a pre-CSV version, execute steps 3 and 4 after loading your CFG and you should be good).

1) Select game from dropdown menu.

2) Select the paths to your extracted Model, Personal, Levelup, and Evolution GARC folders. The file dialog will tell you which GARC you are looking for based on your selected game. Following this, you can save your paths into a config file, so you can use those settings every time you work on this particular game.

3) Click "Create/Reset CSV", then "Save CSV" to select a location to save it. This will record all the inserted formes, their indices in Personal, and what Model files correspond to which Forme. When you create the CSV, it will do so with the appropriate Forme names. Once you insert your formes, you can open the CSV and enter your custom forme names (it will give the new formes numerical designations). If you later use this tool to insert more formes, it will load your custom names. You can also change any stock forme name as desired.

4) Click "Save CFG & CSV" to save the selected game and filepaths.



Use Instructions:
1) Select the the Species (e.g. Bulbasaur) you are adding Forme(s) to from the leftmost column. You can search for the desired name in the text box, choose it by double-clicking the menu below (I coded almost the entire thing before I learned that tkinter doesn't have a module for the modern "type into the dropdown menu to narrow things down" thing, so I used this hacky setup until one is added or I find a nicer implementation).

2a) By default, this program will copy the Personal, Levelup, and Evolution files from the base forme of the selected species to set things up. If you want to copy any of those from a different specific instance, deselect the "Same as species" options above the desired custom selector, and select the desired source. Inserted formes will be named <Base Species> <#th forme>. Once the CSV file is updated with the inserted formes, you can change that default forme name with a custom one for tracking purposes (this will be reflected in the loaded lists in the tool when the updated CSV file is then reloaded).

2b) If you want to add unique data for an existing cosmetic forme (e.g. Female Venusaur or Pyroar, the different colors of Florges, etc.), uncheck "Initialize Model Files". If the program detects that there are not as many free cosmetic formes for the selected Pokemon as you told it Formes to add, it will report as such in the console and abort.

3) Enter the number of formes you want to insert.

4) Hit "Insert Forme(s)"

5) Rebuild your Personal, Levelup, and Evolution GARCs, then *close Pk3ds* and return them to their appropriate locations in the romfs file structure.

6) Load Pk3ds and confirm that the formes are properly inserted. If so, you may now edit the new formes as desired. Please note that the index numbers of all formes will be sorted by nat dex number (e.g. the first alt-forme will be Venusaur after the last species, instead of Deoxys). This was implemented because the game requires all alternate formes of a given species to have consecutie index numbers, so adding formes to any Pokemon with existing formes requires shuffling around the indices, at which point it was actually simplest to just sort them like this.

7) The new model files (8 (gen VI) or 9 (gen VII) files) will be inserted after every other existing files for that species. The model files are tracked in the generated CSV file.


A tutorial can be found at https://youtu.be/gu5JrxL3v4g
