import os
import pandas as pd
import matplotlib.pyplot as plt
from pyfmi import load_fmu, exceptions
from runSim.runSim import main as run_sim
from runSim.runSim import get_master_step_size

"""
Helper functions for anything related to linking
"""
# causality --
# The causality of the variables (Parameter==0, 
# Calculated Parameter==1, Input==2, Output==3, Local==4, 
# Independent==5, Unknown==6).
# Default: None (i.e all).
# fmi.FMI2_INPUT xael

# helper functions
def get_input_names(fmu):
    try:
        
        inputs = fmu.get_model_variables(causality=2)
        names = []

        for input_var in inputs:
            names.append(input_var)

        return names
    except AttributeError:
        return None

def get_output_names(fmu):
    try:
        outputs = fmu.get_model_variables(causality=3)

        names = []
        for output_var in outputs:
            names.append(output_var)

        return names
    
    except AttributeError:
        return None
    

def add_index_to_name(new_name, list):
    index = 0
    old_name = new_name
    while (new_name in list) :
        index += 1
        new_name = old_name + "_" + str(index)

    return new_name

# def delete_spaces_file_names(file_path):
#     base_name = os.path.splitext(os.path.basename(file_path))[0]
#     new_base_name = base_name.replace(" ", "_")
#     directory = os.path.dirname(file_path)
#     new_file_path = os.path.join(directory, new_base_name)

#     return new_file_path

"""
Class which holds the information for individual FMU object
"""
class FMUObject:
    name = ""

    fmu_path = ""

    loaded_fmu = None

    input_files = []

    # {"input_name": bool} will be set TRUE if
    # A. "input_name" is inside connections
    connection_bools = {}
    # B. "input_name" has an input_file column
    input_file_bools = {}

    suppressed_inputs = []

    def __init__(self, name, fmu_path):
        self.name = name
        self.fmu_path = fmu_path
        self.load_fmu()
        
        self.connection_bools = {}
        for input_name in get_input_names(self.loaded_fmu):
            self.connection_bools[input_name] = False

        self.input_file_bools = {}
        for input_name in get_input_names(self.loaded_fmu):
            self.input_file_bools[input_name] = False
    

    def load_fmu(self):  
        self.loaded_fmu = load_fmu(self.fmu_path, kind='CS', log_level=7)  # Load the FMU using pyfmi
        

    def change_name(self, new_name):
        self.name = new_name


    def get_input_names(self):
        return get_input_names(self.loaded_fmu)
    

    def get_output_names(self):
        return get_output_names(self.loaded_fmu)


    # appends data_path to input_files to later be turned into input_object when running simulation
    # deletes input_name from input_files if input_name is not an input name of the FMU
    # returns added header
    def add_data(self, data_path, df, header):
        self.input_files.append(data_path)
        for input_name in header:
            if input_name not in self.get_input_names():
                header.remove(input_name)  # remove input_name if it is not in the input names of the FMU
                df.drop(input_name, axis=1)
            else:
                self.input_file_bools[input_name] = True
        return header


    def remove_data(self, input_name):
        if input_name in self.get_input_names():
            for input_file in self.input_files:
                df = pd.read_csv(input_file)
                if input_name in list(df.columns):
                    df.drop(input_name, axis=1)
                    self.input_file_bools[input_name] = False
        else:
            return -1
    
    def add_connection(self, input_name):
        if input_name in self.connection_bools:
            self.connection_bools[input_name] = True
    

    def remove_connection(self, input_name):
        if input_name in self.connection_bools:
            self.connection_bools[input_name] = False


    def check_overlap(self, input_name):
        type = None
        overlap = False

        if input_name in self.get_input_names():
            if self.connection_bools[input_name]:
                type = "connection"
                overlap = True
            elif self.input_file_bools[input_name]:
                type = "data"
                overlap = True
        
        return type, overlap


    def suppress_input_warnings(self, input):
        if isinstance(input, list):
            self.suppressed_inputs.extend(input)
        else:
            self.suppressed_inputs.append(input)


    def suppress_all_warnings(self):
        self.suppressed_inputs = self.get_input_names()


    def unsuppress_input_warnings(self, input):
        if input in self.suppressed_inputs:
            self.suppressed_inputs.remove(input)


    def unsuppress_all_warnings(self):
        self.suppressed_inputs.clear()


    def list_inputs(self):
        inputs = self.get_input_names()

        if inputs is None:
            print("No inputs could be found or this fmu. FMU name may be incorrect.")
            return 0

        print(f"Inputs in {self.name}:")
        num = 0
        for name in inputs:
            print(f" {num} - {name}")
            num += 1

    def list_outputs(self):
        outputs = self.get_output_names()

        if outputs is None:
            print("No inputs could be found or this fmu. FMU name may be incorrect.")
            return 0

        print(f"Outputs in {self.name}:")
        num = 0
        for name in outputs:
            print(f" {num} - {name}")
            num += 1
    
    def list_suppressed(self):
        print(f"{self.name} - {self.suppressed_inputs}")

    def list_inputs_with_data(self):
        filtered_connection_bool = [key for key, value in self.connection_bools.items() if value is True]
        print(f"{self.name:<30} - {filtered_connection_bool}")


    def create_header_master(self, header):
        master_header = []
        for input_var in header:
            master_header.append((self.loaded_fmu, input_var))
        return master_header

    def create_data_df(self, dfs):
        merged_df = None
        if len(dfs):
            merged_df = dfs[0]
            for df in dfs:
                if not df.equals(dfs[0]):
                    merged_df.merge(df, how='outer', on='time')
            merged_df.ffill(inplace=True)

        return merged_df

    def csv_to_input_object(self, master = False):
        """
        Function to add data to input
        """
        # returned input_object is = [header, df]
        tot_header = []
        input_data_dfs = []

        for data_path in self.input_files:
            base_type = os.path.splitext(data_path)[1]  # Get the file extension

            if base_type != ".csv":
                print(f"Error: The file {data_path} is not in form csv. Currently only csvs are correctly loaded.") 
                return 0   
            
            load = pd.read_csv(data_path)
            header = list(load.columns)
            header.remove('time')

            tot_header = tot_header + header
            input_data_dfs.append(load)
        
        merged_df = self.create_data_df(input_data_dfs)

        if master:
            tot_header = self.create_header_master(tot_header)
        
        # if no input_object, return [[], None]
        return [tot_header, merged_df]


