import shutil
import os
import mmap
from tkinter.filedialog import asksaveasfile
from my_constants import *
from user_data_handling import *

#Sorts Forme file order of Personal, Evolution, and Levelup Garc folders in order to allow for new formes of existing multi-formed Pokemon to be added
def resort_file_structure(poke_edit_data):
    
    forme_location_reference_array = []
    new_personal_index = poke_edit_data.max_species_index + 1
    


    
    #delete any files after max_species_index, if they exist. This clears the compilation file and any zero files from old versions

    print("Removing old compilation file and zero files in range")
    for file_number in range(poke_edit_data.max_species_index + 1, int(poke_edit_data.personal[-1]) + 28):
        try:
            #only delete starting from the compilation file
            if(os.path.getsize(file_namer(poke_edit_data.personal_path, file_number, poke_edit_data.personal_filename_length, poke_edit_data)) > 84):
                silentremove(file_namer(poke_edit_data.personal_path, file_number, poke_edit_data.personal_filename_length, poke_edit_data))
                silentremove(file_namer(poke_edit_data.evolution_path, file_number, poke_edit_data.evolution_filename_length, poke_edit_data))
                silentremove(file_namer(poke_edit_data.levelup_path, file_number, poke_edit_data.levelup_filename_length, poke_edit_data))
        except:
            for x in range(file_number, int(poke_edit_data.personal[-1]) + 28):
                silentremove(file_namer(poke_edit_data.personal_path, x, poke_edit_data.personal_filename_length, poke_edit_data))
                silentremove(file_namer(poke_edit_data.evolution_path, x, poke_edit_data.evolution_filename_length, poke_edit_data))
                silentremove(file_namer(poke_edit_data.levelup_path, x, poke_edit_data.levelup_filename_length, poke_edit_data))
            break
            
    print("Preparing to rebuild Forme file order")
    
    new_forme_pointer = 0
    #build table for sorting
    for row_number, row in enumerate(poke_edit_data.master_list_csv):
        #checks to see if alternate forme with own data (so has personal file location after max species index)=
        #2 is nat dex, 3 is personal
        
        #if the current nat dex number is bigger than the previous, we need to set the internal forme pointer equal to the current personal index
            
        if(row[2] != ''):
            if(isinstance(poke_edit_data.master_list_csv[row_number - 1][2], int) and isinstance(row[2], int)):
                if(poke_edit_data.master_list_csv[row_number - 1][2] < row[2]):
                    new_forme_pointer = new_personal_index
                
            if(row[3] != '' and row[3] > row[2]):
                
                #create entry in array row_number of csv, species index, forme personal index (old filename), the new personal index offset, and the new forme pointer
                forme_location_reference_array.append([row_number, row[2], row[3], new_personal_index, new_forme_pointer])
                
            
                #increment forme order
                new_personal_index += 1
            
            
    #iterate through the table of formes we built. rename each file starting in order from max_species_index + 1, and update the pointers in each (and the base species if it's the first instance).
    

    #update CSV
    for sort_array_row in forme_location_reference_array:
        #CSV
        poke_edit_data.master_list_csv[sort_array_row[0]][3] = sort_array_row[3]

    #grab just the old and new file names, and the pointers
    to_sort_table = entire_of_columns(forme_location_reference_array, [2, 3, 4, 1])

    #we need to figure out an order of renaming files. need to find the file going to the highest personal index, pull that to the end, then again until all done
    
    renaming_order_table = sort_table_personal_files(to_sort_table)

    for row in renaming_order_table:

        #rename the Personal file to new name
        dropbox_workaround_file_rename(file_namer(poke_edit_data.personal_path, row[0], poke_edit_data.personal_filename_length, poke_edit_data), file_namer(poke_edit_data.personal_path, row[1], poke_edit_data.personal_filename_length, poke_edit_data))
            
        #rename the Evolution file to new name
        dropbox_workaround_file_rename(file_namer(poke_edit_data.evolution_path, row[0], poke_edit_data.evolution_filename_length, poke_edit_data), file_namer(poke_edit_data.evolution_path, row[1], poke_edit_data.evolution_filename_length, poke_edit_data))
              
        #rename the Levelup file to new name
        dropbox_workaround_file_rename(file_namer(poke_edit_data.levelup_path, row[0], poke_edit_data.levelup_filename_length, poke_edit_data), file_namer(poke_edit_data.levelup_path, row[1], poke_edit_data.levelup_filename_length, poke_edit_data))

        #now update the forme's personal file pointer, then the base forme's pointer
        poke_edit_data = personal_file_update(poke_edit_data, row[1], -1, row[2])
        
        #and the base species
        poke_edit_data = personal_file_update(poke_edit_data, row[3], -1, row[2])
        
        
    #rebuild personal compilation file
    concatenate_bin_files(poke_edit_data.personal_path)
    

    #refresh filenames
    poke_edit_data.run_model_later = False    
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.personal_path, "Personal", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.levelup_path, "Levelup", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.evolution_path, "Evolution", poke_edit_data.game)
    poke_edit_data = load_GARC(poke_edit_data, poke_edit_data.model_path, "Model", poke_edit_data.game)
    print('Internal tables updated with changes' + '\n')

    return(poke_edit_data)        

