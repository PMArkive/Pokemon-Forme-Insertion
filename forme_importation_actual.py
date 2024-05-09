import shutil
import os
import mmap
import sys
import errno
from my_constants import *
from file_handling import *

def add_new_forme_execute(poke_edit_data, base_form_index, start_location, new_forme_count, model_source_index, personal_source_index, levelup_source_index , evolution_source_index, existing_formes_array, def_model, total_alt_formes, enough_room):
    
    total_formes = total_alt_formes + 1
    print("Initializing new data")
    #Part 1, Personal file, update existing Personal blocks with new forme count and pointer
    personal_file_update(poke_edit_data, base_form_index, total_formes, start_location)
    
    for pokemon in existing_formes_array:
        personal_file_update(poke_edit_data, pokemon, total_formes, start_location)
        
    #for Levelup, evo, and Personal, move existing formes if needed. We need to delete existing files if they are there, then copy them to the new location, then overwrite the old spot with zeroes
    #offset starts from 0, which is the first forme that is at index start_location
    if(not(enough_room)):
        for offset, pokemon in enumerate(existing_formes_array):
    
            #delete target spots if they exist (only happens if filling a spot cleared by moving something else)
            silentremove(file_namer(poke_edit_data.personal_path, start_location + offset, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension))
            silentremove(file_namer(poke_edit_data.evolution_path, start_location + offset, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension))
            silentremove(file_namer(poke_edit_data.levelup_path, start_location + offset, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension))

            #copy personal file to new location
            shutil.copy(file_namer(poke_edit_data.personal_path, pokemon, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.personal_path, start_location + offset, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension))
        
            #zero out old personal block
            with open(file_namer(poke_edit_data.personal_path, pokemon, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
                    personal_hex_map.flush
                    personal_hex_map.resize(poke_edit_data.personal_table_length)
                    for x in range(0, poke_edit_data.personal_table_length):
                        personal_hex_map[x] = 0x00
                    personal_hex_map.flush
        
            #copy evolution file to new location
            shutil.copy(file_namer(poke_edit_data.evolution_path, pokemon, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.evolution_path, start_location + offset, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension))
        
            #zero out old evolution block
            with open(file_namer(poke_edit_data.evolution_path, pokemon, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as evolution_hex_map:
                    evolution_hex_map.flush

                    for x in range(0, poke_edit_data.evolution_table_length):
                        evolution_hex_map[x] = 0x00
                    evolution_hex_map.flush
        
            #copy levelup file to new location
            shutil.copy(file_namer(poke_edit_data.levelup_path, pokemon, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.levelup_path, start_location + offset, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension))
        
            #write Tackle at Level 1 to old location (avoid pk3ds crash)
            with open(file_namer(poke_edit_data.levelup_path, pokemon, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
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
    
    #offset to adjust for preexisting formes
    new_offset_start = len(existing_formes_array)
    
    for offset in range(0, new_forme_count):
        #user will have specified which existing Forme to copy from
        
        #copy source personal file to new location
        shutil.copy(file_namer(poke_edit_data.personal_path, personal_source_index, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.personal_path, start_location + offset + new_offset_start, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension))
        personal_file_update(poke_edit_data, start_location + offset + new_offset_start, total_formes, start_location)
        #print(start_location + offset + new_offset_start)
        #copy evolution file to new location
        shutil.copy(file_namer(poke_edit_data.evolution_path, evolution_source_index, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.evolution_path, start_location + offset + new_offset_start, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension))
        
        #copy levelup file to new location
        shutil.copy(file_namer(poke_edit_data.levelup_path, levelup_source_index, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.levelup_path, start_location + offset + new_offset_start, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension))
        
        
    
    #rebuild personal compilation file
    concatenate_bin_files(poke_edit_data.personal_path)
    
    
    print("New data initialized")
    
    #create new sets of model files
    #don't forget model index starts from 0 unlike everything else
    #first figure out which files we're copying
    total_previous_models = 0
    
    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
            model_hex_map.flush
            #first need to go to the four bytes for that *species*, which start at (index - 1)*4
            #the fourth byte, (index - 1)*4 + 3, is 0x1 when no formes, 0x3 when only alternate-gender formes, 0x7 when both
            #the third byte is how many models that species has.
            #The first and second bytes are a 2-byte little endian that is the *total number of models up to but not including the first model for that species*. So Bulby is 00 00 01 01 (no models before it), Venusaur is 02 00 03 07 (2 models before it, 3 models for Venusaur (male, female, and Mega), and has both gendered and non-gendered models
            
            #number of models on pokemon getting new forms + total number of models of all prior Pokemon
            total_previous_models = model_hex_map[4*(base_form_index - 1) + 2] + model_hex_map[4*(base_form_index - 1) + 1]*256 + model_hex_map[4*(base_form_index - 1) + 0]
            
            #if going with default model, need to grab the base-forme's model for model_source_index
            if(def_model):
                model_source_index = model_hex_map[4*(base_form_index - 1) + 1]*256 + model_hex_map[4*(base_form_index - 1) + 0]
            
            #print(model_source_index)
            #had to wait to open the file and grab the above so we could see where to insert the file
            
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
                #Need someone to check
                model_start_file = 8*(model_source_index)+2+1
                model_dest_file = 8*total_previous_models+2
                model_file_count = 8
            #assume SM or USUM
            else:
                model_start_file = 9*(model_source_index)+1
                model_dest_file = 9*total_previous_models
                model_file_count = 9
            
            print("Shifting model files")

            #shift the later model files forward
            for file_number, file in reversed(list(enumerate(poke_edit_data.model))):
                #if we've hit the *last* file of the Pokemon we're adding forme(s) too, stop this
                if(file_number == model_dest_file):
                    break
                
                #move file (# files per model)*(# new formes added) numbers forward
                os.rename(file_namer(poke_edit_data.model_path, file_number, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.model_path, file_number + model_file_count*new_forme_count, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension))
                #print(file_number, ': ', file_namer(poke_edit_data.model_path, file_number, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), ' to ', file_namer(poke_edit_data.model_path, file_number + model_file_count*new_forme_count, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension))
            #print(model_start_file, model_dest_file)
            #copies each of the source model/texture/animation files from A.bin to the filename cleared up by the previous for loop
            for x in range(0, new_forme_count):
                for y in range(0, model_file_count):
                    shutil.copy(file_namer(poke_edit_data.model_path, model_start_file + y, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension), file_namer(poke_edit_data.model_path, model_dest_file + x + y + 1, poke_edit_data.model_filename_length, poke_edit_data.extracted_extension))
            
            print("New model files initialized")
            print("Updating model header")
            
            #Now need to update model header
            
            #set the non-gendered form bit to true if not so set
            if(model_hex_map[4*(base_form_index - 1) + 3] < 0x05):
                model_hex_map[4*(base_form_index - 1) + 3] += 0x04
            
            
            #update the number of models for the species
            model_hex_map[4*(base_form_index - 1) + 2] += new_forme_count
            
            
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
            
            #write model file back
            model_hex_map.flush
            print('Model header updated')
    
    print('New formes initialized!' + '\n')

    #Now update the csv table. It might be perhaps slightly more efficient to do each bit as it happens above, but this code is easier to follow
    #first get the row number of all instances of the current species
    working_indices = find_rows_with_column_matching(poke_edit_data.master_list_csv, 2, int(base_form_index))
    
    
    #First, if we moved existing alt formes, need to update their Personal Index
    for offset, csv_index in enumerate(working_indices):
        if(poke_edit_data.master_list_csv[csv_index][3] in existing_formes_array):
            poke_edit_data.master_list_csv[csv_index][3] = start_location + offset
    
    #grab the base species name since we'll be using that at least once
    base_species_name = poke_edit_data.master_list_csv[working_indices[0]][0]
    
    #and the last model index number (as we inserted the models after that)
    model_index_start = poke_edit_data.master_list_csv[working_indices[-1]][4]
    
    #index we start inserting the new rows from
    csv_insertion_point = max(working_indices) + 1
    
    print(csv_insertion_point)

    #Second, we insert the new rows
    #base species index, personal file index, model index, species name, forme name
    for offset in range(new_forme_count):
        #note that model index is set to zero, since we will do one big sweep after this to update all that come after, anyway
        #Forme name is set to the number alt forme it is (e.g. if we add a forme to a Pokemon with 3 existing alt formes, it will be 4 (as the base species itself is 0))
        poke_edit_data.master_list_csv.insert(csv_insertion_point + offset, [base_species_name, new_offset_start + offset + 1, base_form_index, start_location + new_offset_start + offset, 0])
        
    #third we sweep through the entire array and update the model numbers, starting from the first newly inserted row
    for offset in range(csv_insertion_point, len(poke_edit_data.master_list_csv)):
        
        if(poke_edit_data.master_list_csv[offset][3] in poke_edit_data.modelless_formes):
                csv_insertion_point += 1
                continue
        poke_edit_data.master_list_csv[offset][4] = model_index_start + offset - csv_insertion_point + 1
        
    try:
        poke_edit_data = write_CSV(poke_edit_data)
    except:
        print('Please close your Pokemon Names and Files CSV if it is open')
        poke_edit_data.csv_pokemon_list_path = askopenfilename(title='Select Pokemon Names and Files CSV')
        write_CSV(poke_edit_data)
        
    poke_edit_data = load_names_from_CSV(poke_edit_data, True)
    
    print('Pokemon Names and Files CSV updated' + '\n')
    #refresh filenames
    poke_edit_data.run_model_later = False    
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.personal_path, "Personal", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.levelup_path, "Levelup", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.evolution_path, "Evolution", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.model_path, "Model", poke_edit_data.game)
    
    print('Internal tables updated with changes' + '\n' + '\n')
    

    return(poke_edit_data)
 

    
 
def add_new_forme_prelim(poke_edit_data, base_form_index, new_forme_count, model_source_index, personal_source_index, levelup_source_index, evolution_source_index, def_model):

    enough_room = False

    #Grab any existing formes
    existing_formes_array = []
    with open(file_namer(poke_edit_data.personal_path, base_form_index, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
            #find existing formes
            if(personal_hex_map[0x20] > 0x01):
                for offset in range(0, personal_hex_map[0x20] - 1):
                    existing_formes_array.append(personal_hex_map[0x1C] + personal_hex_map[0x1D]*256 + offset)
                    
    #find empty slot to write new forme(s) to
    start_location = 0
    
    total_alt_formes = len(existing_formes_array) + new_forme_count
    consecutive_open_found = 0
    print('\n' + "Looking for first empty space to write to")
    
    for index in range(poke_edit_data.max_species_index, 9999):
        path_temp = file_namer(poke_edit_data.personal_path, index, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension)
        #if path exists, check if the file is zeroed out (because we moved some other forme somewhere else)
        if(os.path.isfile(path_temp)):
            #if the file is zero, increment consecutive counter by 1
            if(file_is_zero(path_temp)):
                
                #if this is the first of this zero-block, tentatively grab it
                if(consecutive_open_found == 0):
                    start_location = index
                
                #increment counter
                consecutive_open_found += 1
                
                #case there is enough room here to put everything
                if(consecutive_open_found == total_alt_formes):
                    break
                #case there is enough cleared room after existing formes
                elif(consecutive_open_found == total_alt_formes - len(existing_formes_array) and index - consecutive_open_found == existing_formes_array[-1]):
                    start_location = existing_formes_array[0]
                    enough_room = True
                    #delete the zeroed out files to prepare:
                    for x in range(0, consecutive_open_found):
                        silentremove(file_namer(poke_edit_data.personal_path, existing_formes_array[-1] + x, poke_edit_data.personal_filename_length, poke_edit_data.extracted_extension))
                        silentremove(file_namer(poke_edit_data.evolution_path, existing_formes_array[-1] + x, poke_edit_data.evolution_filename_length, poke_edit_data.extracted_extension))
                        silentremove(file_namer(poke_edit_data.levelup_path, existing_formes_array[-1] + x, poke_edit_data.levelup_filename_length, poke_edit_data.extracted_extension))
                
            #otherwise check to see if the current file is big enough to be compilation file (we will overwrite it)
            elif(os.path.getsize(path_temp) > 84):
                start_location = index
                break
            #otherwise reset counter
            else:
                consecutive_open_found = 0
        #specific edge case wherein there is room for the new forme(s) after existing the pre-existing formes of that Pokemon and that is the last existing forme index
        elif(index - 1 == existing_formes_array[-1]):
            start_location = existing_formes_array[0]
            enough_room = True
            break
        #in this case, the compilation file does not exist, we are at the first empty slot and plant our flag here
        else:
            start_location = index
            break
    
    if(len(existing_formes_array) == 0):
        print('Existing formes moved, they now start at index ' + str(start_location))

    print('Inserted new forme(s) starting at index ' + str(start_location + new_forme_count))
    
    poke_edit_data = add_new_forme_execute(poke_edit_data, base_form_index, start_location, new_forme_count, model_source_index, personal_source_index, levelup_source_index, evolution_source_index, existing_formes_array, def_model, total_alt_formes, enough_room)
    return(poke_edit_data)