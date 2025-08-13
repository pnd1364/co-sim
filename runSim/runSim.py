import os
import numpy as np
from fmpy import extract
from pyfmi import Master, exceptions
import re
import shutil
from eppy import modeleditor
from eppy.modeleditor import IDF

def is_number(value):
    if is_float(value) or value.isnumeric():
        return True
    else:
        return False


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

    
def get_start_time():
    start_time = input("Input start time: ")
    while not start_time.isnumeric():
        print("Please input a number.")
        start_time = input("Input finale_time: ")

    try:
        start_time = int(start_time)
    except ValueError:
        return -1
    
    return start_time

def get_final_time():
    final_time = input("Input finale_time: ")
    while not final_time.isnumeric():
        print("Please input a number.")
        final_time = input("Input finale_time: ")
    
    try:
        final_time = int(final_time)
    except ValueError:
        return -1

    return final_time

def check_multiple(start_time, final_time, initialize=True):
    div_time = 86400
    is_not_multiple = float(final_time)%div_time

    if is_not_multiple != 0:
        print("Warning: EnergyPlus requires delta between start and stop time to be a multiple of 86400.")
        proceed = input("Proceed anyways? [y/n] : ")
        while proceed.lower() not in ['y', 'n']:
            proceed = input("Please input [y/n]: ")

        if proceed.lower() == "n":
            if initialize:
                start_time = get_start_time()
            final_time = get_final_time()
            start_time, final_time = check_multiple(start_time, final_time)
        else:
            return start_time, final_time
    
    return start_time, final_time

def get_master_step_size(fmu_objects):
    # fmu_files is formated like such: [("idf", fmu_model, file_path), ("mo", fmu_model), ("sim", fmu_model) ...]

    size = None
    seconds_in_hour = 60 * 60


    for fmu_obj in fmu_objects:
        new_size = -1
        fmu_path = fmu_obj.fmu_path
        loaded_fmu = fmu_obj.loaded_fmu

        # if fmu_object can handle variable step_size, skip fmu
        canHandle = False
        if "canHandleVariableCommunicationStepSize" in loaded_fmu.get_capability_flags():
            canHandle = loaded_fmu.get_capability_flags()["canHandleVariableCommunicationStepSize"]
        if canHandle:
            continue

        # if fmu is EnergyPlus model, parse through idf file to fine TimeStep and calculate step_size
        if "idf" in loaded_fmu.get_generation_tool() or "energyplus" in loaded_fmu.get_generation_tool():
            unzipdir = extract(fmu_path)
            path = unzipdir + "\\resources\\"
            for file in os.listdir(path):
                if file.endswith(".idf"):
                    path = os.path.join(path, file)
                # if file.endswith(".idd"):                             used for finding step size with idf modeleditor
                    # iddfile = os.path.join(path, file)

            try:
                idf_steps_per_hour = get_step_size_parse(path) 
                # idf_steps_per_hour = get_step_size(path, iddfile)     used for finding step size with idf modeleditor
                new_size = float(seconds_in_hour/idf_steps_per_hour)
            except FileNotFoundError as e:
                print(e)
                return -1
            
            shutil.rmtree(unzipdir)                                     # close the copied zip file

            # if TimeStep is not a component of EnergyPlus, input it manually
            if new_size < 0:
                fmu_name = os.path.splitext(os.path.basename(fmu_path))[0]
                while (1):
                    new_size = input(f"Step_size couldn't be found for FMU '{fmu_name}'. Please input manually: ")
                    try:
                        new_size = float(new_size)
                        break
                    except ValueError:
                        print("That is not a number...")
                        continue
        else:
            new_size = loaded_fmu.get_default_experiment_step()

        if size is None:
            size = new_size
        elif size != new_size:      
            # if sizes aren't equal, master.simulate will not initialize
            print("The stepSizes of models aren't equal and models can't handle variable stepSizes. Cannot run simulation.")
            return -1

    # if all models can handle variable step size
    if size is None:
        while(1):
            new_size = input("All models can handle variable stepSizes, please input prefered stepSize: ")
            try:
                new_size = float(new_size)
                break
            except ValueError:
                print("That is not a number...")
                continue
        size = new_size 

    return size

def get_step_size_parse(path):
    with open(path, "r") as file:
        for line in file:
            if re.search("Timestep,", line):
                next_line = file.readline()
                new_size = next_line.split(";")[0]
                try:
                    new_size = float(new_size)
                    return new_size
                except ValueError:
                    return -1
                
def get_step_size(path, iddfile):
    try:
        IDF.setiddname(iddfile)
    except modeleditor.IDDAlreadySetError:
        pass                                                        # xael, maybe change this to smth else? print + return -1

    fname1 = path
    idf1 = IDF(fname1)

    try:
        steptime = idf1.idfobjects["Timestep"][0].Number_of_Timesteps_per_Hour
        return steptime
    except exceptions:
        return -1

def find_shortest_column(*args):
    """
    Finds the shortest column in the given arrays.
    """
    min_length = min(len(arg) for arg in args)
    return [arg[:min_length] for arg in args]


def concat_columns(array):
    """
    Concatenates the given arrays into a single array.
    """

    for i in range(len(array)):
        if array[i].ndim < 2:
            array[i] = np.reshape(array[i], (-1, 1))

    return np.concatenate((array), axis=1)

