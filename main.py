from ast import Not
import shutil
import os
import sys
from tkinter import *
from tkinter import ttk
import errno
from my_constants import *
from file_handling import *
from forme_importation_actual import *


def pre_check():
    
    base_form_index = base_species_list.index(base_species_entry.get())
    new_forme_count = number_formes_entry.get()
    
    print(base_form_index, new_forme_count)

    if(model_bool or model_entry.get() == ''):
        #this is not the correct value, that will be computed later based on model_bool passing
        model_source_index = base_form_index
    else:
        model_source_index = model_source_list.index(model_entry.get())
    
    if(personal_bool or personal_entry.get() == ''):
        personal_source_index = base_form_index
    else:
        personal_source_index = master_formes_list.index(personal_entry.get())
    
    if(levelup_bool or levelup_entry.get() == ''):
        levelup_source_index = base_form_index
    else:
        levelup_source_index = master_formes_list.index(levelup_entry.get())
    
    if(evolution_bool or evolution_entry.get() == ''):
        evolution_source_index = base_form_index
    else:
        evolution_source_index = master_formes_list.index(evolution_entry.get())
    
    if(not(base_form_index.is_integer())):
        print("Species is not an integer!")
        return
    elif(not(new_forme_count.is_integer())):
        print("Formes to add is not an integer!")
        return
    elif(not(model_source_index.is_integer())):
        print("Model source is not an integer!")
        return
    elif(not(personal_source_index.is_integer())):
        print("Personal source is not an integer!")
        return
    elif(not(levelup_source_index.is_integer())):
        print("Levelup source is not an integer!")
        return
    elif(not(evolution_source_index.is_integer())):
        print("Evolution source is not an integer!")
        return


    add_new_forme_prelim(base_form_index, new_forme_count, model_source_index, personal_source_index, levelup_source_index, evolution_source_index, model_bool)

root = Tk()
root.geometry('750x300')

model_bool = BooleanVar()
personal_bool = BooleanVar()
levelup_bool = BooleanVar()
evolution_bool = BooleanVar()

def update(input_list, input_listbox):
    
    input_listbox.delete(0, END)
    
    for item in input_list:
        input_listbox.insert(END, item)


#not working
def fillout_base_species(e):
    base_species_entry.delete(0, END)
    base_species_entry.insert(END, base_species_listbox.get(ACTIVE))


#update search list for base species
def check_base_species(e):
    typed = base_species_entry.get()
    global current_base_species_list
    if typed == '':
        #reset everything
        data = base_species_list
    else:
        data = []
        for item in current_base_species_list:
            if typed.lower() in item.lower():
                data.append(item)
    current_base_species_list = data
    update(data, base_species_listbox)


#update listbox for personal source
def check_personal(e):
    typed = personal_entry.get()
    global current_personal_list
    if typed == '':
        #reset everything
        data = master_formes_list
    else:
        data = []
        for item in current_personal_list:
            if typed.lower() in item.lower():
                data.append(item)
    current_personal_list = data
    update(data, personal_listbox)


#update listbox for levelup source
def check_levelup(e):
    typed = levelup_entry.get()
    global current_levelup_list
    if typed == '':
        #reset everything
        data = master_formes_list
    else:
        data = []
        for item in current_levelup_list:
            if typed.lower() in item.lower():
                data.append(item)
    current_levelup_list = data
    update(data, levelup_listbox)

#update listbox for evolution source
def check_evolution(e):
    typed = evolution_entry.get()
    global current_evolution_list
    if typed == '':
        #reset everything
        data = master_formes_list
    else:
        data = []
        for item in current_evolution_list:
            if typed.lower() in item.lower():
                data.append(item)
    current_evolution_list = data
    update(data, evolution_listbox)

#update listbox for model source
def check_model(e):
    typed = model_entry.get()
    global current_model_source_list
    if typed == '':
        #reset everything
        data = model_source_list
    else:
        data = []
        for item in current_model_source_list:
            if typed.lower() in item.lower():
                data.append(item)
    current_model_source_list = data
    update(data, model_listbox)






#load/save config
cfg_load = Button(root, text = 'Load CFG', command = lambda: load_game_cfg(), height = 2, width = 12, pady = 5, padx = 7)
cfg_load.grid(row = 0, column = 0)


cfg_save = Button(root, text = 'Save/Set CFG', command = lambda: save_game_cfg(), height = 2, width = 12, pady = 5, padx = 7)
cfg_save.grid(row = 1, column = 0)


#select game
games = ["XY", "ORAS", "USUM"]

games_temp = StringVar(root)
games_temp.set(games[0])
game_select = OptionMenu(root, games_temp, *games)
game_select.grid(row = 0, column = 1)


