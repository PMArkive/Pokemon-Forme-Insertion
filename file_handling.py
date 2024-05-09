from ast import excepthandler
from lib2to3.fixes.fix_idioms import TYPE
from re import A, M
import shutil
import os
import mmap
from sqlite3 import Row
from string import printable
import sys
import errno
from time import sleep
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename
from my_constants import *
from numpy import *
import csv



#pull a given non-empty column from the given table and returns the max
def max_of_column(input_table, column_number):
    max_temp = 0
    for rows in input_table:
        if(rows[column_number].isdigit() and int(rows[column_number]) > max_temp):
            max_temp = int(rows[column_number])
    return(max_temp)

#pull non-empty entries from a given column from the given table and returns it
def entire_of_column(input_table, column_number, allow_multiple = True):
    table_temp = []
    last_element = ''
    for rows in input_table:
        if(not(rows[column_number] in {'', "NA"}) and (allow_multiple or rows[column_number] != last_element)):
            table_temp.append(rows[column_number])
        last_element = rows[column_number]
    return(table_temp)

#returns a list of the indices of the rows that contain the specified search term in the specified column
def find_rows_with_column_matching(input_table, column_number, search_term):
    found_table = []
    row_index = 0
    for row_index, rows in enumerate(input_table):
        if(rows[column_number] == search_term):
            found_table.append(row_index)
    return(found_table)

#streamline the file name-calling
def file_namer(folder, index, length, extension):
    return(os.path.join(folder, str(index).zfill(length)) + extension)

#removes file, exception thrown if not exist
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

#check if file is zeroed out
def file_is_zero(string):
    with open(string) as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as personal_hex_map:
            for x in personal_hex_map:
                if(x != 0x0):
                    return(False)
    return(True)
		
#convert integer to little endian as long as two bytes at most
def little_endian_chunks(big_input):
    small_byte = big_input%256
    large_byte = int((big_input - small_byte)/256)
    
    if(large_byte > 255):
        print(big_input, " is too big, little endian conversion error")
        return
    else:
        return(small_byte, large_byte)
    
