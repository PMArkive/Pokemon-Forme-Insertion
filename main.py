import os
import tkinter as tk
from tkinter.filedialog import askdirectory
import shutil

"""
Five loading buttons:
	a) load 013 (level)
	b) load 014 (evolution)
	c) load 017 (personal)
	d) load 094 (model/texture)
	e1) load config file
	e2) write these paths to config file
	future) Load sprite/portrait
	
f) Read list of 'mon names from some other file

g) Load list of form-links from personal whenever personal is loaded

Once a-d are loaded:
1) Select base-form Pokemon
2) dropdown to select number of formes to add
3) check if there are existing formes. If there are, look for next open spot and send that to step 5, otherwise add to end
4) If multiple formes, dropdown to select which forme to copy from(?)
5) if there are existing formes, move them to spot from 3 and zero out the free spaces
6a) personal, update forme number in each, update pointer in each, call concatenate
6b) initialize in 013 and  014 (copy source file to appropriate name)
7) duplicate source model files, update header (call rejigger)
8) Update sprite/portrait (when we figure out how)

"""

#Global path variables   
personal_path = ''
levelup_path = ''
evolution_path = ''
model_path = ''

#Global file-list arrays
generation = 0
personal = []
levelup = []
evolution = []
model = []

#boolean to see if all is well
good_to_go_bool = False


#loads list of filenames in extracted GARC if it exists, otherwise return empty array
def load_GARC(garc_path):
    if(os.path.exists(garc_path)):
        return(os.listdir(folder_path))
    else
        return([])

def load_game_cfg(game_cfg_path):
    '''read all the lines
    0 = generation
    1 = Personal
    2 = Level
    3 = Evolution
    4 = Model/texture
    5 = Sprites_1
    6 = Sprites_2
    7 = portrait_1
    8 = portrait_2'''
    
    generation = cfg_array[0]
    personal_path = cfg_array[1]
    levelup_path = cfg_array[2]
    evolution_path = cfg_array[3]
    model_path = cfg_array[4]
    #evolution = cfg_array[5]
    #evolution = cfg_array[6]
    #evolution = cfg_array[7]
    #evolution = cfg_array[8]
    
    personal = load_GARC(personal_path)
    levelup = load_GARC(levelup_path)
    evolution = load_GARC(evolution_path)
    model = load_GARC(model_path)
    
    if(len(personal) - 2 == len(levelup) - 1 == len(evolution) - 1 and len(model) >= len(personal)*9):
        good_to_go_bool = True

def add_new_forme_execute(base_form, existing_formes_array = [], start_location, new_forme_count, personal_source_index = base_form, levelup_source_index = base_form, evolution_source_index = base_form, model_source_index):
    
    
    #modify pointer and base forme count in base form
    
    for i, pokemon in enumerate(existing_formes_array):
        #modify pointer and base forme count in each forme form
        shutil.copy(os.path.join(personal_path, personal[pokemon]), os.path.join(personal_path, '''new file number here, should be start location.bin with appropriate padding'''))