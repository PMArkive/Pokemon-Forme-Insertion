import os
import errno
import tkinter as tk
from tkinter.filedialog import askdirectory
import shutil
import mm

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
personal = []
levelup = []
evolution = []
model = []

#boolean to see if all is well
good_to_go_bool = False



#rebuilds personal compilation file
def concatenate_bin_files(folder_path, 'temp_personal_compilation.bin'):

    generation = 7
    pad_count = 4
    max_binary_file = 9999
    
    
    #grab list of filenames inside folder
    dir_list = os.listdir(folder_path)
    
    #check to see gen. Gen 6 has 3 char, 7 has 4, with extension is 7 and 8
    if(len(dir_list[0]) == 8):
        generation = 7
        pad_count = 4
        max_binary_file = 9999
    elif(len(dir_list[0]) == 7):
        generation = 6
        pad_count = 3
        max_binary_file = 999
    else:
        print("Error with filename")
        return
    #check to see if current directory has the compilation file:
    #grab last index
    
    #if length of last element is greater than dec 84, is compilation file (or something is wrong)
    if(os.path.getsize(os.path.join(folder_path, dir_list[-1])) > 84):
        # move the old compilation file to current directory and stick "backup_" in front of it
        os.rename(os.path.join(folder_path, dir_list[-1]), 'backup_' + dir_list[-1])
        print('Backed up old compilation file')
        
        #remove compilation file from dir_list
        del dir_list[-1]
    
    print(len(dir_list)-1, " Pokemon entries detected.")
    
    with open(temp_file, 'wb') as output_stream:
        output_file = str(len(dir_list)).zfill(pad_count) + '.bin'
        
        
        for file_name in dir_list:
            file_path = os.path.join(folder_path, file_name)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    data = file.read()
                    output_stream.write(data)
        
    print('New compilation file created')
    os.rename(temp_file, os.path.join(folder_path, output_file))
    print('New compilation file placed in folder')


#convert integer to little endian as long as two bytes at most
def little_endian_chunks(big_input):
    small_byte = big_input%256
    large_byte = (big_input - small_byte)/256
    
    if(large_byte > 255 or not(is_integer(small_byte) and is_integer(large_byte))):
        print(big_input, " is too big, little endian conversion error")
        return
    else:
        return([hex(small_byte), hex(large_byte)])


#streamline the file name-calling
def file_namer(folder, index, length, extension):
    return(os.path.join(folder, str(index).zfill(length), 'extension'))

#removes file, exception thrown if not exist
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

#loads list of filenames in extracted GARC if it exists, otherwise return empty array
def load_GARC(garc_path):
    if(os.path.exists(garc_path)):
        return(os.listdir(folder_path))
    else
        return([])

def load_game_cfg(game_cfg_path):
    '''read all the lines
    0 = game
    1 = Personal
    2 = Level
    3 = Evolution
    4 = Model/texture
    5 = Sprites_1
    6 = Sprites_2
    7 = portrait_1
    8 = portrait_2
    9 = length of personal filename
    10= length of levelup filename
    11= length of evolution filename
    12= length of model filename
    '''
    
    
    game = cfg_array[0]
    personal_path = cfg_array[1]
    levelup_path = cfg_array[2]
    evolution_path = cfg_array[3]
    model_path = cfg_array[4]
    #evolution = cfg_array[5]
    #evolution = cfg_array[6]
    #evolution = cfg_array[7]
    #evolution = cfg_array[8]
    personal_filename_length = cfg_array[9]
    levelup_filename_length = cfg_array[10]
    evolution_filename_length = cfg_array[11]
    model_filename_length = cfg_array[12]
    extracted_extension = '.bin'
    
    personal = load_GARC(personal_path)
    levelup = load_GARC(levelup_path)
    evolution = load_GARC(evolution_path)
    model = load_GARC(model_path)
    
    if(len(personal) - 2 == len(levelup) - 1 == len(evolution) - 1 and len(model) >= len(personal)*9):
        good_to_go_bool = True


#updated target Personal file with new Forme Count and First Forme Pointer
def personal_file_update(target_index, new_forme_count, start_location):
    #open target personal file
    with open(file_namer(personal_path, target_index, personal_filename_length, extracted_extension), "r+b") as f:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_map_temp:
            personal_hex_map[0x20] = hex(new_forme_count)
            personal_hex_map[0x1C], personal_hex_map[0x1D] = little_endian_chunks(start_location)


