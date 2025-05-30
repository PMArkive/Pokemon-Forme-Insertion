from forme_importation_actual import *
from utilities import *



def export_levelup(move_edit_data, move_list, pokemon_list):

    #load levelup GARC
    move_edit_data = choose_GARC(move_edit_data, 'Levelup', move_edit_data.game)

    #choose output path for dump
    save_path = asksaveasfilename(title='Save exported table of Level-Up Moves', defaultextension='.csv',filetypes= [('CSV','.csv')])

    with open(save_path, 'w', newline = '', encoding='utf-8-sig') as csvfile:
        writer_head = csv.writer(csvfile, dialect='excel', delimiter=',')

        #write the header line
        writer_head.writerow (['Personal Index', 'Name', 'Level', 'Move'])

        #iterate over all files
        for index, file in enumerate(move_edit_data.levelup):
            for entry_index in range(len(file)//4):
                move_index = from_little_bytes_int(file[entry_index*4:entry_index*4 + 2])
                level = file[entry_index*4 + 2]

                #don't edit terminator
                if(level == 0xFF and move_index == 0xFFFF):
                    pass
                else:
                    writer_head.writerow ([index, pokemon_list[index], level, move_list[move_index]])
            #write blank line after every Pokemon for easy reading
            writer_head.writerow (['', '', '', ''])
            
def import_levelup(move_edit_data, move_list, pokemon_list):

    #initialize with Pokemon 0's empty file, just has terminator
    output_array = [[0xFF, 0xFF, 0xFF, 0xFF]]

    temp_array = []

    #choose edited .csv
    save_path = askopenfilename(title='Choose edited table of Level-Up Moves', defaultextension='.csv',filetypes= [('CSV','.csv')])

    #get data from csv individual binary files
    with open(save_path, 'r', newline = '', encoding='utf-8-sig') as csvfile:
        reader_head = csv.writer(csvfile, dialect='excel', delimiter=',')

        temp_array = list(reader_head)



    #convert levelup move name to all lower case to ease search

    for x in range(len(move_list)):
        move_list[x] = move_list[x].lower()

    #build the new set of binary files

    last_personal = 1
    temp_file = []
    for line in temp_array:
        #no file for header or blank space
        if(line[0] in {'','Personal Index'}):
            pass
        else:
            #if not-equal, starting next file
            if(line[0] != last_personal):
                #append terminator to previous file
                temp_file.extend([0xFF, 0xFF, 0xFF, 0xFF])
                #append current file to array
                output_array.append(temp_file)
                #clear temp
                temp_file = []
                #update last personal
                last_personal = line[0]

            #get move index
            temp_index = move_list.index(line[3].lower())

            #move index, low byte then high
            temp_file.append(temp_index%0x100)
            temp_file.append(temp_index >> 8)
            #level
            temp_file.append(int(line[2]))
            #unused
            temp_file.append(0x00)
    #final loop ends without appending last file, handle it now
    temp_file.extend([0xFF, 0xFF, 0xFF, 0xFF])
    output_array.append(temp_file)

    move_edit_data.levelup = output_array

    save_GARC(move_edit_data, levelup):

    return(move_edit_data)


def main():
    move_edit_data = Pokedata()
    action_choice = ''
    
    current_directory = os.getcwd()
    move_list_path = os.path.join(current_directory, 'move_list.csv')

    move_list = []
    pokemon_list = []

    #get generation
    while True:
        temp = input('Enter Generation, (XY, ORAS, SM, USUM)\n').upper()
        if(temp in {'XY', 'ORAS', 'SM', 'USUM'}):
            move_edit_data.game = temp
            break
        else:
            print(temp, 'is not valid\n\n')
        
    pokemon_list_path = os.path.join(current_directory, 'pokemon_list_' + move_edit_data.game + '.csv')

    #load move names
    with open(move_list_path, newline = '', encoding='utf-8-sig') as csvfile:
        reader_head = csv.reader(csvfile, dialect='excel', delimiter=',')
        
        #load csv into an array      
        temp = list(reader_head)

        for line in temp:
            if(line[1] != ''):
                move_list.append(line[1])
            else:
                break
    print('Loaded Move Name List')


    #load pokemon names
    with open(pokemon_list_path, newline = '', encoding='utf-8-sig') as csvfile:
        reader_head = csv.reader(csvfile, dialect='excel', delimiter=',')
        
        #load csv into an array      
        temp = list(reader_head)

        for line in temp:
            if(line[1] != '' or line[0] == '0'):
                pokemon_list.append(line[1])
            else:
                break
    print('Loaded Pokemon Name List')

    while True:

        #choose extract or rebuild
        while True:
            temp = input('Extract or rebuild Level-Up GARC, or quite? (e/r/q)\n').lower()
            if(temp in {'e', 'r', 'q'}):
                action_choice = temp
                break
            else:
                print(temp, 'is not valid\\nn')

        match action_choice:
            case 'e':
                export_levelup(move_edit_data, move_list, pokemon_list)
            case 'r':
                import_levelup(move_edit_data, move_list, pokemon_list)
            case 'q':
                return


main()