#updated target Personal file with new Forme Count and First Forme Pointer
def personal_file_update(poke_edit_data, target_index, total_formes, start_location):
    #open target personal file
    with open(file_namer(poke_edit_data.personal_path, target_index, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
            personal_hex_map.flush()
            #print('about to write ', new_forme_count)
            personal_hex_map[0x20] = total_formes
            personal_hex_map[0x1C], personal_hex_map[0x1D] = little_endian_chunks(start_location)
            personal_hex_map.flush()
    return(poke_edit_data)
            
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
        print('Backed up old compilation file to executable\'s directory')
        
        #remove compilation file from dir_list
        del dir_list[-1]
    
    #print(len(dir_list)-1, " Pokemon entries detected.")
    
    with open(os.path.join(folder_path, str(len(dir_list)).zfill(pad_count) + '.bin'), 'wb') as output_stream:
        for file_name in dir_list:
            file_path = os.path.join(folder_path, file_name)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    data = file.read()
                    output_stream.write(data)
    print('New compilation file created')

def update_model_list(poke_edit_data):
    
    #if we haven't loaded the Personal file yet, we will need to do all the rest later
    if(len(poke_edit_data.personal) == 0):
        poke_edit_data.run_model_later = True
        print('Will initialize Model list after the Personal list')
        return
    else:
        poke_edit_data.run_model_later = False
        print('Initializing default Model list')
        
    poke_edit_data.model_source_list = []
    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as model_hex_map:
            #for base formes plus egg at poke_edit_data.max_species_index
            for index in range(1, poke_edit_data.max_species_index + 2):
                #number of model sets this species has
                number_of_models = model_hex_map[(index - 1)*4 + 2]
                #avoid issues of having 'egg' show up in main species list or having to have a second array for everything just with egg at the end
                temp_name = 'Egg'
                if(index != poke_edit_data.max_species_index+1):
                    temp_name = poke_edit_data.base_species_list[index]
                
                #name each model as <Pokemon species> <number>, the base forme is named <Pokemon> 0 so that (in at least most cases) the model-number lines up with the forme-number (where there are multiple)
                for distinct_models in range(0, number_of_models):
                    poke_edit_data.model_source_list.append(temp_name + ' ' + str(distinct_models))
    
    #copy this into the current list to initialize properly (particularly when loading from cfg)
    poke_edit_data.current_model_source_list = poke_edit_data.model_source_list.copy()
    
    #
    if(not(poke_edit_data.run_model_later)):
        poke_edit_data = load_names_from_CSV(poke_edit_data)

    return(poke_edit_data)

def conditional_update_modelless_formes_list(poke_edit_data):
    if(poke_edit_data.modelless_formes == []):
        match poke_edit_data.game:
            case "XY":
                poke_edit_data.modelless_formes = xy_modelless_formes
            case "ORAS":
                poke_edit_data.modelless_formes = oras_modelless_formes
            case "SM":
                poke_edit_data.modelless_formes = sm_modelless_formes
            case "USUM":
                poke_edit_data.modelless_formes = usum_modelless_formes
    return(poke_edit_data)



def update_species_list(poke_edit_data):
    
    #Assume user is either creating new thing, or that this is loading from config, in which case the custom list hasn't loaded yet

    print('Initializing default Species list')
    #set base species list based on which game we're dealing with
    #grab the species name from the master list
    if(poke_edit_data.game == "USUM"):
        poke_edit_data.master_list_csv = usum_master_list_csv.copy()
        poke_edit_data.base_species_list = entire_of_column(usum_master_list_csv, 0, False)
    if(poke_edit_data.game == "SM"):
        poke_edit_data.master_list_csv = sm_master_list_csv.copy()
        poke_edit_data.base_species_list = entire_of_column(sm_master_list_csv, 0, False)
    elif(poke_edit_data.game == "XY" or poke_edit_data.game == "ORAS"):
        poke_edit_data.master_list_csv = xy_master_list_csv.copy()
        poke_edit_data.base_species_list = entire_of_column(xy_master_list_csv, 0, False)
    
        
    #remove the model-only Egg from the end:
    poke_edit_data.base_species_list.pop() 


    #first part of master formes list is just the base species list
    poke_edit_data.master_formes_list = poke_edit_data.base_species_list.copy()
    
    #add appropriate number of spots
    #first find total number of files, then don't count the compilation file
    if(os.path.getsize(file_namer(poke_edit_data.personal_path, poke_edit_data.personal[-1], poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension)) > 84):
        personal_index_count = len(poke_edit_data.personal) - 1
    else:
        personal_index_count = len(poke_edit_data.personal)
        
    print("Initializing default Formes list")
    #adds (total number of pokemon personal files) - (total number of base species) spots to the end of the array
    for x in range(0, personal_index_count - poke_edit_data.max_species_index - 1):
        poke_edit_data.master_formes_list.append('')
        

    #print(poke_edit_data.max_species_index)
    #open personal
    #open each file until max species, note pointer and forme count
    #reference hardcoded list to spit out <species> <number> like pk3ds
    #iterate through the personal files
    for index, file in enumerate(poke_edit_data.personal):
        #since we're filling up the poke_edit_data.master_formes_list by iterating through the base formes, we can stop when we finish the last base Pokemon
        #poke_edit_data.max_species_index is here the first alt forme because off-by-1, so stop here
        if(index == poke_edit_data.max_species_index + 1):
            break
        

        with open(file_namer(poke_edit_data.personal_path, file, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as personal_hex_map:
                #pull # of formes
                forme_count = personal_hex_map[0x20]
                forme_pointer = personal_hex_map[0x1C] + 256*personal_hex_map[0x1D]
                #if more than 1 AND forme pointer not 0, need to update those names in the array
                if(forme_count > 1 and forme_pointer != 0):
                    #this is the internal index number of the first alt forme, less 1 because we're shifted over one
                    
                    #print(index, forme_count, forme_pointer)
                    #first forme in forme count is the base, need to do 1 less than that. We call each forme <base species name> <alt forme count> (e.g. Mega Blastoise is "Blastoise 1")
                    for x in range(0, forme_count - 1):
                        #print(index, forme_count, forme_pointer, x)
                        poke_edit_data.master_formes_list[forme_pointer + x] = poke_edit_data.base_species_list[index] + ' ' + str(x+1)
    #print(poke_edit_data.master_formes_list)
    #if we loaded Model before Personal, need to load Model now
    if(poke_edit_data.run_model_later):
        poke_edit_data = update_model_list(poke_edit_data)
    #if CSV is loaded, load the CSV and do the checks now. In order to only do this once, will run in whichever of personal-loading and model-loading is done second, if run_model_later is false load here. This will also make it run if you reload the personal for whatever reason.
        poke_edit_data = load_names_from_CSV(poke_edit_data)
        
    #copy this into the current list to initialize properly (particularly when loading from cfg)
    poke_edit_data.current_base_species_list = poke_edit_data.base_species_list.copy()
    poke_edit_data.current_personal_list = poke_edit_data.master_formes_list.copy()
    poke_edit_data.current_levelup_list = poke_edit_data.master_formes_list.copy()
    poke_edit_data.current_evolution_list = poke_edit_data.master_formes_list.copy()
    
    return(poke_edit_data)

#loads list of filenames in extracted GARC if it exists, otherwise return empty array
def load_GARC(poke_edit_data, garc_path, target, gameassert):

    if(os.path.exists(garc_path)):
        temp = []
        ext = ''
        #for each file there, pull the extension off, append the filename itself to the temp array.
        for filename in os.listdir(garc_path):
            filename_stripped, ext = os.path.splitext(filename)
            temp.append(filename_stripped)
        #this does assume that everything in the folder has the same extension, but that should be the case...
        poke_edit_data.extracted_extension = ext
    
        if(len(temp) > 0):
            poke_edit_data.game = gameassert
            match poke_edit_data.game:
                case "XY":
                    poke_edit_data.max_species_index = 721
                case "ORAS":
                    poke_edit_data.max_species_index = 721
                case "SM":
                    poke_edit_data.max_species_index = 802
                case "USUM":
                    poke_edit_data.max_species_index = 807
            match target:
                case "Model":
                    poke_edit_data.model_path = garc_path
                    poke_edit_data.model = temp
                    poke_edit_data.model_filename_length = len(temp[0])
                    poke_edit_data = update_model_list(poke_edit_data)
                    conditional_update_modelless_formes_list(poke_edit_data)
                case "Personal":
                    poke_edit_data.personal_path = garc_path
                    poke_edit_data.personal = temp
                    poke_edit_data.personal_filename_length = len(temp[0])
                    poke_edit_data = update_species_list(poke_edit_data)
                case "Levelup":
                    poke_edit_data.levelup_path = garc_path
                    poke_edit_data.levelup = temp
                    poke_edit_data.levelup_filename_length = len(temp[0])
                case "Evolution":
                    poke_edit_data.evolution_path= garc_path
                    poke_edit_data.evolution = temp
                    poke_edit_data.evolution_filename_length = len(temp[0])
    else:
        print("Garc folder not found, unreadable, or empty")
    return(poke_edit_data)
    

def choose_GARC(poke_edit_data, target, gameassert):

    targetpath = ''
    #Evolution table has a fixed length per personal file, 0x30 in gen VI, 0x40 in gen VII
    #Similarly, the Personal file itself is 0x50 in gen VI, 0x54 in gen VII (additional bytes for "is regional forme" and Species-specific Z move)
    match gameassert:
        case "XY":
            poke_edit_data.evolution_table_length = 0x30
            poke_edit_data.personal_table_length = 0x50
            match target:
                case"Model":
                    targetpath = '007'
                case"Personal":
                    targetpath = '218'
                case"Levelup":
                    targetpath = '214'
                case"Evolution":
                    targetpath = '215'
        case "ORAS":
            poke_edit_data.evolution_table_length = 0x30
            poke_edit_data.personal_table_length = 0x50
            match target:
                case "Model":
                    targetpath = '008'
                case "Personal":
                    targetpath = '195'
                case"Levelup":
                    targetpath = '191'
                case"Evolution":
                    targetpath = '192'
        case "SM":
            poke_edit_data.evolution_table_length = 0x40
            poke_edit_data.personal_table_length = 0x54
            match target:
                case"Model":
                    targetpath = '093'
                case"Personal":
                    targetpath = '017'
                case"Levelup":
                    targetpath = '013'
                case"Evolution":
                    targetpath = '014'
        case "USUM":
            poke_edit_data.evolution_table_length = 0x40
            poke_edit_data.personal_table_length = 0x54
            match target:
                case"Model":
                    targetpath = '094'
                case"Personal":
                    targetpath = '017'
                case"Levelup":
                    targetpath = '013'
                case"Evolution":
                    targetpath = '014'
        case "Select Game":
               print("Error: Game not set")
               return

    folder_path = askdirectory(title='Select extracted ' + target + ' Garc Folder, a' + targetpath)
    
    poke_edit_data = load_GARC(poke_edit_data, folder_path, target, gameassert)
    return(poke_edit_data)


#called if the game files have more (inserted) formes than the CSV file.
def rebuild_csv(poke_edit_data):

    #we will rebuild the csv file in this. initialize with the first row, the empty Personal file
    temp_csv_file = [['Egg/Blank', '',0,0,'NA']]
        
    #Now build an array where the jth entry is the number of models for the (j-1)th Pokemon species (e.g. 0 is Bulby). Last entry is the 1 model for egg.
    species_model_count = []
    
    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
            
            for x in range(poke_edit_data.max_species_index + 1):
                #the third byte is how many models that species has.
                species_model_count.append(model_hex_map[4*x + 2])
    
   
    #reference the right master list
    temp_master_list_csv = []
    match poke_edit_data.game:
        case 'XY':
            temp_master_list_csv = xy_master_list_csv.copy()
        case 'ORAS':
            temp_master_list_csv = oras_master_list_csv.copy()
        case 'SM':
            temp_master_list_csv = oras_master_list_csv.copy()
        case 'USUM':
            temp_master_list_csv = usum_master_list_csv.copy()
    

    #row 0 has the empty personal file, skip to next before first iteration
    row_index = 0    
    for current_base_species in range(poke_edit_data.max_species_index + 1):
        #skip the empty personal line
        if(current_base_species != 0):
            
            #grab the rows from the loaded csv that match the currently loaded base species
            species_indices_from_csv = find_rows_with_column_matching(poke_edit_data.master_list_csv, 2, current_base_species)
            total_formes_csv = len(species_indices_from_csv)
            first_forme_index_csv = poke_edit_data.master_list_csv[species_indices_from_csv[-1]][3]
            
            total_formes_game = 0
            forme_index_game = 0
            
            #total number of formes of any kind in the default master list
            total_formes_master = len(find_rows_with_column_matching(temp_master_list_csv, 2, current_base_species))
            #total number of formes with models in the default master list
            total_model_formes_master = total_formes_master - sum([x in find_rows_with_column_matching(temp_master_list_csv, 2, current_base_species) for x in poke_edit_data.modelless_formes])

            
            with open(file_namer(poke_edit_data.personal_path, current_base_species, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
                    total_formes_game = personal_hex_map[0x20]
                    forme_index_game = personal_hex_map[0x1C] + personal_hex_map[0x1D]*256

            #if the total number of formes in the CSV is less than or equal to the max of the forme count and the model count, the old stuff is in there first, stick that in
            if(total_formes_csv <= max(total_formes_game, species_model_count[current_base_species - 1])):
                for index in species_indices_from_csv:
                    row_index += 1
                    temp_csv_file.append(poke_edit_data.master_list_csv[index])
                    temp_csv_file[index][4] = row_index
                    #if this is an alt forme, update the personal index from the game file, then move to the next forme
                    if(temp_csv_file[index][2] != temp_csv_file[index][3]):
                        temp_csv_file[index][3] = forme_index_game
                        forme_index_game += 1
            else:
                print('Formes for species ' + str(current_base_species) + ' have been removed. Please manually edit the CSV.')
                return
            
            #now, if we have any extra stuff from the game file, let's load that
            if(total_formes_csv < max(total_formes_game, species_model_count[current_base_species - 1])):
            
                #in this case, the user has added non-personal-file bearing alt formes, so basically gender-alternate models.
                if(total_model_formes_master < species_model_count[current_base_species - 1] and species_model_count[current_base_species - 1] - total_model_formes_master > total_formes_game - total_formes_csv):
                    print('Detected' + str(species_model_count[current_base_species - 1] - total_formes_game) + ' models added without personals attached. Please manually edit the CSV.')
                else:
                    for x in range(max(total_formes_game, species_model_count[current_base_species - 1]) - total_formes_csv):
                        #for now assume that any added formes have a model attached
                        if(not(forme_index_game in poke_edit_data.modelless_formes)):
                            row_index += 1
                        temp_csv_file.append([poke_edit_data.master_list_csv[first_forme_index_csv][0], x + total_formes_csv + 1, current_base_species, forme_index_game, row_index])
                        forme_index_game += 1
                        #['Venusaur', 'Mega',3,760,4]
    #write egg line
    temp_csv_file.append(['Egg', '','NA','',row_index + 1])
    poke_edit_data.master_list_csv = temp_csv_file.copy()
    return(poke_edit_data)
             

#loads the data from the filepath in the class data structure to the correct variables
def load_names_from_CSV(poke_edit_data, just_wrote = False):
    
    
    temp_base_species_list =  []
    temp_master_formes_list = []
    temp_model_source_list = []


    try:
        with open(poke_edit_data.csv_pokemon_list_path, newline = '', encoding='utf-8-sig') as csvfile:
            reader_head = csv.reader(csvfile, dialect='excel', delimiter=',')
            
            temp_forme_name = ''
            
            #load csv into an array, skip first line because it's just the header
            loaded_csv_file = []
            iter_temp = 0
            for row in reader_head:
                if(iter_temp == 0):
                    iter_temp += 1
                else:
                    loaded_csv_file.append(row)
            #We need to find the max personal file index since that's not in order with the structure of the models
            personal_max_temp = max_of_column(loaded_csv_file, 1)

            #and now give the formes_list table the right size:
            #has max index + 1 entries, because there is both a 0th and max indexth entry                
            for x in range(personal_max_temp+1):
                temp_master_formes_list.append('')

            for data_rows in loaded_csv_file:
                #build the underlying species, forme, and model file lists
                #if personal index is the same as the nat dex number, is the base forme, so append the species name
                if(data_rows[0].isdigit() and data_rows[1].isdigit() and data_rows[0] == data_rows[1]):
                    temp_base_species_list.append(data_rows[3])
                #if the forme-name slot is non-empty, will be used at least once following this, if it empty need to not have dangling seperator
                if(data_rows[4] != ""):
                    temp_forme_name = data_rows[3] + " - " + data_rows[4]
                else:
                    temp_forme_name = data_rows[3]

                #if the personal index is NOT (empty or NA), then write the species name + forme name to the formes list
                if(not(data_rows[1] in {"", "NA"})):
                    temp_master_formes_list[int(data_rows[1])]= temp_forme_name
                    
                #if the model index is NOT empty or NA, then write the species name + forme name to the formes list. This should only happen for the very first entry, so report an error if that happens
                if(not(data_rows[2] in {"", "NA"})):
                    temp_model_source_list.append(temp_forme_name)
                elif(data_rows[2].isdigit() and int(data_rows[2]) > 0):
                    print('Entry without unique model file detected at Species Index-Personal Index-Name:' + data_rows[0] + '-' + data_rows[1] + '-' + data_rows[3] + '-' + data_rows[4])
                #print(data_rows)
                
            #series of checks to see if it is the case that the loaded CSV arrays are shorter than the default-created ones (in which case assume we just created/refreshed the CSV, or loaded the wrong thing), or is longer (in which case the CSV has more entries than the game files and something is terribly wrong)
            #only do this if we loaded, not if we just insert a Pokemon        

            if(not(just_wrote)):
                    species_check = len(temp_base_species_list) - len(poke_edit_data.base_species_list)
                    forme_check = len(temp_master_formes_list) - len(poke_edit_data.master_formes_list)
                    model_check = len(temp_model_source_list) - len(poke_edit_data.model_source_list)

                    if(species_check < 0):
                        print('The loaded CSV has fewer Pokemon base species than your game files. Something is very probably wrong unless you have successfully added new species to the game (in which case please submit a bug report so I can update). The Pokemon base species entries read from the CSV have NOT been loaded.')
                        return(poke_edit_data)
                    elif(species_check > 0):
                        print('The loaded CSV has more Pokemon base species than your game files. Something is very probably wrong. Please recheck your game files, the csv itself, and your settings. The Pokemon base species entries read from the CSV have NOT been loaded.')
                        return(poke_edit_data)
                    elif(species_check == 0):
                        print('Loading Pokemon Species List from CSV')
                        poke_edit_data.base_species_list = temp_base_species_list.copy()
            
                    if(forme_check < 0):
                        print('The loaded CSV has fewer total Forme entries than your game files. Unless you have not previously selected or initialized a csv for your game, or for whatever reason refreshed it to default, something might be wrong. Please double-check your file selections and settings. Will rebuild CSV file in memory from game files, if this is wrong, please exit without saving')
                        return(rebuild_csv(poke_edit_data))

                    elif(forme_check > 0):
                        print('The loaded CSV has more total Forme entries than your game files. Something is wrong. Please double-check your file selections and settings. The Forme entries read from the CSV have NOT been loaded.')
                        return(poke_edit_data)
                    if(forme_check == 0):
                        print('Loading Formes List from CSV')
                        poke_edit_data.master_formes_list = temp_master_formes_list.copy()
            
                    if(model_check < 0):
                        print('The loaded CSV has fewer total Model entries than your game files. Unless you have not previously selected or initialized a csv for your game, or for whatever reason refreshed it to default, something might be wrong. Please double-check your file selections and settings. Will rebuild CSV file in memory from game files, if this is wrong, please exit without saving')
                        return(rebuild_csv(poke_edit_data))
                    elif(model_check > 0):
                        print('The loaded CSV has more total Model entries than your game files. Something is wrong. Please double-check your file selections and settings. The Model entries read from the CSV have NOT been loaded.')
                    if(model_check == 0):
                        print('Loading Model List from CSV')
                        poke_edit_data.model_source_list = temp_model_source_list.copy()
            else:
                poke_edit_data.base_species_list = temp_base_species_list.copy()
                poke_edit_data.master_formes_list = temp_master_formes_list.copy()
                poke_edit_data.model_source_list = temp_model_source_list.copy()
    except:
        print('CSV file ' + poke_edit_data.csv_pokemon_list_path + ' not found (if no text is present between "file" and "found", filename is empty).')
        poke_edit_data.csv_pokemon_list_path = askopenfilename(title='Select Pokemon Names and Files CSV')
        poke_edit_data= load_names_from_CSV(poke_edit_data, just_wrote)
    return(poke_edit_data)


#just asks for the path and calls the write-csv-to-the-right-part-of-the-class-data-structure program
def user_prompt_load_CSV(poke_edit_data, target):

    poke_edit_data.csv_pokemon_list_path = askopenfilename(title='Select ' + target + ' CSV')
    

    poke_edit_data = load_names_from_CSV(poke_edit_data)
    

    return(poke_edit_data)

def create_refresh_CSV(poke_edit_data, target, gameassert):
    

    #update game in data structure (in case this is the first thing selected)
    if(gameassert in {'XY', 'ORAS', 'SM', 'USUM'}):
        poke_edit_data.game = gameassert


    if(not(poke_edit_data.game in {'XY', 'ORAS', 'SM', 'USUM'})):
        print('Please select supported game')
        return
    try:
        #poke_edit_data.csv_pokemon_list_path = asksaveasfilename(title='Select CSV file to RESET or CREATE your list of ' + target)
    
        match poke_edit_data.game:
            case 'XY':
                poke_edit_data.master_list_csv = xy_master_list_csv.copy()
            case 'ORAS':
                poke_edit_data.master_list_csv = oras_master_list_csv.copy()
            case 'SM':
                poke_edit_data.master_list_csv = oras_master_list_csv.copy()
            case 'USUM':
                poke_edit_data.master_list_csv = usum_master_list_csv.copy()
        if():
            poke_edit_data = rebuild_csv(poke_edit_data)
    except:
        print('No file selected')
    return(poke_edit_data)

def write_CSV(poke_edit_data, csv_path = ''):

    #use saved config path if nothing set
    if(csv_path == ''):
        csv_path = poke_edit_data.csv_pokemon_list_path
    else:
        poke_edit_data.csv_pokemon_list_path = csv_path
    
    #try to open filepath
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer_head = csv.writer(csvfile, dialect='excel', delimiter=',')
            #write the header line
            writer_head.writerow (['Base Index', 'Personal Index', 'Model Index', 'Species', 'Forme', 'Model', 'Texture', 'Shiny_Texture', 'Greyscale_Texture', 'Battle_Animations', 'Refresh_Animations', 'Movement_Animations', 'Lip_Animations', 'Empty', 'Portrait', 'Shiny_Portrait', 'Icon'])
            
            model_file_start = 0
            model_file_count = 0

            if(poke_edit_data.game in {'SM', 'USUM'}):
                model_file_start = 1
                model_file_count = 9                
            else:
                model_file_count = 8
                
                if(poke_edit_data.game == 'XY'):
                    model_file_start = 4
                else:
                    model_file_start = 3
                
            #print(len(poke_edit_data.master_list_csv))
            #iterate over the names in the model source list
            #write species index to column A, personal file index to B, model index to C, species name to D, forme to E, then model/texture/animaiton filenames in 6 starts at 4, 3, 1 for XY, ORAS, SMUSUM
            for enum, pokemon_instance in enumerate(poke_edit_data.master_list_csv):
                if(enum == 0):
                    writer_head.writerow ([pokemon_instance[2], pokemon_instance[3], pokemon_instance[4], pokemon_instance[0], pokemon_instance[1]])
                else:
                    writer_head.writerow ([pokemon_instance[2], pokemon_instance[3], pokemon_instance[4], pokemon_instance[0], pokemon_instance[1]] + [(enum - 1)*model_file_count + x + model_file_start for x in range(model_file_count)])
    #don't do anything and proceed as usual if none exists, print error message
    except:
        print('Selected CSV file is open in another program. Please close it and try again')
    return(poke_edit_data)

def user_prompt_write_CSV(poke_edit_data, target):

    write_CSV(poke_edit_data, asksaveasfilename(title='Select CSV file that has your list of ' + target))
    
    return(poke_edit_data)

def load_game_cfg(poke_edit_data):
    
    game_cfg_path = askopenfilename(title='Select cfg file', defaultextension='.cfg',filetypes= [('config','.cfg')])
    
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
    9 = extension
    10 = max species index
    11 = Names Table CSV
    '''
    
    cfg_desc = ["Game", "Personal path", "Levelup path", "Evolution path", "Pokemon Model/Texture path",'','','','',"Extension","Max Species Index", "Names and Model File List CSV Path"]
 
    try:
        with open(game_cfg_path, "r") as cfg:
            cfg_array = [line.rstrip() for line in cfg]
        poke_edit_data.game = cfg_array[0]
        poke_edit_data.personal_path = cfg_array[1]
        poke_edit_data.levelup_path = cfg_array[2]
        poke_edit_data.evolution_path = cfg_array[3]
        poke_edit_data.model_path = cfg_array[4]
        poke_edit_data.modelless_formes = cfg_array[5]
        #evolution = cfg_array[6]
        #evolution = cfg_array[7]
        #evolution = cfg_array[8]
        poke_edit_data.extracted_extension = cfg_array[9]
        poke_edit_data.max_species_index = cfg_array[10]
        poke_edit_data.csv_pokemon_list_path = cfg_array[11]
    
        if(poke_edit_data.game in {'XY', 'ORAS'}):
            poke_edit_data.evolution_table_length = 0x30
            poke_edit_data.personal_table_length = 0x50
        elif(poke_edit_data.game in {'SM', 'USUM'}):
            poke_edit_data.evolution_table_length = 0x40
            poke_edit_data.personal_table_length = 0x54
        else:
            print('Warning: Game not correctly set in cfg, ensure a game is selected, then reload any GARC')
        

        print('Data loaded as follows:')
        for x in range(len(cfg_desc)):
            if(cfg_desc[x] != ''):
                print(cfg_desc[x] + ': ' + str(cfg_array[x]))
        print('\n')

        poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.personal_path, "Personal", poke_edit_data.game)
        poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.levelup_path, "Levelup", poke_edit_data.game)
        poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.evolution_path, "Evolution", poke_edit_data.game)
        poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.model_path, "Model", poke_edit_data.game)
        
        print('\n')
        print("Number of Species:", len(poke_edit_data.base_species_list) - 1, "(not including the blank entry)")
        print("Number of Personal Entries:", len(poke_edit_data.master_formes_list) - 1, "(not including the blank entry)")
        print("Number of Model Entries:", len(poke_edit_data.model_source_list))
    except:
        print('Selection missing or invalid')


    return(poke_edit_data)
    
def save_game_cfg(poke_edit_data, game_set):
 
    game_cfg_path = asksaveasfilename(title='Select location to save cfg file', defaultextension='.cfg',filetypes= [('config','.cfg')])
    
    poke_edit_data.game = game_set
    
    cfg_array = []
    
    try:
        with open(game_cfg_path, "w") as cfg:
            cfg.write(poke_edit_data.game + '\n')
            cfg.write(poke_edit_data.personal_path + '\n')
            cfg.write(poke_edit_data.levelup_path + '\n')
            cfg.write(poke_edit_data.evolution_path + '\n')
            cfg.write(poke_edit_data.model_path + '\n')
            cfg.write(poke_edit_data.modelless_formes)
            cfg.write('\n') #evolution = cfg_array[6]
            cfg.write('\n')#evolution = cfg_array[7]
            cfg.write('\n')#evolution = cfg_array[8]
            cfg.write(poke_edit_data.extracted_extension + '\n')
            cfg.write(str(poke_edit_data.max_species_index) + '\n')
            cfg.write(poke_edit_data.csv_pokemon_list_path)
        print('Config file saved to ' + game_cfg_path)
        write_CSV(poke_edit_data)
        print('Names and Model File List CSV saved to ' + poke_edit_data.csv_pokemon_list_path)
    except:
        print("No file selected")