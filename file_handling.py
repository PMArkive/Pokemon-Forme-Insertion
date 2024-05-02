from re import A, M
import shutil
import os
import mmap
import sys
import errno
from tkinter.filedialog import askdirectory, asksaveasfilename
from my_constants import *



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

#check if file is zeroed out
def file_is_zero(string):
    with open(string) as file:
        return not any(map(ord,file.read()))
		
#convert integer to little endian as long as two bytes at most
def little_endian_chunks(big_input):
    small_byte = big_input%256
    large_byte = (big_input - small_byte)/256
    
    if(large_byte > 255 or not(small_byte.is_integer() and large_byte.is_integer())):
        print(big_input, " is too big, little endian conversion error")
        return
    else:
        return([hex(small_byte), hex(large_byte)])
    

#updated target Personal file with new Forme Count and First Forme Pointer
def personal_file_update(target_index, new_forme_count, start_location):
    #open target personal file
    with open(file_namer(personal_path, target_index, personal_filename_length, extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
            personal_hex_map[0x20] = hex(new_forme_count)
            personal_hex_map[0x1C], personal_hex_map[0x1D] = little_endian_chunks(start_location)
            

#rebuilds personal compilation file
def concatenate_bin_files(folder_path):

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
    
    with open('temp_personal_compilation.bin', 'wb') as output_stream:
        output_file = str(len(dir_list)).zfill(pad_count) + '.bin'
        
        
        for file_name in dir_list:
            file_path = os.path.join(folder_path, file_name)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    data = file.read()
                    output_stream.write(data)
        
    print('New compilation file created')
    os.rename('temp_personal_compilation.bin', os.path.join(folder_path, output_file))
    print('New compilation file placed in folder')

def update_model_list():
    #open model header
    #same as below, reference game for species name, call them as <species> <number>
base_species_list =  ["Bulby", "Ivy", "Venu"]
master_formes_list = ["Bulby", "Ivy", "Venu"]
model_source_list = ["Bulby", "Ivy", "Venu"]

def update_species_list():
    #open personal
    #open each file until max species, note pointer and forme count
    #reference hardcoded list to spit out <species> <number> like pk3ds
    #just load the relevant file for the base_species list


#loads list of filenames in extracted GARC if it exists, otherwise return empty array
def load_GARC(garc_path, target, gameassert):
    global personal_path
    global levelup_path
    global evolution_path
    global model_path
    global game
    global max_species_index
    global personal
    global levelup
    global evolution
    global model
    
    global personal_filename_length
    global evolution_filename_length
    global levelup_filename_length
    global model_filename_length
    if(os.path.exists(garc_path)):
        temp = os.listdir(garc_path)
    
        if(len(temp) > 0):
            game = gameassert
            match target:
                case "Model":
                    model_path = garc_path
                    model = temp
                    model_filename_length = len(temp[0]) - 4
                    update_model_list()
                case "Personal":
                    personal_path = garc_path
                    personal = temp
                    personal_filename_length = len(temp[0]) - 4
                    update_species_list()
                case "Levelup":
                    levelup_path = garc_path
                    levelup = temp
                    levelup_filename_length = len(temp[0]) - 4
                case "Evolution":
                    evolution_path= garc_path
                    evolution = temp
                    evolution_filename_length = len(temp[0]) - 4
            match game:
                case "XY":
                    max_species_index = 721
                case "ORAS":
                    max_species_index = 721
                case "USUM":
                    max_species_index = 807
    else:
        print("Garc folder not found, unreadable, or empty")
    

def choose_GARC(target, gameassert):

    targetpath = ''
    match gameassert:
        case "XY":
               match target:
                   case "Model":
                       targetpath = '007'
                   case "Personal":
                       targetpath = '218'
                   case "Levelup":
                       targetpath = '214'
                   case "Evolution":
                       targetpath = '215'
        case "ORAS":
               match target:
                   case "Model":
                       targetpath = '008'
                   case "Personal":
                       targetpath = '195'
                   case "Levelup":
                       targetpath = '191'
                   case "Evolution":
                       targetpath = '192'
        case "USUM":
               match target:
                   case "Model":
                       targetpath = '094'
                   case "Personal":
                       targetpath = '017'
                   case "Levelup":
                       targetpath = '013'
                   case "Evolution":
                       targetpath = '014'
                       
    folder_path = askdirectory(title='Select extracted ' + target + ' Garc Folder, a' + targetpath)
    
    load_GARC(folder_path, target, gameassert)


                
def load_game_cfg():
    
    game_cfg_path = askdirectory(title='Select saved cfg file')
    
    global game
    global personal_path
    global levelup_path
    global evolution_path
    global model_path
    global max_species_index
    
    cfg_array = []
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
    9 = max species index
    '''
    
    with open(game_cfg_path, "r") as cfg:
        cfg_array = [line.rstrip() for line in cfg]
    
    game = cfg_array[0]
    personal_path = cfg_array[1]
    levelup_path = cfg_array[2]
    evolution_path = cfg_array[3]
    model_path = cfg_array[4]
    #evolution = cfg_array[5]
    #evolution = cfg_array[6]
    #evolution = cfg_array[7]
    #evolution = cfg_array[8]
    max_species_index = cfg_array[9]
    extracted_extension = '.bin'
    

    load_GARC(personal_path, "Personal", game)
    load_GARC(levelup_path, "Levelup", game)
    load_GARC(evolution_path, "Evolution", game)
    load_GARC(model_path, "Model", game)
    

def save_game_cfg():
 
    game_cfg_path = asksaveasfilename(title='Select location to save cfg file', defaultextension='.cfg',filetypes= [('config','.cfg')])
    
    
    cfg_array = []
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
    9 = max species index
    '''
    
    with open(game_cfg_path, "w") as cfg:
        cfg.write(game + '\n')
        cfg.write(personal_path + '\n')
        cfg.write(levelup_path + '\n')
        cfg.write(evolution_path + '\n')
        cfg.write(model_path + '\n')
        cfg.write('\n')#evolution = cfg_array[5]
        cfg.write('\n') #evolution = cfg_array[6]
        cfg.write('\n')#evolution = cfg_array[7]
        cfg.write('\n')#evolution = cfg_array[8]
        extracted_extension = '.bin'