def shorten_df(dfs):
    """
    Finds the shortest column in the given arrays.
    """

    min_length = min(len(df) for df in dfs)
    return [df.truncate(before=0, after=min_length-1) for df in dfs]

# we merge again because initial fmu_files is creating NOT for master
# but for each fmu object, so we need to merge them all together
def merge_columns(dfs, column_name):
    """
    merges column of the given dataframes on column with column_name
    """
    if len(dfs) != 0:
        master_df = dfs[0]
        for df in dfs:
            if df.equals(dfs[0]):
                master_df.merge(df, how='outer', on=column_name)
        
        master_df.ffill(inplace=True)              # ask amanda if she'd like 0s or forward fill...
        return master_df
    else:
        return None

def create_master_input(fmu_objects):
    master_header = []
    data_dfs_array = []

    for fmu_obj in fmu_objects:
        input_obj = fmu_obj.csv_to_input_object(master = True)
        if len(input_obj[0]) != 0 and input_obj[1] is not None:
            master_header = master_header + input_obj[0]
            data_dfs_array.append(input_obj[1])

    # shortened_df = shorten_df(data_dfs_array)                     do we want to shorten? otherwise the same data just gets repeated over and over
    master_df = merge_columns(data_dfs_array, 'time')

    if len(master_header) == 0 and master_df is None:
        return None
    
    master_data = master_df.values
    
    return (master_header, master_data)
     
def get_additional_options(options):
    print("Input additional options, type 'list options' to see the full list of options, type 'done' if done inputting additional options.")
    while (1) :
        newOption = input("Input additional options: ")
        newOption = newOption.strip().lower()
        if newOption == "list options":
            print("List of all additional options:")
            for optionName in options:
                print(f"{optionName} : {options[optionName]}")
        elif newOption == "done":
            break
        else:
            if newOption in options:
                optionValue = input(f"Please input option {newOption} value: ")
                if is_number(optionValue):
                    # check if inputed value type is mismatched with options' type
                    if isinstance(options[newOption], int):
                        options[newOption] = int(optionValue)
                    elif isinstance(options[newOption], float):
                        options[newOption] = float(optionValue)
                    elif isinstance(options[newOption], complex):
                        options[newOption] = complex(optionValue)
                    else:
                        print("Option type mismatch, please try again.")
                        continue
                elif optionValue.strip().lower() == "true":
                    if isinstance(options[newOption], bool):
                        options[newOption] = True
                    else: 
                        print("Option type mismatch, please try again.")
                        continue
                elif optionValue.strip().lower() == "false":
                    if isinstance(options[newOption], bool):
                        options[newOption] = False
                    else: 
                        print("Option type mismatch, please try again.")
                        continue
                else:
                    # checking if the option holds a string (i'm unsure how to touch the ones that are uh... dictionaries <- would need a parser)
                    if isinstance(options[newOption], type(optionValue)):
                        options[newOption] = optionValue
                    else:
                        print("Option type mismatch, please try again.")
                        continue
            else:
                print("user inputed option is NOT a real option, please try again")
                continue
        

def main(result_dir, fmu_objects, connections, start_time = 0, final_time = 60, initialize = True):
    """
    This function runs the simulation.
    """
    hasEnergyPlus = False

    models = []                             # list of loaded fmu objects/models

    for fmu_obj in fmu_objects:
        models.append(fmu_obj.loaded_fmu)
        if "idf" in fmu_obj.loaded_fmu.get_generation_tool() or "energyplus" in fmu_obj.loaded_fmu.get_generation_tool():
            hasEnergyPlus = True

    try:
        master = Master(models, connections)
    except exceptions.InvalidFMUException as e:
        print(f"Initialization Error: {e}")
        return None

    if initialize:
        start_time = get_start_time()
    final_time = get_final_time()
    
    while (start_time > final_time) or start_time < 0 or final_time < 0:
        if (start_time > final_time):
            print("Start time cannot be smaller than final time.")
        if (start_time < 0):
            print("Start time cannot be lower than 0.")
        if (final_time < 0):
            print("Final time cannot be lower than 0.")
        print("")
        if initialize:
            start_time = get_start_time()
        final_time = get_final_time()

    if hasEnergyPlus:
        start_time, final_time = check_multiple(start_time, final_time, initialize=initialize)

    step_size = get_master_step_size(fmu_objects)
    if step_size == -1:
        return -1

    input_object = create_master_input(fmu_objects)
    
    options = master.simulate_options()
    get_additional_options(options)

    # Necessary options:
    options["initialize"] = initialize
    options["result_handling"] = "csv"

    res = {}
    
    for fmu_obj in fmu_objects:
        name = fmu_obj.name
        result_csv_path = result_dir + "\\" + name + "_result.csv"
        res[name] = result_csv_path
        options["result_file_name"][fmu_obj.loaded_fmu] = result_csv_path
    # ncp = int((final_time - start_time)/(step_size))
    options['step_size'] = step_size

    try: 
        master.simulate(start_time=start_time, final_time=final_time, options = options, input= input_object)
        return res
    except exceptions.FMUException as e:     
        print(f"FMU Error: {e}")
        return e
    except Exception as e:
        print(f"Error: {e}")
        return e