def check_adding_without_models_works(poke_edit_data, base_form_index, new_forme_count):
    
    temp_forme_count_from_personal_file_count = 1
    explicit_forme_count = 0
    update_forme_count = 0
    
    #get the number of Personal files this pokemon actually has
    with open(file_namer(poke_edit_data.personal_path, base_form_index, poke_edit_data.personal_filename_length, poke_edit_data), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
            explicit_forme_count = personal_hex_map[0x20]
            #find existing formes
            if(explicit_forme_count > 0x01):
                temp_pointer = personal_hex_map[0x1C] + personal_hex_map[0x1D]*256
                if(temp_pointer != 0):
                    for offset in range(0, explicit_forme_count - 1):
                        with open(file_namer(poke_edit_data.personal_path, temp_pointer + offset, poke_edit_data.personal_filename_length, poke_edit_data), "r+b") as f_temp:
                            with mmap.mmap(f_temp.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map_temp:
                                if(temp_pointer == personal_hex_map_temp[0x1C] + personal_hex_map_temp[0x1D]*256):
                                    temp_pointer += 1
                                    temp_forme_count_from_personal_file_count += 1

    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
            model_hex_map.flush()
			#number of models this species has
            temp_model_count = model_hex_map[4*(base_form_index - 1) + 2]
			

            #if the number of models is greater than or equal to the total number of personal file formes plus the number being inserted, we're good (e.g. inserting 1 for Venusaur, 2 personal filed (base and mega), but 3 model files (male base, female base, mega), so 3 >= 2 + 1), we are good to go. Flip the cosmetic female forme flag off if needed, and return true

            if(temp_model_count >= temp_forme_count_from_personal_file_count + new_forme_count):

                #need to figure out if the alt formes are including in forme count
                
                #explicit_forme_count is >= the number of existing unique data instances plus the ones being added, we don't need to increase the explicit forme count. Otherwise, we need to update that. Could just do a max but this is clearer and trivially more overhead
                if(explicit_forme_count >= temp_forme_count_from_personal_file_count + new_forme_count):
                    update_forme_count = explicit_forme_count
                else:
                    update_forme_count = temp_forme_count_from_personal_file_count + new_forme_count

			    #unset the "female cosmetic forme" flag if set
                if model_hex_map[4*(base_form_index - 1) + 3] in {3, 7}:
                    model_hex_map[4*(base_form_index - 1) + 3] = 5
                    model_hex_map.flush()
                return(poke_edit_data, True, update_forme_count)
            else:
                print('There are ' + str(temp_model_count) + ' model files and ' + str(temp_forme_count_from_personal_file_count) + ' Personal files, aborting.')
                return(poke_edit_data, False, 0)

#handles actual editing and moving of files for forme insertion
def add_new_forme_execute(poke_edit_data, base_form_index, new_forme_count, model_source_index, personal_source_index, levelup_source_index , evolution_source_index, def_model, skip_model_insertion, update_forme_count):
    
    
    #first unused file name
    start_location = 0
    
    #checks to ensure that the evolution and levelup folders have the same number of files, and that the personal folder has either 1 more (because compilation file) or the same (if it was removed)
    if(poke_edit_data.evolution[-1]  ==  poke_edit_data.levelup[-1] and (poke_edit_data.levelup[-1] in {poke_edit_data.personal[-1], poke_edit_data.personal[-2]})):
        #start from 255 later so we ALWAYS have room to sort things easily when we do the final step
        start_location = int(poke_edit_data.evolution[-1]) + 1 + 255
    else:
        print('Mismatch in file counts:\n')
        print('Personal has:', poke_edit_data.personal[-1], 'files')
        print('Levelup has:', poke_edit_data.levelup[-1], 'files')
        print('Evolution has:', poke_edit_data.evolution[-1], 'files')
        return(poke_edit_data)
    
    #Grab any existing formes
    existing_formes_array = []

    total_formes = new_forme_count
    
    print('\n\nUpdating existing files for species ' + str(base_form_index))
    with open(file_namer(poke_edit_data.personal_path, base_form_index, poke_edit_data.personal_filename_length, poke_edit_data), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as personal_hex_map:
            
            #forme count is not going to change, since we are initializing unique data for existing cosmetic formes
            if(skip_model_insertion):
                total_formes = update_forme_count
            else:
                #Get the new total number of formes
                total_formes += personal_hex_map[0x20]
            
                #find existing formes
                if(personal_hex_map[0x20] > 0x01):
                    for offset in range(0, personal_hex_map[0x20] - 1):
                        temp_pointer = personal_hex_map[0x1C] + personal_hex_map[0x1D]*256 + offset
                    
                        #save current forme file pointer to the formes array
                        existing_formes_array.append(temp_pointer)
                    
                        #set new number of total formes. Don't bother resetting the internal forme pointer because that will be handled by the sort at the end
                        personal_file_update(poke_edit_data, temp_pointer, total_formes, -1)
            
                #set new number of formes in this personal file as well before we exit
            personal_hex_map[0x20] = total_formes
                    
    
    print("Initializing new game data")
    #now initialize the newly added formes

    #delete the old compilation file if it's there
    if(os.path.getsize(file_namer(poke_edit_data.personal_path, poke_edit_data.personal[-1], poke_edit_data.personal_filename_length, poke_edit_data)) > 84):
        silentremove(file_namer(poke_edit_data.personal_path, poke_edit_data.personal[-1], poke_edit_data.personal_filename_length, poke_edit_data)) 
    
    for offset in range(0, new_forme_count):
        #user will have specified which existing Forme to copy from
        
        #copy source personal file to new location
        shutil.copy(file_namer(poke_edit_data.personal_path, personal_source_index, poke_edit_data.personal_filename_length, poke_edit_data), file_namer(poke_edit_data.personal_path, start_location + offset, poke_edit_data.personal_filename_length, poke_edit_data))
        
        #update new forme to have appropriate offset and forme count
        personal_file_update(poke_edit_data, start_location + offset, total_formes, start_location)
       
        #copy evolution file to new location
        shutil.copy(file_namer(poke_edit_data.evolution_path, evolution_source_index, poke_edit_data.evolution_filename_length, poke_edit_data), file_namer(poke_edit_data.evolution_path, start_location + offset, poke_edit_data.evolution_filename_length, poke_edit_data))
        
        #copy levelup file to new location
        shutil.copy(file_namer(poke_edit_data.levelup_path, levelup_source_index, poke_edit_data.levelup_filename_length, poke_edit_data), file_namer(poke_edit_data.levelup_path, start_location + offset, poke_edit_data.levelup_filename_length, poke_edit_data))

    if(skip_model_insertion):
        poke_edit_data = update_csv_after_changes(poke_edit_data, base_form_index, new_forme_count, start_location, True)
    else:
        print("Initializing new model data")
    
        #create new sets of model files
        #don't forget model index starts from 0 unlike everything else
        #first figure out which files we're copying
        total_previous_models = 0
    
        with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data), "r+b") as f:
            with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
                model_hex_map.flush()
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
                    dropbox_workaround_file_rename(file_namer(poke_edit_data.model_path, file_number, poke_edit_data.model_filename_length, poke_edit_data, poke_edit_data.model_folder_prefix), file_namer(poke_edit_data.model_path, file_number + model_file_count*new_forme_count, poke_edit_data.model_filename_length, poke_edit_data, poke_edit_data.model_folder_prefix))
                       
                    #update the model file list. Otherwise if we do more than 1 forme it will miss the last files and crash
                    poke_edit_data.model.append(file_number + model_file_count*new_forme_count)
                
                #print(model_start_file, model_dest_file)
                #copies each of the source model/texture/animation files from A.bin to the filename cleared up by the previous for loop
                for x in range(0, new_forme_count):
                    for y in range(0, model_file_count):
                        shutil.copy(file_namer(poke_edit_data.model_path, model_start_file + y, poke_edit_data.model_filename_length, poke_edit_data, poke_edit_data.model_folder_prefix), file_namer(poke_edit_data.model_path, model_dest_file + x*model_file_count + y + 1, poke_edit_data.model_filename_length, poke_edit_data, poke_edit_data.model_folder_prefix))
            
                #reset the model filename list, since we added stuff to the end
                poke_edit_data.model = []
                for filename in os.listdir(poke_edit_data.model_path):
                    filename_stripped, ext = os.path.splitext(filename)
                    poke_edit_data.model.append(filename_stripped)
            
                print("New model files initialized")
                print("Updating model header")
            
                #Now need to update model header
                '''
                    0x1 == Any model exists?
                    0x2 == Gender-difference model/forme exists. It seems that if this is set AND the next bit is not set, then the 2nd model goes to the 2nd personal file (it assumes it's an alt-gender forme like Meowstic)
                    0x4 == other cause of forme models. If this is set, then the 2nd model is assumed to be for the female of the base species, and the 3rd model goes to the 2nd personal file, etc.
                '''
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
           
            

                ''':

                Most pokemon are 00 00 as Axyn observed in gen VI

                Totem Raticate, Totem Marowak, and Zygarde 10% with Power Construct are 07 01

                Furfrou Star Trim, Furfrou Diamond Trim, and the Hat Pikachu for Johto, Sinnoh, Unova, Kalos, and Alola are 00 01

                All the other totems except for Ribombee, Zygarde 50% with Power Construct, Medium and Large Pumpkaboo and Gourgeist are 07 00

                Furfrou Matron Trim & Furfrou Dandy Trim are 00 04

                Furfrou Kabuki Trim, Furfrou Pharaoh Trim, and all Minior Core Formes except for Red are 00 07

                All Female Gender Difference models (except for Frillish, Jellicent, Pyroar, & Meowstic), all Silvally and Arceus (except for Normal), the entire Flabebe line except for Red and Eternal Floette, all Vivillon except for Icy Snow, Genesect w/ drive, Deerling/Sawsbuck except Spring, non-Zen Darmanitan, & Blue Basculin are 01 00

                '''
            
            
                #first entry (Bulbasaur model) is at 4*(max_species_index + 1)
                start_of_byte_flag_table = 4*(poke_edit_data.max_species_index + 1)
                


                #update csv with new model indices & also the model type table
                poke_edit_data = update_csv_after_changes(poke_edit_data, base_form_index, new_forme_count, start_location, False, model_source_index)


                #add 2*<number formes added> bytes to the model table
                model_hex_map.resize(len(model_hex_map) + 2*new_forme_count)
                
                csv_row = 1

                #update the file in memory with the new table
                for offset in range(start_of_byte_flag_table, 2, len(model_hex_map)):
                    if(isinstance(poke_edit_data.master_list_csv[csv_row][4], int)):
                        model_hex_map[offset] = poke_edit_data.master_list_csv[csv_row][5]
                        model_hex_map[offset + 1] = poke_edit_data.master_list_csv[csv_row][6]
                    csv_row += 1
                   

                #write model file back to disk    
                model_hex_map.flush()
            
                print('Model header updated')
    
    print('New formes initialized!' + '\n')

    #finally, we sort the files so everything works nicely
    poke_edit_data = resort_file_structure(poke_edit_data)
        
    try:
        poke_edit_data = write_CSV(poke_edit_data)
    except:
        print('Please close your Pokemon Names and Files CSV if it is open')
        poke_edit_data.csv_pokemon_list_path = asksaveasfile(title='Select Pokemon Names and Files CSV')
        write_CSV(poke_edit_data)
    print('Pokemon Names and Files CSV updated' + '\n')
        
    #poke_edit_data = load_names_from_CSV(poke_edit_data)
                         
    print('Insertion complete!\n')
    return(poke_edit_data)