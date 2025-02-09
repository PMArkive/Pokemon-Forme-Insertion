import mmap
import os
import pathlib
import time
from struct import unpack


#read input bytestring as little-endian, return integer
def fromlittlebytesint(byte_input):
    return(unpack("<I", byte_input)[0])

#pull a given non-empty column from the given table and returns the max
def max_of_column(input_table, column_number) -> int:
    max_temp = 0
    for rows in input_table:
        try:
            if (int(rows[column_number]) > max_temp):
                max_temp = int(rows[column_number])
        except ValueError:
            max_temp = max_temp

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

#returns a list of the indices of the rows that contain the specified search term in the specified column. If only_one is true, then it returns the first one it finds instead
def find_rows_with_column_matching(input_table, column_number, search_term, only_one = False):
    found_table = []
    for row_index, rows in enumerate(input_table):
        if(rows[column_number] == search_term):
            if(only_one):
                return(row_index)
            else:
                found_table.append(row_index)
    return(found_table)

#streamline the file name-calling
def file_namer(folder, index, length, poke_edit_data, file_prefix = ''):
    
    return(os.path.join(folder, file_prefix + str(index).zfill(length)) + poke_edit_data.extracted_extension)

#removes file, exception thrown if not exist
def silentremove(filename: str) -> None:
    pathlib.Path(filename).unlink(missing_ok=True)

#check if file is zeroed out
def file_is_zero(string) -> bool:
    with open(string) as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as personal_hex_map:
            for x in personal_hex_map:
                if(x != 0x0):
                    return(False)
    return(True)
		
#convert integer to little endian as long as two bytes at most
def little_endian_chunks(big_input: int) -> tuple[int, int]:
    little = big_input.to_bytes(2, byteorder="little")
    return (little[0], little[1])


#calls os.rename. if file is in use, it will wait for various amounts of seconds then try again
def dropbox_workaround_file_rename(old_name, new_name):
    
    try:
        os.rename(old_name, new_name)
        return
    except:
        time.sleep(1)
        try:
            os.rename(old_name, new_name)
        except:
            time.sleep(5)
            try:
                os.rename(old_name, new_name)
            except:
                time.sleep(10)
                try:
                    os.rename(old_name, new_name)
                except:
                    time.sleep(30)
                    try:
                        os.rename(old_name, new_name)
                    except:
                        print('File ' + old_name + 'is open in some program, being uploaded by Dropbox, etc.' + 'This program will now wait another 120 seconds (already waited for 46).')
                        time.sleep(120)
                        try:
                            os.rename(old_name, new_name)
                        except:
                            print('Will try one more time, waiting for 360 seconds')
                            time.sleep(360)
                            try:
                                os.rename(old_name, new_name)
                            except:
                                print('That did not work. I am going to throw an error now. I was partway through renaming files, so you should delete those folders and restore from your last good GARC.')
                            


#returns list of specified columns from specified table
def entire_of_columns(input_table, column_numbers_list):
    table_temp = []
    for row_input in input_table:
        row_temp = []
        for column in column_numbers_list:
                row_temp.append(row_input[column])
        table_temp.append(row_temp)
    return(table_temp)


#takes the table and reorders it so that the thing going somewhere empty has room, then moves the thing to where that one was, etc. Then repeats until done
def sort_table_personal_files(to_sort_table):
            
    #old, new, pointer
    order_table = []
    

    #there's a big gap between the last "real" personal file and the newly insert files, need to find the last real one
    #find the smallest number in old that's bigger than the biggest in new. This is the first new forme file, so the real max personal pre-insert will be the next biggest number    
    max_personal_new = max_of_column(to_sort_table, 1)
    
    smallest_dummy_personal_old = 999999

    for row in to_sort_table:
        if(max_personal_new < row[0] < smallest_dummy_personal_old):
            smallest_dummy_personal_old = row[0]
            
    max_personal_old = 0 
    for row in to_sort_table:
        if(max_personal_old < row[0] < smallest_dummy_personal_old):
            max_personal_old = row[0]
                



   # try:
    while True:
        #finds the highest destination file number left, adds that
        order_table.append(to_sort_table.pop(find_rows_with_column_matching(to_sort_table, 1, max_of_column(to_sort_table, 1))[0]))
        
        
        #if these are equal, no chain to follow
        if(order_table[-1][0] != order_table[-1][1]):
            while True:
                #takes the most recently added line the order table, and gets the filenumber it came from.
                next_personal = order_table[-1][0]
    
                #if next_personal is bigger than the largest destination file (max_personal), the file we just moved is one of the newly inserted Pokemon, so there is nothing more to add from this chain,
                if(next_personal >= max_personal_old or len(to_sort_table) == 0):
                    break
                else:
                    #grab the thing that is going to where the previous file was
                    order_table.append(to_sort_table.pop(find_rows_with_column_matching(to_sort_table, 1, next_personal)[0]))
                    
            if(len(to_sort_table) == 0):
                    break
        elif(len(to_sort_table) == 0):
            break
    for x in to_sort_table:
        order_table.append(x)
        
    return(order_table)