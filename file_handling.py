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
from tokenize import maybe
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
    model_temp_list = []
    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as model_hex_map:
            
            #for base formes plus egg at poke_edit_data.max_species_index
            for index in range(poke_edit_data.max_species_index):
                #number of model sets this species has
                number_of_models = int(model_hex_map[(index)*4 + 2])
              
                #grab the name
                temp_name = poke_edit_data.base_species_list[index + 1]
                
                #name each model as <Pokemon species> <number>, the base forme is named <Pokemon> 0 so that (in at least most cases) the model-number lines up with the forme-number (where there are multiple)
                for distinct_models in range(0, number_of_models):
                    model_temp_list.append(temp_name + ' ' + str(distinct_models))
    
    #append the Egg
    model_temp_list.append('Egg')

    #copy this into the current list to initialize properly (particularly when loading from cfg)
    poke_edit_data.model_source_list = model_temp_list.copy()                
    poke_edit_data.current_model_source_list = poke_edit_data.model_source_list.copy()

    return(poke_edit_data)

'''def conditional_update_modelless_formes_list(poke_edit_data):
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
    return(poke_edit_data)'''

#adds missing models (e.g. Dusk Rockruff or from incomplete manual forme insertion)
def add_missing_models(poke_edit_data):
    #locate base species with missing models
    personal_forme_count = []
    species_has_unique_personal_genders_array = []
    temp_master = []
    #grab the current game's default list:


    for species_index in range(1, poke_edit_data.max_species_index + 1):
        
        #build array with the jth element being the j+1th species' personal forme count
        with open(file_namer(poke_edit_data.personal_path, species_index, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
                    #if the forme pointer bytes are 0x0000, then there is only the single Personal file    
                    if(personal_hex_map[0x1C] != 0x0 or personal_hex_map[0x1D] != 0x0):
                        personal_forme_count.append(personal_hex_map[0x20])
                        #check to see what the gender byte in the next personal file is
                        with open(file_namer(poke_edit_data.personal_path, int(str(personal_hex_map[0x1C] + personal_hex_map[0x1D]*256)), poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f_1:
                            with mmap.mmap(f_1.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map_1:
                                
                                #if they have the same gender value, then not unique gendered formes (at most cosmetic). Also, if one of them is not all-male or all female, then something else, like Pikachu (base is 50/50, first personal forme is 100% male, but has alt female model for regular)
                                if(personal_hex_map_1[0x12] == personal_hex_map[0x12] or not (personal_hex_map[0x12] in {0x0, 0xFE} and personal_hex_map_1[0x12] in {0x0, 0xFE})):
                                    species_has_unique_personal_genders_array.append(False)
                                else:
                                    species_has_unique_personal_genders_array.append(True)
                    else:
                        personal_forme_count.append(0x1)
                        species_has_unique_personal_genders_array.append(False)
        #print(str(species_index), species_has_unique_personal_genders_array[species_index - 1])
                        
    #print(personal_forme_count)
    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
            model_hex_map.flush
            
            #look for species with fewer formes than personal files. This 
            for species_index, current_personal_forme_count in reversed(list(enumerate(personal_forme_count))):
                
                #if this species has a gender-difference forme, subtract one from the model count (this detects if, for example, we added Mega Venusar Y but no model, because then we have 3 personal files (base, original Mega, and Y) and 3 model files (base male, base female, original mega), but only if the total formes is more than in the stock game
                #It might be possible to add more than 1 gender difference forme (e.g. have Mega Venusaur have alt female mega forme), if we verify will figure out how to find that out from this table
                total_personal_models = model_hex_map[4*species_index + 2]
                    
                
                '''
                    cases
                    1) More Models than Personal. Don't care
                    2) More Personal than Model. Only should happen from manual insert or something like Rockruff. Either way need to insert Personal - Model (from GARC) models and update the master list. This will always run after the thing that rebuilds the CSV to have the right number of rows
                    3) Need to account for gender-difference models. Check the relevant bit to see if there is a female forme. In that case the base form has 1 personal for 2 models OR 2 for 2 (Meowstic). this gives amount_to_add < 0, which is fine if nothing else.
                        We can check for this by looking at the gender of the first two personal files, if it's All Male/All Female, then meowstic case (proceed as normal, but DON'T update the bitflag at the end to have alt formes be true). Otherwise, the gender difference is cosmetic, we should update the flag, and we have 1 extra model
                '''
                
                #like Meowstic, alt-gender has unique personal. No extra models.
                if(species_has_unique_personal_genders_array[species_index]):
                    amount_to_add = current_personal_forme_count - total_personal_models
                #otherwise, if the "gendered forme model" bit is 1, then we have an extra model
                elif(model_hex_map[4*species_index + 3] >> 1 & 1):
                    amount_to_add = current_personal_forme_count - (total_personal_models - 1)
                #otherwise no gendered formes at all
                else:
                    amount_to_add = current_personal_forme_count - total_personal_models
                    
                

                
                #print(real_personal_count, real_model_count, stock_model_exceeds_personal, amount_to_add, current_personal_forme_count, total_personal_models)
                if(amount_to_add > 0):
                    #print(amount_to_add, poke_edit_data.base_species_list[species_index +1], current_personal_forme_count, total_personal_models)
                    
                    #updated_species.append(species_index+1)
                    new_forme_count = amount_to_add
                    #number of models on pokemon getting new forms + total number of models of all prior Pokemon
                    total_previous_models = model_hex_map[4*(species_index) + 2] + model_hex_map[4*(species_index) + 1]*256 + model_hex_map[4*(species_index) + 0]
                
                    model_source_index = model_hex_map[4*(species_index) + 1]*256 + model_hex_map[4*(species_index) + 0]
            
                    #this is the model we're copying
                    model_start_file = 0
                    #this is where we have to insert those copies after
                    model_dest_file = 0
                    #this is how many of those files there are per new forme
                    model_file_count = 0
            
                    if(poke_edit_data.game == 'XY'):
                        model_start_file = 8*(model_source_index)+3+1
                        model_dest_file = 8*total_previous_models+3
                        model_file_count = 8
                    elif(poke_edit_data.game == "ORAS"):
                        model_start_file = 8*(model_source_index)+2+1
                        model_dest_file = 8*total_previous_models+2
                        model_file_count = 8
                    #assume SM or USUM
                    else:
                        model_start_file = 9*(model_source_index)+1
                        model_dest_file = 9*total_previous_models
                        model_file_count = 9
            
                    print("Shifting model files for species after index", str(species_index + 1), ' ', poke_edit_data.base_species_list[species_index +1])

                    #shift the later model files forward
                    for file_number, file in reversed(list(enumerate(poke_edit_data.model))):
                        #if we've hit the *last* file of the Pokemon we're adding forme(s) too, stop this
                        if(file_number == model_dest_file):
                            break
                        #move file (# files per model)*(# new formes added) numbers forward
                        os.rename(file_namer(poke_edit_data.model_path, file_number, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.model_path, file_number + model_file_count*new_forme_count, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension))
                        
                        #print(file_namer(poke_edit_data.model_path, file_number, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), ' ', file_namer(poke_edit_data.model_path, file_number + model_file_count*new_forme_count, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension))
                       
                        #update the model file list. Otherwise if we do more than 1 forme it will miss the last files and crash
                        poke_edit_data.model.append(file_number + model_file_count*new_forme_count)
                    #print(model_start_file, model_dest_file)
                    #copies each of the source model/texture/animation files from A.bin to the filename cleared up by the previous for loop
                    temp_test = []    
                    for x in range(0, new_forme_count):
                        for y in range(0, model_file_count):
                            shutil.copy(file_namer(poke_edit_data.model_path, model_start_file + y, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.model_path, model_dest_file + x*model_file_count + y + 1, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension))

                    #reset the model filename list, since we added stuff to the end
                    poke_edit_data.model = []
                    for filename in os.listdir(poke_edit_data.model_path):
                        filename_stripped, ext = os.path.splitext(filename)
                        poke_edit_data.model.append(filename_stripped)
                    #print(len(poke_edit_data.model))
                    #print("New model files initialized for species index", str(species_index + 1))
                    #print("Updating model header for species index", str(species_index + 1))
            
                    #Now need to update model header
            
                    #set the non-gendered form bit to true if not so set, unless the Pokemon has unique personal for its alt gender
                    if(model_hex_map[4*(species_index) + 3] < 0x05 and not(species_has_unique_personal_genders_array[species_index])):
                        model_hex_map[4*(species_index) + 3] += 0x04
            
            
                    #update the number of models for the species
                    model_hex_map[4*(species_index) + 2] += new_forme_count
            
            
                    #update the "model count so far" value
                    #poke_edit_data.max_species_index + 1 because egg is last at position poke_edit_data.max_species_index (0 is Bulba, poke_edit_data.max_species_index - 1 is the last species in nat dex)
                    #because for loop, would need to subtract 1 (0,poke_edit_data.max_species_index - 1) normally, but +1 for egg
            
                    #grab model count so far
                    model_count = 0
            
                    #update number of models
                    #start from the beginning just in case something erred at another point
                    for index in range(0, poke_edit_data.max_species_index):
                        model_hex_map[4*index + 0], model_hex_map[4*index + 1] = little_endian_chunks(model_count)
                        model_count += model_hex_map[4*index + 2]
             
                    #after the first part of the file, the next part (starting immediately after the last four bytes of the above described section of the model table header that mark the Egg model) has 2 bytes per *model*, the values of which have some pattern but make about no sense at all. Perhaps legacy data? In any event the game needs there be those 2 bytes per model, so the following section shifts this table forward by the appropriate amount to insert 00 00 for each new model added (not adding them to the end just in case something somehow needs those in the expected spot).
                    #This section starts at poke_edit_data.max_species_index*4
            
            
                    #number of bytes to move
                    #this is the length (in bytes) of the entire table, minus 4*(poke_edit_data.max_species_index+1) (to include the Egg), minus the number of models before the spot we're inserting into:
                    length_of_bytes_to_move = len(model_hex_map) - (poke_edit_data.max_species_index+1)*4 - total_previous_models*2
            
                    #add 2*<number formes added> bytes to the model table
                    model_hex_map.resize(len(model_hex_map) + 2*new_forme_count)
            
                    #move(dest, src, cont) - moves the cont bytes starting at src to dest (note destination is just source plus twice as many bytes as models inserted)
                    model_hex_map.move(poke_edit_data.max_species_index*4 + total_previous_models*2 + 2*new_forme_count, poke_edit_data.max_species_index*4 + total_previous_models*2, length_of_bytes_to_move)
            
                    #set the bytes for the new models to 0x00
                    for offset in range(0, 2*new_forme_count):
                        model_hex_map[poke_edit_data.max_species_index*4 + total_previous_models*2 + offset] = 0x00
                    print('Model header updated for species index', str(species_index + 1))

    #print('Missing formes initialized!' + '\n')

    #Now update the csv table. All we did was add model files for what's there, so all we have to do is start at the 2nd row and add 1 the model index every time we go forwards
    for row_number, row in enumerate(poke_edit_data.master_list_csv):
        if(row_number != 0):
            row[4] = row_number - 1
    
    #no formes should be without model now:
    poke_edit_data.modelless_exists = False
   # print('Internal tables updated with changes' + '\n' + '\n')
    

    return(poke_edit_data)

def update_species_list(poke_edit_data, overwrite_from_default = True):
    
    if(overwrite_from_default):
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
    else:
        poke_edit_data.base_species_list = entire_of_column(poke_edit_data.master_list_csv, 0, False)
        
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
        
    #copy this into the current list to initialize properly (particularly when loading from cfg)
    poke_edit_data.current_base_species_list = poke_edit_data.base_species_list.copy()
    poke_edit_data.current_personal_list = poke_edit_data.master_formes_list.copy()
    poke_edit_data.current_levelup_list = poke_edit_data.master_formes_list.copy()
    poke_edit_data.current_evolution_list = poke_edit_data.master_formes_list.copy()
    
    return(poke_edit_data)

#loads list of filenames in extracted GARC if it exists, otherwise return empty array
def load_GARC(poke_edit_data, garc_path, target, gameassert, overwrite_from_default = True):

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
                    #conditional_update_modelless_formes_list(poke_edit_data)
                case "Personal":
                    poke_edit_data.personal_path = garc_path
                    poke_edit_data.personal = temp
                    poke_edit_data.personal_filename_length = len(temp[0])
                    poke_edit_data = update_species_list(poke_edit_data, overwrite_from_default)
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
    
    #row 0 has the empty personal file, skip to next before first iteration
    row_index = 0
    model_index = 0
        
    temp_personal_instance_garc = 0
    temp_personal_pointer_garc = 0
    
    for current_base_species in range(1, poke_edit_data.max_species_index + 1):
        #skip the empty personal line
        #grab the rows from the loaded csv that match the currently loaded base species
        species_indices_from_csv = find_rows_with_column_matching(poke_edit_data.master_list_csv, 2, current_base_species)

        #grab the number of personal and model instances for the current Pokemon from the loaded csv
        temp_personal_instance_csv = 0
        temp_model_instance_csv = 0
        
        for row_index in species_indices_from_csv:
            if(poke_edit_data.master_list_csv[row_index][3] != ''):
                temp_personal_instance_csv += 1
            if(poke_edit_data.master_list_csv[row_index][4] != ''):
                temp_model_instance_csv += 1

        #grab the number of personal files for this Pokemon from the GARC
        with open(file_namer(poke_edit_data.personal_path, current_base_species, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
                temp_personal_pointer_garc = personal_hex_map[0x1C] + personal_hex_map[0x1D]*256
                
                #if the pointer is 0 but the forme count is >1, then only 1 personal file
                if(temp_personal_pointer_garc in {'0', '', 0, 0x0}):
                    temp_personal_instance_garc = 0x1
                else:
                    temp_personal_instance_garc = personal_hex_map[0x20]
                
        
        missing_personal_count = temp_personal_instance_garc - temp_personal_instance_csv
        missing_model_count = species_model_count[current_base_species - 1] - temp_model_instance_csv
        
        '''if(missing_personal_count != 0 or missing_personal_count != 0):
            print(poke_edit_data.master_list_csv[species_indices_from_csv[0]])
            print(missing_personal_count, temp_personal_instance_garc, temp_personal_instance_csv)
            print(missing_model_count, species_model_count[current_base_species - 1] , temp_model_instance_csv)'''


        #just append the rows in the CSV
        for row in species_indices_from_csv:
            temp_csv_file.append(poke_edit_data.master_list_csv[row])
            row_index += 1
            #check for personal formes sharing model that haven't been fixed and don't write a model index number
            if(not(temp_personal_instance_csv > temp_model_instance_csv)):
                #update model index number
                temp_csv_file[row][4] = row
                model_index += 1
                
        #both the same, no changes here
        if(missing_personal_count == 0 and missing_model_count == 0):
            pass
        #CSV has additions and deletions from game in both directions in either Model or Personal
        elif(missing_personal_count < 0 or missing_model_count < 0):
            print('Problem detected at row', row_index)
            print('CSV has additons AND deletions compared to GARC. Please refresh the CSV and try again.')
            return
        #at least one of model and Personal have more entries. 
        else:
            rows_to_add = max(missing_personal_count, missing_model_count)
            #get base species name
            temp_name = poke_edit_data.master_list_csv[species_indices_from_csv[0]][0]
            for x in range(rows_to_add):
                
                if(missing_personal_count > x):
                    temp_forme_personal_location = temp_personal_pointer_garc + (temp_personal_instance_csv - 1) + x
                #keep things in line if there's a model file without a personal
                else:
                    temp_forme_personal_location = ''
                    temp_personal_pointer_garc -= 1
                if(missing_model_count > x):
                    temp_model_index = model_index
                    model_index += 1
                else:
                    temp_model_index = ''
                temp_csv_file.append([temp_name, temp_personal_instance_csv + x, current_base_species, temp_forme_personal_location, temp_model_index])
                
                row_index += 1

    #drop in the egg model last
    temp_csv_file.append(['Egg', '','NA','',model_index])
    
    #update the model indices
    for row_number, row in enumerate(temp_csv_file):
        if(row_number == 0):
            row[4] = ''
        else:
            row[4] = row_number - 1

    poke_edit_data.master_list_csv = temp_csv_file.copy()
    
    write_CSV(poke_edit_data)

    return(poke_edit_data)
             

#loads the data from the filepath in the class data structure to the correct variables
def load_names_from_CSV(poke_edit_data, just_wrote = False):
    
    
    temp_base_species_list =  []
    temp_master_formes_list = []
    temp_model_source_list = []


    try:
        with open(poke_edit_data.csv_pokemon_list_path, newline = '', encoding='utf-8-sig') as csvfile:
            reader_head = csv.reader(csvfile, dialect='excel', delimiter=',')
            next(reader_head) # skip the header

            #load csv into an array
            loaded_csv_file = []
            for row in reader_head:
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
    
        #looks for missing models, adds them in
        if(poke_edit_data.modelless_exists):
            poke_edit_data = add_missing_models(poke_edit_data)
            poke_edit_data.modelless_exists = False
        
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
                    print('The loaded CSV might have fewer Forme entries than your game files. Unless you have not previously selected or initialized a csv for your game, or for whatever reason refreshed it to default, something might be wrong. Please double-check your file selections and settings. Will rebuild CSV file in memory from game files, if this is wrong, please exit without saving')
                    poke_edit_data = rebuild_csv(poke_edit_data)
                elif(forme_check > 0):
                    print('The loaded CSV has more total Forme entries than your game files. Something is wrong. Please double-check your file selections and settings. The Forme entries read from the CSV have NOT been loaded.')
                    return(poke_edit_data)
                    
                if(forme_check == 0):
                    print('Loading Formes List from CSV')
                    poke_edit_data.master_formes_list = temp_master_formes_list.copy()
            
                if(model_check < 0):
                    print('The loaded CSV might have fewer total Model entries than your game files. Unless you have not previously selected or initialized a csv for your game, or for whatever reason refreshed it to default, something might be wrong. Please double-check your file selections and settings. Will attempt to update.')
                    poke_edit_data = rebuild_csv(poke_edit_data)
                    poke_edit_data = load_names_from_CSV(poke_edit_data, True)
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
        try:
            poke_edit_data.csv_pokemon_list_path = askopenfilename(title='Select Existing Pokemon Names and Files CSV, or cancel to create a new one')
            poke_edit_data = load_names_from_CSV(poke_edit_data, just_wrote)
        except:
            poke_edit_data.csv_pokemon_list_path = asksaveasfilename(title='Create New Pokemon Names and Files CSV')
            poke_edit_data = load_names_from_CSV(poke_edit_data, just_wrote)
    
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
        user_prompt_write_CSV(poke_edit_data, 'Pokemon Names and Files')
        poke_edit_data = load_names_from_CSV(poke_edit_data)
    except:
        print('No file selected')
    return(poke_edit_data)

def write_CSV(poke_edit_data, csv_path = ''):

    #use saved config path if nothing set
    if(csv_path == ''):
        csv_path = poke_edit_data.csv_pokemon_list_path
    else:
        poke_edit_data.csv_pokemon_list_path = csv_path
    #print(csv_path)
    #try to open filepath
    
    #print('after called write')
    #for pokemon_instance in poke_edit_data.master_list_csv:
    #    print(pokemon_instance)
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
                    #print([pokemon_instance[2], pokemon_instance[3], pokemon_instance[4], pokemon_instance[0], pokemon_instance[1]] + [(enum - 1)*model_file_count + x + model_file_start for x in range(model_file_count)])
                    writer_head.writerow ([pokemon_instance[2], pokemon_instance[3], pokemon_instance[4], pokemon_instance[0], pokemon_instance[1]] + [(enum - 1)*model_file_count + x + model_file_start for x in range(model_file_count)])
    #don't do anything and proceed as usual if none exists, print error message
    except:
        print('Selected CSV file is open in another program. Please close it and try again')
    
    
    #print('after write')
    #for pokemon_instance in poke_edit_data.master_list_csv:
    #    print(pokemon_instance)
    return(poke_edit_data)

def user_prompt_write_CSV(poke_edit_data, target):

    write_CSV(poke_edit_data, asksaveasfilename(title='Select ' + target + ' CSV'))
    
    return(poke_edit_data)

def load_game_cfg(poke_edit_data):
    
    game_cfg_path = askopenfilename(title='Select cfg file', defaultextension='.cfg',filetypes= [('config','.cfg')])

    '''read all the lines
    0 = game
    1 = Personal
    2 = Level
    3 = Evolution
    4 = Model/texture
    5 = list of modelles formes
    6 = all clear bool
    7 = portrait_1
    8 = portrait_2
    9 = extension
    10 = max species index
    11 = Names Table CSV
    '''
    
    cfg_desc = ["Game", "Personal path", "Levelup path", "Evolution path", "Pokemon Model/Texture path",'','Need to update Models','','',"Extension","Max Species Index", "Names and Model File List CSV Path"]
 
    #try:
    with open(game_cfg_path, "r") as cfg:
        cfg_array = [line.rstrip() for line in cfg]
    try:
        poke_edit_data.game = cfg_array[0]
        poke_edit_data.personal_path = cfg_array[1]
        poke_edit_data.levelup_path = cfg_array[2]
        poke_edit_data.evolution_path = cfg_array[3]
        poke_edit_data.model_path = cfg_array[4]
        # = cfg_array[5]
        #check to avoid issues loading old files, defaults to True due to class construction if neither passes
        if(cfg_array[6] == 'True'):
            poke_edit_data.modelless_exists = True
        elif(cfg_array[6] == 'False'):
            poke_edit_data.modelless_exists = False
        
        #evolution = cfg_array[7]
        #evolution = cfg_array[8]
        poke_edit_data.extracted_extension = cfg_array[9]
        poke_edit_data.max_species_index = cfg_array[10]
        poke_edit_data.csv_pokemon_list_path = cfg_array[11]
    except:
        print('Config file missing lines, loaded what was there')
    
    if(poke_edit_data.game in {'XY', 'ORAS'}):
        poke_edit_data.evolution_table_length = 0x30
        poke_edit_data.personal_table_length = 0x50
    elif(poke_edit_data.game in {'SM', 'USUM'}):
        poke_edit_data.evolution_table_length = 0x40
        poke_edit_data.personal_table_length = 0x54
    else:
        print('Warning: Game not correctly set in cfg, ensure a game is selected, then reload any GARC')
        
    try:
        print('Data loaded as follows:')
        for x in range(len(cfg_desc)):
            if(cfg_desc[x] != ''):
                print(cfg_desc[x] + ': ' + str(cfg_array[x]))
    except:
        print('Missing lines from config')
    print('\n')

    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.personal_path, "Personal", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.levelup_path, "Levelup", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.evolution_path, "Evolution", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.model_path, "Model", poke_edit_data.game)
    poke_edit_data = load_names_from_CSV(poke_edit_data)
        
    print('\n')
    print("Number of Species:", len(poke_edit_data.base_species_list) - 1, "(not including the Egg)")
    print("Number of Personal Entries:", len(poke_edit_data.master_formes_list) - 1, "(not including the Egg)")
    print("Number of Model Entries:", len(poke_edit_data.model_source_list))
    '''except:
        print('Selection missing or invalid')'''


    return(poke_edit_data)
    
def save_game_cfg(poke_edit_data, game_set = ''):
 
    game_cfg_path = asksaveasfilename(title='Select location to save cfg file', defaultextension='.cfg',filetypes= [('config','.cfg')])
    
    if(game_set != ''):
        poke_edit_data.game = game_set
    
    if(poke_edit_data.modelless_exists):
        temp_modelless = 'True'
    else:
        temp_modelless = 'False'
    
    try:
        with open(game_cfg_path, "w") as cfg:
            cfg.write(poke_edit_data.game + '\n')
            cfg.write(poke_edit_data.personal_path + '\n')
            cfg.write(poke_edit_data.levelup_path + '\n')
            cfg.write(poke_edit_data.evolution_path + '\n')
            cfg.write(poke_edit_data.model_path + '\n')
            cfg.write('\n')
            cfg.write(temp_modelless + '\n')
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