"""
Class which holds the information needed for pyFMI workspace information
"""
class FMUWorkspace:
    save_dir = os.getcwd()                  # string of save directory

    RESULT_LOG_dir = ".\\Result_and_Logs"   # folder for result and log for each run

    fmu_objects = {}                        # {"fmu_name" : FMUObject}

    connections = []                        # [(fmu_output_object, "out_name", fmu_input_object, "input_name"), ...]

    # master_input_object = (None, None)    # input_object is formated as such:
    #                                       # (header, total_data)
    #                                       # total_data = np.concatonate(data, axis = 1)

    results = {}                            # ["result_name" : {"FMU_name" : "result_file.csv", "FMU2_name" : "result_file2.csv"}]       result names correspond with key to get results inside FMUObject

    # final_time = 0

    # additional fields I'm not sure are needed (if they are useful for lab, then I will keep, otherwise move to sim)
    # start_time
    # stop_time
    # tolerance
    # step_size

    def __init__(self, fmu_paths = [], save_dir = ""):
        if save_dir != "":
            self.save_dir = save_dir
            self.RESULT_LOG_dir = save_dir + "\\Result_and_Logs"

        self.make_new_run_dir()
        
        if len(fmu_paths):
            for fmu_path in fmu_paths:
                ret = self.add_fmu(fmu_path)
                if not ret:
                    print(f"{fmu_path} skipped.")
            
    """
    Overall helper methods
    """
    def get_loaded_fmu(self, fmu_name = None):
        if fmu_name is not None:
            return self.fmu_objects[fmu_name].loaded_fmu
        
        # return list of all fmu_objects
        loaded_fmus = []
        for fmu_obj in self.fmu_objects.values():
            loaded_fmus.append(fmu_obj.loaded_fmu)

        return loaded_fmus
    
    def get_connection_bools(self, fmu_name):
        if fmu_name in self.fmu_objects:
            return self.fmu_objects[fmu_name].connection_bools
        else:
            return None
    
    def get_input_file_bools(self, fmu_name):
        if fmu_name in self.fmu_objects:
            return self.fmu_objects[fmu_name].input_file_bools
        else:
            return None
    
    def get_suppressed_inputs(self, fmu_name):
        if fmu_name in self.fmu_objects:
            return self.fmu_objects[fmu_name].suppressed_inputs
    
    def make_new_run_dir(self):
        os.chdir(self.save_dir)
        while ("Result_and_Logs" not in os.getcwd()):
            try:
                os.mkdir(self.RESULT_LOG_dir)
                os.chdir(self.RESULT_LOG_dir)
            except FileExistsError:
                subdirectories = [f.name for f in os.scandir(self.save_dir) if f.is_dir()]

                new_export_dir = add_index_to_name("Result_and_Logs", subdirectories)
                
                self.RESULT_LOG_dir = self.save_dir + "\\" + new_export_dir
    
    """
    All Running Simulation with pyFMI code.
    """

    # helper function for run_sim
    def reload(self):
        # checking if we want to restart .simulate (aka re-initialize) the FMUs
        self.make_new_run_dir()

        for fmu_name in self.fmu_objects:
            old_fmu = self.get_loaded_fmu(fmu_name)
            self.fmu_objects[fmu_name].load_fmu()
            new_fmu = self.get_loaded_fmu(fmu_name)

            for old_tuple in self.connections:                                      # resetting tuple in self.connections with reloaded EP model
                index = self.connections.index(old_tuple)
                output_fmu = old_tuple[0]
                input_fmu = old_tuple[2]

                new_tuple = old_tuple
                if output_fmu == old_fmu and input_fmu == old_fmu:
                    new_tuple = (new_fmu, old_tuple[1], new_fmu, old_tuple[3])
                elif output_fmu == old_fmu:
                    new_tuple = (new_fmu, old_tuple[1], old_tuple[2], old_tuple[3])
                elif input_fmu == old_fmu:
                    new_tuple = (old_tuple[0], old_tuple[1], new_fmu, old_tuple[3])
                self.connections[index] = new_tuple

    def run_checks(self):
        """
        Function to check if FMUs are ready to run.
        Returns True if FMUs are ready to run, False otherwise.
        """
        if len(self.fmu_objects) == 0:
            print("No FMUs imported. Please import at least 1 FMU before running the simulation.")
            return False

        missing_inputs = self.check_inputs_warning()
        if missing_inputs:
            print("")
            print("There are inputs missing either connection or data.")

        no_data = True

        for fmu_obj in self.fmu_objects.values():
            if len(fmu_obj.input_files):
                no_data = False
        
        if no_data:
            print("")
            print("Warning: no initial data. May cause errors to arise.")


        print("")
        print(f"Results will be saved in: '{self.RESULT_LOG_dir}'")
        print("")

        return True

    def run_sim(self, initialize = True):
        """
        Function to run FMUs in simulation mode.
        """
        print("")
        print("Running FMUs in simulation mode...")
        print("")

        if initialize: # xael
            res = run_sim(self.RESULT_LOG_dir, self.fmu_objects.values(), self.connections)                  # run_sim will either return pyFMI result object, or Exception object raised
        # else:
        #     res = run_sim(self.RESULT_LOG_dir, self.fmu_objects, self.connections, inputs, start_time=self.final_time, initialize=False)  # run_sim will either return pyFMI result object, or Exception object raised
        print("")
        
        if "Failed to setup the experiment" in str(res):
            print("This is a result of already running once and not reloading into new working directory... reloading models...")
            print("")
            self.reload()
            res = run_sim(self.RESULT_LOG_dir, self.fmu_objects.values(), self.connections) # run sim again with reloaded models

        print("Run finished...")
        print("")
            
        if res is Exception or res is exceptions.FMUException:
            print(f"Run ended with a raised exception: {res}")
            print("Check above to see if error spawned from where.")
            print("To see more information about what this error may mean, use command 'doc'")
            print("")
            return -1
        else:
            result_name = add_index_to_name(new_name="result", list=self.results.keys()) 
            self.results[result_name] = res

            print(f"Saved result as '{result_name}'. To view result use command 'view-res <result_name/result_index>' 'view-res <result_name/result_index> <variable_list>'")
            print("or 'graph-res <result_name/result_index> <x-axis_variable> <y-axis_variable>'")
            print("Rename the result with 'name-res <old_name> <new_name>'")
            return 1
    
    def run_lab(self):
        print("Connecting FMUs to LabView...")
        print("Not implemented yet.")
        return 1


    """
    Function related to altering/viewing results
    """
    def get_result(self, name_or_index):
        res = None

        if name_or_index is None:
            print("You must input either result name or index.")
        else:
            try: 
                index = int(name_or_index)
                list_ver = list(self.results.items())
                if index > len(list_ver) or index < 0:
                    res = list_ver[index]
            except ValueError:
                if name_or_index in self.results:
                    res = self.results[name_or_index]
        
        return res

    def rename_result(self, old_name, new_name):
        if old_name not in self.results:
            print(f"Result with name '{old_name}' does not exist in result list.")
            return 0
        
        if new_name in self.results:
            old_new_name = new_name
            new_name = add_index_to_name(new_name, self.results)
            print(f"Result name '{old_new_name}' already exists in result list. Changing new name to '{new_name}'")
        
        self.results[new_name] = self.results.pop(old_name)
        return 1
    
    def show_results(self, name_or_index, model_name = None, variables = None):
        # variables are formatted as ["variable_name", "variable_name2"...]
        # res is formatted as: {"model_name" : "result_file.csv", "model_name2" : "result_file2.csv"}
        res = self.get_result(name_or_index)
        if res is None:
            print(f"'{name_or_index}' does not exist in results.")
            return None
        elif isinstance(res, Exception):
            error_str = str(res)
            print(error_str)
            return None
        elif isinstance(res, exceptions.FMUException):
            error_str = str(res)
            print(error_str)
            return None
        
        print("Model:")
        if model_name is not None and variables is not None:
            print(f"{model_name}")
            print("")
            try:
                df = pd.read_csv(res[model_name], usecols=variables)
                print("Variables:")
                print(f"{df}")
                print("")
            except FileNotFoundError as e:
                print(e)
                print(f"{model_name} doesn't exist, please input an FMU that was inside this result")
                return -1
            except KeyError as e:
                print(e)
                print(f"{variables} aren't outputs inside FMU, {model_name}.")
                return -1
        else:
            for model_name in res:
                print(f"{model_name}: ")
                pd.options.display.max_rows = 20  #xael option to change this later
                df = pd.read_csv(res[model_name])
                print(df)
                input("Press any button to continue to next model... ")
        return 1
    
    def graph_results(self, name_or_index, x_axis_fmu, x_axis_var, y_axis_fmu_names, y_axis_vars, together = False):
        # res is formatted as: {"model_name" : "file_name.csv", "model_name2" : "file_name2.csv"}
        res = self.get_result(name_or_index)
        if res is None:
            return 0
        elif res is Exception:
            error_str = str(res)
            print(error_str)
            return -1
        
        if x_axis_fmu in res:
            try:
                df_x = pd.read_csv(res[x_axis_fmu], usecols=[x_axis_var])
                x_axis = df_x[x_axis_var].to_list()
            except FileNotFoundError as e:
                print(e)
                print(f"Result file cannot be found. Either'{x_axis_fmu}' FMU isn't inside this result, or result file got moved.")
                return -1
            except KeyError as e:
                print(e)
                print(f"'{x_axis_var}' isn't an output for FMU, '{x_axis_fmu}'.")
                return -1
        else:
            print(f"'{x_axis_fmu}' FMU doesn't exist, please input an FMU that was inside this result.")
            return -1

        y_axis = []
        zipped_y_mod_var = zip(y_axis_fmu_names, y_axis_vars)
        for fmu_name, var in zipped_y_mod_var:
            if fmu_name in res:
                try:
                    df_y = pd.read_csv(res[fmu_name], usecols=[var])
                    y_axis.append(df_y[var].to_list())
                except FileNotFoundError as e:
                    print(e)
                    print(f"Result file cannot be found. Either'{fmu_name}' FMU isn't inside this result, or result file got moved.")
                    return -1
                except KeyError as e:
                    print(e)
                    print(f"'{var}' isn't an output for FMU, '{fmu_name}'.")
                    return -1
            else:
                print(f"'{fmu_name}' FMU doesn't exist, please input an FMU that was inside this result.")
                return -1

        if together:
            plt.figure()
            plt.xlabel(x_axis_var)

        for i in range(len(y_axis)):
            if not together:
                plt.figure()
                plt.xlabel(x_axis_var)
            plt.plot(x_axis, y_axis[i], label=f"{y_axis_vars[i]}")
        
        plt.legend(loc='best')
        
        save_confirm = input("Save plot as png? [y/n] ")
        while (1):
            if save_confirm.lower() not in ['y', 'n']:
                save_confirm = input("Invalid input. Please enter 'y' or 'n': ")
            else:
                break
        
        if save_confirm.lower() == 'y':
            name = input("Input name you would like png to be saved as: ")
            plt.savefig(f"{name}.png", bbox_inches='tight')
        else:
            print("Just showing plot, not saving...")

        print("")
        print("The program will pause until you close the plot...")
        plt.show()
        plt.close()

        # fig, ax1 = plt.subplots()
        # ax1.plot(res[x_axis_var], res[y_axis_vars[0]], 'b-')
        # ax1.set_xlabel(x_axis_var)
        # ax1.set_ylabel(y_axis_vars[0], color='b')
        # ax1.tick_params('y', colors='b')

        # ax2 = ax1.twinx()
        # ax2.plot(res[x_axis_var], res[y_axis_vars[1]], 'r.')
        # ax2.set_ylabel(y_axis_vars[1], color='r')
        # ax2.tick_params('y', colors='r')
        # fig.tight_layout()
        # plt.show()
        
        return 1
    

    """
    Functions to add/change/delete fmus
    """
    def export_fmu(self, fmu):
        """
        Placeholder function to export an FMU from a program.
        In a real implementation, this would contain the logic to export the FMU.
        """
        # For now, we will just return the original path
        return None

    def set_name(self, old_name, new_name):
        """
        Function to set a new name for an FMU in the fmuFiles dictionary.
        """
        if old_name in self.fmu_objects:
            if new_name in self.fmu_objects:
                old_new_name = new_name
                new_name = add_index_to_name(new_name, self.fmu_objects.keys())
                print(f"Warning: {old_new_name} already exists, changing name to {new_name}")
            self.fmu_objects[old_name].change_name(new_name)
            self.fmu_objects[new_name] = self.fmu_objects.pop(old_name)
            return 1
        else:
            print(f"Error: {old_name} does not exist")
            return 0
        
    def change_dir(self, new_dir):
        """
        Function to change the save directory
        """
        if (not os.path.isdir(new_dir)):                            
            print(f"Error: The directory {new_dir} does not exist.")
            return 0
        elif new_dir == self.save_dir:
            print(f"No change, save directory is already {new_dir}")
            return 0
        else:
            self.save_dir = new_dir
            return 1

    def add_fmu(self, fmu_path, fmu_name = None):
        """
        Function to add an FMU to the fmuFiles dictionary.
        """
        if fmu_name is None:
            fmu_name = os.path.splitext(os.path.basename(fmu_path))[0]  # Get the base name of the FMU file
        
        if not os.path.isfile(fmu_path): 
            print(f"Error: The file {fmu_path} does not exist.")
            return 0
        
        base_type = os.path.splitext(fmu_path)[1]  # Get the file extension
    
        if base_type != ".fmu":
            fmu_path = self.export_fmu(fmu_path)
            if (fmu_path is None):
                print(f"Error: The file {fmu_path} could not be exported as an FMU. Skipping file")
                return 0
        
        if fmu_name in self.fmu_objects:
            new_name = add_index_to_name(fmu_name, self.fmu_objects.keys())
            print(f"Warning: you're inputting a repeat file. Setting as new name: '{new_name}'")
        
        try:
            self.fmu_objects[fmu_name] = FMUObject(fmu_name, fmu_path)
            print(f"Adding FMU to the list of FMUs: '{fmu_name}'")
            return 1
        except exceptions:
            print(f"Error: Could not load FMU from {fmu_path}.")
            return -1

        
    def delete_fmu(self, fmu_name):
        """
        Function to delete an FMU from the fmuFiles dictionary and clears links to it.
        """
        if fmu_name in self.fmu_objects:
            self.unlink_input_output(fmu_name)
            print(f"Connections related to FMU {fmu_name} have been removed.")

            del self.fmu_objects[fmu_name]
            print(f"FMU {fmu_name} deleted.")
            return 1
        else:
            print(f"FMU with name {fmu_name} does not exist.")
            return 0

    def reset(self):
        """
        Resets the simulation, deletes all FMUs.
        """
        self.make_new_run_dir()
        # for fmu_obj in self.fmu_objects.values():     keeping because smth smth master is malloc'd xael
        #     del fmu_obj
        self.fmu_objects.clear()  # Reset the fmuFiles dictionary
        self.connections.clear()  # Reset the connections list
        print("FMU files reset.")

    """
    Functions to check overlap when adding connections/data files
    """
    def check_overlap(self, fmu_name, input_names):
        # list of inputs that will NOT override previous connection/data file inputs
        overlap_remove = []
        for input_name in input_names:
            type, overlap = self.fmu_objects[fmu_name].check_overlap(input_name)
            if overlap:
                if type == "connection":
                    confirmation = input(f"Warning: Previous link/connection already has '{input_name}'. Override previous connection/link? [Y/y] ")
                    if confirmation.lower() == 'y':
                        print("Confirmed, overriding previous connection...")
                    else:
                        print(f"Canceling connection for input: {input_name}...")
                elif type == "data":
                    confirmation = input(f"Warning: Previous data file has '{input_name}' as a column. Override previous input file inputs? [Y/y] ")
                    if confirmation.lower() == 'y':
                        print("Confirmed, overriding previous input data file...")
                        self.remove_data(fmu_name, input_name)
                        print("Removed previous input data.")
                    else:
                        print(f"Canceling data column: {input_name}...") 
                        overlap_remove.append(input_name)
        
        return overlap_remove
            

    """
    Functions to add/remove data files/points for model inputs. 
    """
    def add_data(self, fmu_name, data_path):
        if fmu_name not in self.fmu_objects:
            print("FMU does not exist/is not loaded.")
            return 0

        if isinstance(data_path, str):
            df = pd.read_csv(data_path)
            header = list(df.columns)
            if 'time' in header:
                header.remove('time')
                overlap_remove = self.check_overlap(fmu_name, header)  # check if any of the inputs overlap with previous connections/data files

                for input_name in overlap_remove:
                    header.remove(input_name)

                self.fmu_objects[fmu_name].add_data(data_path, df, header)
                print(f"Added data file '{data_path}' to FMU '{fmu_name}'.")
            else:
                print("'time' is a necessary column inside of your csv file. Please input it as a column.")

                
    def remove_data(self, fmu_name, input_name):
        if fmu_name not in self.fmu_objects:
            return 0

        if input_name in self.fmu_objects[fmu_name].get_input_names():
            self.fmu_objects[fmu_name].remove_data(input_name)
            return 1

        return 0
    
    """
    Functions to change linking (and it's errors/warnings) of inputs/outputs
    """
    def link_input_output(self, fmu_name_1, output_name, fmu_name_2, input_name):
        """
        function to link an input of one FMU to the output for another FMU.
        """
        print("Linking input and output for FMUs:")

        if fmu_name_1 not in self.fmu_objects or fmu_name_2 not in self.fmu_objects:
            print(f"Error: One or both FMUs '{fmu_name_1}' and '{fmu_name_2}' do not exist.")
            return 0

        fmu1 = self.get_loaded_fmu(fmu_name_1)
        fmu2 = self.get_loaded_fmu(fmu_name_2)

        fmu1_outputs = get_output_names(fmu1)
        fmu2_inputs = get_input_names(fmu2)

        if fmu1_outputs is None or fmu2_inputs is None:
            print("No inputs could be found or this fmu. FMU name may be incorrect.")
            return 0

        # Getting output_name from index
        if isinstance(output_name, int):
            try:
                output_name = fmu1_outputs[output_name]
            except IndexError:
                print(f"Error: {output_name} is out of bounds. Please input a index that exists")
                return 0
            
            # xael which is more efficient?
            # if output_name >= len(fmu1_outputs) or output_name < 0:
            #     print(f"Error: {output_name} is out of bounds. Please input a index that exists")
            #     return 0
            
            # output_name = fmu1_outputs[output_name]
        
        # Getting input_name from index
        if isinstance(input_name, int):
            try:
                input_name = fmu2_inputs[input_name]
            except IndexError:
                print(f"Error: {input_name} is out of bounds. Please input a index that exists")
                return 0
            
        if output_name not in fmu1_outputs or input_name not in fmu2_inputs:
            if output_name not in fmu1_outputs:
                print(f"Error: Output '{output_name}' does not exist in {fmu_name_1}")
                print(f"Available outputs for {fmu_name_1}")
                self.list_outputs(fmu_name_1)
            if input_name not in fmu2_inputs:
                print(f"Error: Input '{input_name}' does not exist in {fmu_name_2}.")
                print(f"Available inputs for {fmu_name_2}:")
                self.list_inputs(fmu_name_2)
            return 0

        # Check if this input already had previous connection/data input file
        do_not_override = self.check_overlap(fmu_name_2, [input_name])

        if input_name in do_not_override:
            return 0 # if input_name is in do_not_override, then it means that the user chose not to override the previous connection/data file
        
        # Link the input and output
        self.connections.append((fmu1, output_name, fmu2, input_name))
        self.fmu_objects[fmu_name_2].add_connection(input_name)

        print(f"Linked output '{output_name}' of FMU '{fmu_name_1}' to input '{input_name}' of FMU '{fmu_name_2}'.")
        return 1


    # 6 ways to unlink:
    # 1. fmu_name                                       unlinks all connections to fmu_name
    # 2. fmu_name output_name == "All"                  unlinks all connections with fmu_name's outputs
    # 3. fmu_name output_name                           unlinks all connections with fmu_name's output_name
    # 4. fmu_name input_name  == "All"                  unlinks all connections with fmu_name's inputs
    # 5. fmu_name input_name                            unlinks all connections with fmu_name's input_name
    # 6. fmu_name_1 output_name fmu_name_2 input_name   unlinks specific connection (fmu_1, output, fmu_2, input)
    def unlink_input_output(self, fmu_name_1, output_name = None, fmu_name_2 = None, input_name = None):
        """
        function to unlink an input and output for an FMU.
        """
        if fmu_name_1 not in self.fmu_objects:
            print(f"Error: FMU '{fmu_name_1}' do not exist.")
            return 0
        
        fmu1 = self.get_loaded_fmu(fmu_name_1)

        if fmu_name_2 is None:
            if output_name is None and input_name is None:
                remove_both = input(f"Confirm you want to unlink all inputs and outputs of {fmu_name_1}? [y]: ")
                if remove_both == 'y':
                    output_name = "All"
                    input_name = "All"
                else:
                    print("Stopping unlinking proceedure...")
                    return 0
            
            for tuple in self.connections:
                if (tuple[0] == fmu1):
                    if (tuple[1] == output_name or output_name == "All"):
                        self.connections.remove(tuple)
                if (tuple[2] == fmu1):
                    if (tuple[3] == input_name or input_name == "All"):
                        self.connections.remove(tuple)
                self.fmu_objects[tuple[2]].remove_connection(tuple[3])
        elif fmu_name_2 not in self.fmu_objects:
            print(f"Error: FMU '{fmu_name_2}' do not exist.")
            return 0
        else:
            # no check for input_name = None and output_name = None, because run.py will not send with fmu_name_2 without input/output names
            fmu2 = self.get_loaded_fmu(fmu_name_2)

            for tuple in self.connections:
                if (tuple[0] == fmu1 and tuple[1] == output_name and tuple[2] == fmu2 and tuple[3] == input_name):
                    self.connections.remove(tuple)

            self.fmu_objects[fmu_name_2].remove_connection(input_name)

            print("New connections: ")
            self.list_links()

            return 1


    def check_inputs_warning(self):
        missing_connection = False

        for fmu_name in self.fmu_objects.keys():
            connection_bools = self.get_connection_bools(fmu_name)
            input_file_bools = self.get_input_file_bools(fmu_name)
            suppressed_inputs = self.get_suppressed_inputs(fmu_name)
            
            for input_name in connection_bools:
                # if input_name has no input at all (connection/input file), and is not suppressed
                if not connection_bools[input_name] and not input_file_bools[input_name] and input_name not in suppressed_inputs:
                    print(f"Warning: input variable {input_name} from {fmu_name} does not have data input or connection to another model")
                    missing_connection = True

        return missing_connection


    def suppress_input(self, fmu_name, input_name = None):
        """
        Adds input variable into suppressed_input_warnings list, if no input_name is specified suppresses all inputs for fmu
        """
        if fmu_name not in self.fmu_objects:
            print(f"'{fmu_name}' is not added or does not exist.")
            return 0
        
        fmu_obj = self.fmu_objects[fmu_name]

        if input_name is None:
            print(f"Suppressing all warnings for inputs in {fmu_name}")
            print("Inputs will no longer show warnings if no input or link is given.")
            fmu_obj.suppress_all_warnings()
        else:
            inputs = fmu_obj.get_input_names()
            if input_name not in inputs:
                print(f"{input_name} is not in fmu {fmu_name}")
                return 0
            
            print(f"Suppressing warning for input {input_name} for {fmu_name}.")
            print(f"{input_name} will no longer show warnings if no input or link is given.")

            fmu_obj.suppress_input_warnings(input_name)

        print("Simulation will run even if no input is present.")
        print("")
        print("To unsuppress, use command 'unsuppress <fmu_name> <input_name>' or 'unsuppress <fmu_name>' to unsuppress all inputs.")
        return 1

    def unsuppress_input(self, fmu_name, input_name = None):
        """
        Function to unsuppress inputs. If no input_name is given, unsuppresses all inputs for fmu
        """
        if fmu_name not in self.fmu_objects:
            print(f"{fmu_name} does not exist.")
            return 0

        fmu_obj = self.fmu_objects[fmu_name]
        
        if input_name is None:
            print(f"Unsuppressing warnings for all inputs of {fmu_name}")
            fmu_obj.unsuppress_all_warnings(input_name)
        else:
            print(f"Unsuppressing warnings for {input_name} from fmu {fmu_name}")
            self.unsuppress_input_warnings(input_name)
        return 1
    
    """
    All printing (called listing here) functions 
    """
    def list_fmus(self):
        """
        Function to list all FMUs in the fmuFiles dictionary.
        """
        if not self.fmu_objects:
            print("No FMUs imported.")
        else:
            print("Current FMUs:")
            for name in self.fmu_objects:
                print(f" - {name}")


    def list_inputs(self, fmu_name):
        """
        Function to list (print) all inputs for an FMU.
        """
        if fmu_name not in self.fmu_objects:
            print(f"Error: '{fmu_name}' do not exist.")
            return 0
        
        self.fmu_objects[fmu_name].list_inputs()
        
        return 1


    def list_outputs(self, fmu_name):
        """
        Function to list all inputs for an FMU.
        """
        if fmu_name not in self.fmu_objects:
            print(f"Error: '{fmu_name}' do not exist.")
            return 0
        
        self.fmu_objects[fmu_name].list_outputs()
        
        return 1


    def list_links(self):
        """
        Function that prints all connection/links
        """
        # invert dictionary {fmu_object: fmu_name}
        inverted_dict = {v.loaded_fmu: k for k, v in self.fmu_objects.items()}
        print("Output:                                         Input:")
        for tuple in self.connections:
            input_file_name = inverted_dict.get(tuple[0])
            output_file_name = inverted_dict.get(tuple[2])
            print(f"({input_file_name}) {tuple[1]:<30}({output_file_name}) {tuple[3]}")


    def list_link_for_fmu(self, fmu_name):
        """
        Function that prints links with only fmu_name as one of the fmus
        """
        if fmu_name not in self.fmu_objects:
            print(f"Error: '{fmu_name}' do not exist.")
            return 0
        
        fmu_obj = self.fmu_objects[fmu_name].loaded_fmu

        # invert dictionary {fmu_object: fmu_name}
        inverted_dict = {v.loaded_fmu: k for k, v in self.fmu_objects.items()}

        print("Output:                                         Input:")
        for tuple in self.connections:
            if tuple[0] == fmu_obj or tuple[2] == fmu_obj:
                input_file_name = inverted_dict.get(tuple[0])
                output_file_name = inverted_dict.get(tuple[2])
                print(f"({input_file_name}) {tuple[1]:<30}({output_file_name}) {tuple[3]}")
        return


    def list_suppressed(self):
        print("Suppressed inputs:")
        for fmu_obj in self.fmu_objects.values():
            fmu_obj.list_suppressed()
        print("")
        print("To unsupress, use command 'unsuppress <fmu_name> <input_name>'")
    

    def list_data_input_vars(self):
        print("Inputs with data (not links/connections) being inputted:")
        print("FMU name:                                       Input name:")
        for fmu_obj in self.fmu_objects.values():
            fmu_obj.list_inputs_with_data()
        print("")
        print("To remove data, use command 'remove-data <fmu_name> <input_name>' ")


    def list_results(self):
        print("Current list of results:")
        for res_name in self.results:
            print(f"Result Name: '{res_name:<30}'")
            for model in self.results[res_name]:
                print(f"Result file location for FMU '{model}': {self.results[res_name][model]}")
                print(f"Output Variable Names in FMU '{model}':")
                try:
                    load = pd.read_csv(self.results[res_name][model])
                    print(load.columns)
                except FileNotFoundError as e:
                    print(e)

    
    def format_export_workspace(self, workspace_name):
        workspace_json = {
            "name" : workspace_name,
            "step_size" : get_master_step_size(self.fmu_objects.values())
        }

        fmu_jsons, fmu_files = self.format_export_fmus()
        connection_jsons = self.format_export_connection()

        return workspace_json, fmu_jsons, fmu_files, connection_jsons

    def format_export_fmus(self):
        fmu_jsons = []
        fmu_files = []
        for fmu_name, fmu_object in self.fmu_objects.items():
            fmu_jsons.append({"fmu_name":fmu_name})
            # not formatting this as it needs to be open(...) when sending over response
            fmu_files.append(("files", (fmu_name, open(fmu_object.fmu_path, "rb"))))
        return fmu_jsons, fmu_files


    def format_export_connection(self):
        connection_jsons = []
        for tuple in self.connections:
            output_fmu = tuple[0]
            output_name = tuple[1]
            input_fmu = tuple[2]
            input_name = tuple[3]

            output_fmu_name = [k for k, v in self.fmu_objects.items() if v.loaded_fmu == output_fmu][0]
            input_fmu_name = [k for k, v in self.fmu_objects.items() if v.loaded_fmu == input_fmu][0]

            connection_jsons.append({"output_model" : output_fmu_name, "output_var_name" : output_name, "input_model":input_fmu_name, "input_var_name":input_name})
        return connection_jsons
    
            
    
    