#load Model
model_load = Button(root, text = 'Select Model Path', command = lambda: choose_GARC("Model", games_temp), height = 2, width = 15, pady = 5, padx = 7)
model_load.grid(row = 0, column = 2)

#load Personal
personal_load = Button(root, text = 'Select Personal Path', command = lambda: choose_GARC("Personal", games_temp), height = 2, width = 15, pady = 5, padx = 7)
personal_load.grid(row = 0, column = 3)

#load Levelup
levelup_load = Button(root, text = 'Select Levelup Path', command = lambda: choose_GARC("Levelup", games_temp), height = 2, width = 15, pady = 5, padx = 7)
levelup_load.grid(row = 0, column = 4)

#load Evolution
evolution_load = Button(root, text = 'Select Evolution Path', command = lambda: choose_GARC("Evolution", games_temp), height = 2, width = 15, pady = 5, padx = 7)
evolution_load.grid(row = 0, column = 5)



#Base Species Selection
base_species_label = Label(root, text = "Select Species", width = 12, padx = 7)
base_species_label.grid(row = 2, column = 0)

base_species_entry = Entry(root, width = 15)
base_species_entry.grid(row = 3, column = 0)

base_species_listbox = Listbox(root, width = 15)
base_species_listbox.grid(row = 4, column = 0)

update(base_species_list, base_species_listbox)

base_species_listbox.bind("<<ListBoxSelect>>", fillout_base_species)
base_species_entry.bind("<KeyRelease>", check_base_species)


#Model Selection

model_checkbutton = Checkbutton(root, text = 'Same as Species', variable = model_bool, onvalue = True, offvalue = False)
model_checkbutton.grid(row = 1, column = 2)
model_checkbutton.select()

model_label = Label(root, text = "Custom Model", width = 12, padx = 3)
model_label.grid(row = 2, column = 2)

model_entry = Entry(root, width = 15)
model_entry.grid(row = 3, column = 2)

model_listbox = Listbox(root, width = 15)
model_listbox.grid(row = 4, column = 2)

update(model_source_list, model_listbox)

model_entry.bind("<KeyRelease>", check_model)


#Personal Selection

personal_checkbutton = Checkbutton(root, text = 'Same as Species', variable = personal_bool, onvalue = True, offvalue = False)
personal_checkbutton.grid(row = 1, column = 3)
personal_checkbutton.select()

personal_label = Label(root, text = "Custom Personal", width = 12, padx = 3)
personal_label.grid(row = 2, column = 3)

personal_entry = Entry(root, width = 15)
personal_entry.grid(row = 3, column = 3)

personal_listbox = Listbox(root, width = 15)
personal_listbox.grid(row = 4, column = 3)

update(master_formes_list, personal_listbox)


personal_entry.bind("<KeyRelease>", check_personal)


#Levelup Selection

levelup_checkbutton = Checkbutton(root, text = 'Same as Species', variable = levelup_bool, onvalue = True, offvalue = False)
levelup_checkbutton.grid(row = 1, column = 4)
levelup_checkbutton.select()

levelup_label = Label(root, text = "Custom Levelup", width = 12, padx = 3)
levelup_label.grid(row = 2, column = 4)

levelup_entry = Entry(root, width = 15)
levelup_entry.grid(row = 3, column = 4)

levelup_listbox = Listbox(root, width = 15)
levelup_listbox.grid(row = 4, column = 4)

update(master_formes_list, levelup_listbox)


levelup_entry.bind("<KeyRelease>", check_levelup)

#Evolution Selection

evolution_checkbutton = Checkbutton(root, text = 'Same as Species', variable = evolution_bool, onvalue = True, offvalue = False)
evolution_checkbutton.grid(row = 1, column = 5)
evolution_checkbutton.select()

evolution_label = Label(root, text = "Custom Evolution", width = 12, padx = 4)
evolution_label.grid(row = 2, column = 5)

evolution_entry = Entry(root, width = 15)
evolution_entry.grid(row = 3, column = 5)

evolution_listbox = Listbox(root, width = 15)
evolution_listbox.grid(row = 4, column = 5)

update(master_formes_list, evolution_listbox)


evolution_entry.bind("<KeyRelease>", check_evolution)

#Number of New Formes


number_formes_label = Label(root, text = "# Formes To Add", width = 12, padx = 4)
number_formes_label.grid(row = 2, column = 1)

number_formes_entry = Entry(root, width = 15)
number_formes_entry.grid(row = 3, column = 1)

#Run

execute_buttom = Button(root, text = 'Insert Forme(s)', command = lambda: pre_check(), height = 2, width = 15, pady = 5, padx = 7)
execute_buttom.grid(row = 4, column = 1)


root.mainloop()