def add_new_forme_execute(base_form, existing_formes_array = [], start_location, new_forme_count, model_source_index, personal_source_index = base_form, levelup_source_index = base_form, evolution_source_index = base_form):
    
    
    #Part 1, Personal file, update existing Personal blocks with new forme count and pointer
    personal_file_update(base_form, new_forme_count, start_location)
    
    for pokemon in existing_formes_array:
        personal_file_update(pokemon, new_forme_count, start_location)
        
    #for Levelup, evo, and Personal, move existing formes if needed. We need to delete existing files if they are there, then copy them to the new location, then overwrite the old spot with zeroes
    #offset starts from 0, which is the first forme that is at index start_location
    for offset, pokemon in enumerate(existing_formes_array):
    
        #delete target spots if they exist (only happens if filling a spot cleared by moving something else)
        silentremove(file_namer(personal_path, start_location + offset, personal_filename_length, extracted_extension))
        silentremove(file_namer(evolution_path, start_location + offset, evolution_filename_length, extracted_extension))
        silentremove(file_namer(levelup_path, start_location + offset, levelup_filename_length, extracted_extension))

        #copy personal file to new location
        shutil.copy(file_namer(personal_path, pokemon, personal_filename_length, extracted_extension), file_namer(personal_path, start_location + offset, personal_filename_length, extracted_extension))
        
        #zero out old personal block
        with open(file_namer(personal_path, pokemon, personal_filename_length, extracted_extension), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
            personal_hex_map.flush
            personal_hex_map.resize(0x54)
            for x in range(0,0x54):
                personal_hex_map[x] = 0x00
            personal_hex_map.flush
        
        #copy evolution file to new location
        shutil.copy(file_namer(evolution_path, pokemon, evolution_filename_length, extracted_extension), file_namer(evolution_path, start_location + offset, evolution_filename_length, extracted_extension))
        
        #zero out old evolution block
        with open(file_namer(evolution_path, pokemon, evolution_filename_length, extracted_extension), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as evolution_hex_map:
            evolution_hex_map.flush
            for x in range(0,0x40):
                evolution_hex_map[x] = 0x00
            evolution_hex_map.flush
        
        #copy levelup file to new location
        shutil.copy(file_namer(levelup_path, pokemon, levelup_filename_length, extracted_extension), file_namer(levelup_path, start_location + offset, levelup_filename_length, extracted_extension))
        
        #write Tackle at Level 1 to old location (avoid pk3ds crash)
        with open(file_namer(levelup_path, pokemon, levelup_filename_length, extracted_extension), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as levelup_hex_map:
            levelup_hex_map.flush
            levelup_hex_map.resize(0x08)
            levelup_hex_map[0] = 0xED
            levelup_hex_map[1] = 0x00
            levelup_hex_map[2] = 0x01
            levelup_hex_map[3] = 0x00
            for x in range(4,0x08):
                levelup_hex_map[x] = 0xFF
            levelup_hex_map.flush
            
    #now initialize the newly added formes
    
    #make sure we start after any existing shifted formes
    new_offset_start = len(existing_formes_array)
    
    for offset in range(0, new_forme_count):
        #user will have specified which existing Forme to copy from
        
        #copy personal file to new location
        shutil.copy(file_namer(personal_path, personal_source_index, personal_filename_length, extracted_extension), file_namer(personal_path, start_location + offset + new_offset_start, personal_filename_length, extracted_extension))
        
        #copy evolution file to new location
        shutil.copy(file_namer(evolution_path, evolution_source_index, evolution_filename_length, extracted_extension), file_namer(evolution_path, start_location + offset + new_offset_start, evolution_filename_length, extracted_extension))
        
        #copy levelup file to new location
        shutil.copy(file_namer(levelup_path, levelup_source_index, levelup_filename_length, extracted_extension), file_namer(levelup_path, start_location + offset + new_offset_start, levelup_filename_length, extracted_extension))
        
        
    
    #rebuild personal compilation file
    concatenate_bin_files(personal_path)
    
    
    
    #create new sets of model files
    #don't forget model index starts from 0 unlike everything else
    #first figure out which files we're copying
    
    
    with open(file_namer(model_path, 0, model_filename_length, extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
            #first need to go to the four bytes for that *species*, which start at (index - 1)*4
            #the fourth byte, (index - 1)*4 + 3, is 0x1 when no formes, 0x3 when only alternate-gender formes, 0x7 when both
            #the third byte is how many models that species has.
            #The first and second bytes are a 2-byte little endian that is the *total number of models up to but not including the first model for that species*. So Bulby is 00 00 01 01 (no models before it), Venusaur is 02 00 03 07 (2 models before it, 3 models for Venusaur (male, female, and Mega), and has both gendered and non-gendered models
            
            4*(base_form - 1) + 2
            
            
            #this is the model we're copying
            model_start_file = 0
            #this is where we have to insert those copies
            model_dest_file = 0
            #this is how many of those files there are per new forme
            model_file_count = 0
            if(game == 'XY'):
                model_start_file = 8*(model_source_index)+4
                model_dest_file = base_form
                model_file_count = 8
            elif(game == "ORAS"):
                #Need someone to check
                model_start_file = 8*(model_source_index)+4
                model_file_count = 8
            #assume USUM
            else:
                model_start_file = 9*(model_source_index)+1
                model_file_count = 9
            
            #copies each of the source model/texture/animation files from A.bin to <last file in source>_<enumeration of new formes>_<file number in sequence>
            for x in range(0, new_forme_count):
                for y in range(0, model_file_count):
                    shutil.copy(file_namer(model_path, model_start_file + y, model_filename_length, extracted_extension), os.path.join(model_path, str(model_start_file + model_file_count).zfill(model_filename_length), "_", str(x).zfill(2), "_", y, '.bin'))
            
    
    