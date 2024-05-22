import errno
import mmap
import os

from my_constants import *


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
def file_namer(folder, index, length, poke_edit_data, file_prefix = ''):
    
    return(os.path.join(folder, file_prefix + str(index).zfill(length)) + poke_edit_data.extracted_extension)

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
