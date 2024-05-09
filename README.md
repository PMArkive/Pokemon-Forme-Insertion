This program automates the forme insertion for XY, ORAS, and USUM that was initially developed by Axyn for XY.

The interface is rather primitive, I threw this together in two lengthy sessions over the course of two days, it's the fanciest GUI I've made by far thus far.

Notes and Warnings:

	1) Keep an eye on the text window, if anything goes wrong you will (hopefully) see errors I can use to identify and fix the problem there, and you will also get some feedback on what it's doing.
	
	2) If you are editing USUM, please do not give Dusk-Rockruff its own model (this is not possible with this tool, you would have to do it manually). It is the only forme without its own model and I had to account for that. Similarly, if you have manually inserted Formes but not yet inserted Models for them, this tool will malfunction. I plan to add an automated fix-function that will run and insert models for any such it detects just to avoid problems, at which point I will delete this.


Instructions:

	Preparation:
		0) If you have previously followed steps 1 to 4, you can just use "Load CFG" to load your previously saved config and CSV file. (If you are upgrading from a pre-CSV version, execute steps 3 and 4 after loading your CFG and you should be good).
	
		1) Select game from dropdown menu.

		2) Select the paths to your extracted Model, Personal, Levelup, and Evolution GARC folders. The file dialog will tell you which GARC you are looking for based on your selected game. Following this, you can save your paths into a config file, so you can use those settings every time you work on this particular game. When you extract your Model GARC, please do not decompress it.

		3) Click "Create/Reset CSV", then "Save CSV" to select a location to save it. This will record all the inserted formes, their indices in Personal, and what Model files correspond to which Pokemon Forme. When you create the CSV, it will do so with the appropriate Forme names. Once you insert your formes, you can open the CSV and enter your custom forme names (it will give the new formes numerical designations). If you later use this tool to insert more formes, it will load your custom names. You can also change any stock forme name as desired.
		
		4) Click "Save CFG & CSV" to save the selected game and filepaths.

	4) Select the the base Species you are adding Forme(s) to. You can search for the desired Pokemon in the text box, choose it by double-clicking the menu below (I coded almost the entire thing before I learned that tkinter doesn't have a module for the modern "type into the dropdown menu to narrow things down" thing, so I used this hacky setup until one is added or I find a nicer implementation).

	4) By default, this program will copy the Personal, Levelup, and Evolution files from the base forme of the selected species to set things up. If you want to copy any of those from a different Pokemon, deselect the "Same as species" options above the desired custom selector, and select the desired source. For Model, the models are all in the form <Pokemon name> <number>, where <Pokemon> 0 is the base forme. Consult a table of the model order to determine which one you want (I left it... barebones to make it easier to work with hacks with random formes already added). For the other three, you can select any source Forme, with the same format as pk3ds (base forme is just <Pokemon>, alt formes are <Pokemon> <number starting from 1>).

	5) Enter the number of formes you want to add for the selected Pokemon

	6) Hit "Insert Forme(s)"

	7) Rebuild your Personal, Levelup, and Evolution GARCs, then *close Pk3ds* and return them to their appropriate locations in the romfs file structure.

	8) Load Pk3ds and confirm that the formes are properly inserted. If so, you may now edit the new formes as desired.

	9) The new model files (8 (gen VI) or 9 (gen VII) files) will be inserted after every other existing files for that Pokemon species. I recommend keeping track of what is where in a spreadsheet. You can edit them (note that in gen VII only texture files can be reinserted at this time), rebuild the model file, and reinsert that as well. However, the game will run and function without that - the newly added formes will default to using their base forme's model, texture, and animation files.