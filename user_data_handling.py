import csv
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename

from file_handling import *


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
                    #check to see if model file is decompressed
                    if('dec_' in temp[-1]):
                        poke_edit_data.model_folder_prefix = 'dec_'
                    poke_edit_data = update_model_list(poke_edit_data)
                    #conditional_update_modelless_formes_list(poke_edit_data)
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
                case "Model":
                    targetpath = '007'
                case "Personal":
                    targetpath = '218'
                case "Levelup":
                    targetpath = '214'
                case "Evolution":
                    targetpath = '215'
            poke_edit_data.modelless_exists = False
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
            poke_edit_data.modelless_exists = False
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
            poke_edit_data.modelless_exists = False
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
    
    with open(file_namer(poke_edit_data.model_path, 0, poke_edit_data.model_filename_length, poke_edit_data), "r+b") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_WRITE) as model_hex_map:
            
            for x in range(poke_edit_data.max_species_index + 1):
                #the third byte is how many models that species has.
                species_model_count.append(model_hex_map[4*x + 2])
    
    #row 0 has the empty personal file, skip to next before first iteration
    row_index = 0
    model_index = 0


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
        with open(file_namer(poke_edit_data.personal_path, current_base_species, poke_edit_data.personal_filename_length, poke_edit_data), "r+b") as f:
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
    temp_loaded_csv = []

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
            for _ in range(personal_max_temp + 1):
                temp_master_formes_list.append('')
                
            for data_rows in loaded_csv_file:
                
                #build the actual csv file

                temp_row = [data_rows[3], data_rows[4], '', '', '']

                try:
                    temp_row[2] = int(data_rows[0])
                except:
                    temp_row[2] = data_rows[0]
                try:
                    temp_row[3] = int(data_rows[1])
                except:
                    temp_row[3] = data_rows[1]
                try:
                    temp_row[4] = int(data_rows[2])
                except:
                    temp_row[4] = data_rows[2]
                    
                temp_loaded_csv.append(temp_row)
                
                #print(temp_row)
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
    

    
    poke_edit_data.master_list_csv = temp_loaded_csv.copy()

    return(poke_edit_data)


#just asks for the path and calls the write-csv-to-the-right-part-of-the-class-data-structure program
def user_prompt_load_CSV(poke_edit_data, target):

    poke_edit_data.csv_pokemon_list_path = askopenfilename(title='Select ' + target + ' CSV')
    

    poke_edit_data = load_names_from_CSV(poke_edit_data)
    

    return(poke_edit_data)

def create_refresh_CSV(poke_edit_data, gameassert):
    

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
    
    if(poke_edit_data.modelless_exists and poke_edit_data.game == 'USUM'):
        temp_modelless = 'True'
    else:
        temp_modelless = 'False'
        poke_edit_data.game = False
    
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
