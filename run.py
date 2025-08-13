import os
import sys
import fmu_files
import API_code

def login_or_reg():
    if not session.logged_in:
        print("No session currently active.")
        login_or_register = input("Would you like to login or register? [login/register] ")
        while login_or_register.lower() not in ['login', 'register']:
            print("canceling...")
            return 0

        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if login_or_register.lower() == 'register':
            status, text = session.register(username, password)
            if status != 200:
                print(f"Registration failed with {status} - {text}. Please try again.")
                return 0

        # login after registering    
        status, text  = session.login(username, password)
        if status != 200:
            print(f"Login failed with {status} - {text}. Please try again.")
            return 0
        print(text)
        return 1

if __name__ == "__main__":

    print("")
    print("=============================================")
    print("")
    print("          running co-sim environment         ")
    print("")
    print("=============================================")
    print("")

    echo = False
    save_dir = ""
    fmu_paths = []

    if sys.argv[len(sys.argv) - 1] == "echo":
        echo = True
        sys.argv.pop()  # Remove the last argument if it's 'echo'

    # Checking or additional arguments
    if len(sys.argv) == 1:
        print("Save Directory is defaulted to current directory.")
        print("To change save directory, type 'save-directory <path>'")
        print("")
        print("No FMUs were added.")
        print("To add FMUs type:") 
        print("add-FMU <filePath>")
        print("or")
        print("add-FMU <fmu_path> <fmu_name>")
        print("")
    elif len(sys.argv) == 2:
        print("")
        print("No FMUs were added.")
        print("To add FMUs type:") 
        print("add-FMU <filePath>")
        print("or")
        print("add-FMU <fmu_name> <fmu_path>")
        print("")

        save_dir = sys.argv[1]
        # Check if the save directory exists
        if (not os.path.isdir(save_dir)):                            
            print(f"Error: The directory {save_dir} does not exist.")
            sys.exit(1)
    elif len(sys.argv) > 2:

        check_save_dir = sys.argv[1]

        if os.path.isfile(check_save_dir):
            temp_fmu_paths = sys.argv[1:]
        elif os.path.isdir(check_save_dir):
            save_dir = check_save_dir
            temp_fmu_paths = sys.argv[2:]
        else:
            print(f"Error: {check_save_dir} is not a directory or fmu file.")
            sys.exit(1)

        for fmu_path in temp_fmu_paths:
            # Check if the file exists
            if not os.path.isfile(fmu_path):
                print(f"Error: The file {fmu_path} does not exist.")
                sys.exit(1)
        
        fmu_paths = temp_fmu_paths

        if echo:
            print(f"Save Dir: {save_dir}")
            print(f"FMU Paths: {fmu_paths}")

    fmu = fmu_files.FMUWorkspace(fmu_paths, save_dir)
    session = API_code.APISession()

    """
    This is the main program loop, which checks for user inputs and executes commands based on those inputs.
    It provides a command-line interface for cosimulating FMUs with different programs.
    To exit, type 'exit' or 'quit'.
    """
    print("")
    print("Type 'help' for more information")
    print("")

    while (1) :
        retString = input("[cosim_fmu]: ")
        if (retString == "" or retString == " "):
            continue

        ret = retString.split()[0].strip().lower()  # Get the first word of the input command
        
        if (ret == "help"):
            print("This is a program to cosimulate FMUs with different programs.")
            print("You can export an FMU from a program if FMU is not already exported.")
            print("You can also run the FMU in real-time with a specific model and a specific database.")
            print(f"All result FMUs will be saved in the directory {save_dir}.")

            print("Correct usage of program:")
            print("python run.py                                   -                                run with default current directory as save directory")
            print("python run.py <save_dir>                        -                                run with specified save directory ")
            print("python run.py <save_dir> <FMU1> <FMU2> ...      -                                run with specified save directory and fmus")
            print("")
            print("add echo option at the end to echo commands")
            print("")
            print("Examples: ")
            print("python run.py /path/to/save_dir")
            print("python run.py /path/to/save_dir /path/to/FMU1.fmu /path/to/FMU2.fmu echo")

            break_point = input("Press any key to continue. Enter 'done' to quit the help menu. ")
            print("")
            print("")
            if break_point == "done":
                continue

            print("")
            print("Available commands:")
            print("")
            print("Commands for running and viewing results: ")
            print("run :                                                                                                            run simulation or real-time FMUs")
            print("name-res <old_name> <new_name> :                                                                      rename a result from the default 'result_#'")
            print("view-res <result_name/result_index> :                                                  view result via result_name or index, array of all outputs")
            print("view-res <result_name/result_index> <FMU> <variables> :                  view result via result_name or index, array of specific output variables")
            print("graph-res <result_name/result_index> <x-axis_fmu> <x-axis_variable> <y-axis_fmu1> <y-axis_variable1> <y-axis_fmu2> <y-axis_variable2>... " \
            ":    graph result with x-axis result variable and y-axis result variable")
            print("doc :                                                                                                   doc about general errors and helpful tips")
            print("")
            print("")
            break_point = input("Press any key to continue. Enter 'done' to quit the help menu. ")
            print("")
            print("")
            if break_point == "done":
                continue
            print("Commands for setting up workspace:")
            print("")
            print("set-name <fmu_name> <new_name> :                                                                                        set a new name for an FMU")
            print("save-directory <dirPath> :                                                                                    set new save results directory path")
            print("current-setup :                                                                                               prints your current workspace setup")
            print("")
            # adding and deleting commands
            print("add-FMU <fmu_path> :                                                                                            add an FMU to current list of FMUs")
            print("add-FMU <fmu_path> <fmu_name> :                                                                add an FMU with a specific name to the list of FMUs")
            print("delete-FMU <fmu_name> :                                                                                        delete an FMU from the list of FMUs")
            print("reset :                                                                                                     reset the FMU files and save directory")
            print("")
            print("")
            break_point = input("Press any enter to continue. Enter 'done' to quit the help menu. ")
            print("")
            print("")
            if break_point == "done":
                continue
            # adding and deleting data
            print("Altering data commands:")
            print("add-data <fmu_name> <data_path> :                                                        add data to input rather than connection to another model")
            print("remove-data <fmu_name> <input_name> :                                                                                       remove data from input")      
            print("")
            print("")
            break_point = input("Press any enter to continue. Enter 'done' to quit the help menu. ")
            print("")
            print("")
            if break_point == "done":
                continue                                  
            # linking commands
            print("Linking commands:")
            print("link <fmu_name> <output_name> <fmu_name> <intputName> :                                                  link an input and output for variable name")
            print("link <fmu_name> <outputIndex> <fmu_name> <inputIndex> :                                                  link an output and input by variable index")
            print("")
            print("Unlinking commands:")
            print("unlink <fmu_name> :                                                                                       removes all connections/links to fmu_name")
            print("unlink <fmu_name> input==all :                                                                   removes all links where fmu_name is the input port")
            print("unlink <fmu_name> input==<input_name> :                                                         removes specific link with input_name from fmu_name")
            print("unlink <fmu_name> output==all :                                                                 removes all links where fmu_name is the output port")
            print("unlink <fmu_name> output==<output_name> :                                                  removes specific link where output_name is from fmu_name")
            print("unlink <input_fmu_name> <input_name> <output_fmu_name> <output_name> :                        unlink specific input_name and output_name connection")
            print("")
            print("")
            break_point = input("Press any enter to continue. Enter 'done' to quit the help menu. ")
            print("")
            print("")
            if break_point == "done":
                continue
            # suppression commands
            print("suppress <fmu_name> :                                                                              suppress warnings about all inputs from fmu_name")
            print("suppress <fmu_name> <input_name> :                                                        suppress warnings about specific input_name from fmu_name")
            print("unsuppress <fmu_name> :                                                                          unsuppress warnings about all inputs from fmu_name")
            print("unsuppress <fmu_name> <input_name>:                                                     unsuppress warnings about specific input_name from fmu_name")
            print("")
            # listing/printing commands
            print("list :                                                                                                                               list all FMUs")
            print("list-links :                                                                                                           list all links between FMUs")
            print("list-links <fmu_name> :                                                                                           list all links for a certain FMU")
            print("list-inputs <fmu_name> :                                                                                        list all inputs for a specific FMU")
            print("list-outputs <fmu_name> :                                                                                      list all outputs for a specific FMU")
            print("list-suppressed <fmu_name> :                                                                                            list all suppressed inputs")
            print("list-res :                                                                                              list all result names and result variables")
            print("")
            print("")
            break_point = input("Press any enter to continue. Enter 'done' to quit the help menu. ")
            print("")
            print("")
            if break_point == "done":
                continue
            # export + exit commands
            print("export <workspace_name> :                                                        Export current workspace to API with user chosen <workspace_name>")
            print("get-API-link")
            print("")
            print("To exit, type 'exit' or 'quit'.")
        elif (ret == "exit" or ret == "quit"):
            if (echo):
                print("exit")
            print("Exiting the program.")
            break
        elif (ret == "run"):
            if (echo):
                print("run")

            print("")
            print("Running FMUs with the following parameters:")
            fmu.list_fmus()
            print("Current connections/links:")
            fmu.list_links()
            ret = fmu.run_checks()
            if not ret:
                continue

            confirm = input("Confirm continue to run? [Y/y] ")
            if confirm.lower() != "y":
                print("Canceling...")
                continue
            
            simOrReal = input("Run with simulation or to lab [sim/lab]: ")
            while (simOrReal.lower() not in ["sim", "simulation", "lab", "real"]):
                simOrReal = input("Please input 'sim' 'simulate' 'real' or 'lab'")
            
            if simOrReal.lower() in ["sim", "simulation"]:
                ret = fmu.run_sim()
            elif simOrReal.lower() in ["lab", "real"]:
                ret = fmu.run_lab()
            
            if ret != 0:
                while (1):
                    reset_question = input("Would you like to reset your workspace, or keep current FMU/Links? Resetting will erase all current FMUs/links inside of session. [reset/keep] ")
                    if reset_question.lower() not in ['reset', 'keep']:
                        reset_question = input("Invalid input. Please enter 'reset' or 'keep': ")
                        continue
                    break

                if reset_question.lower() == "reset":
                    fmu.reset()

        elif (ret == "doc"):
            print("differentiating errors:")
            print("")
            print("EP errors:")
            print("If you see '**FATAL: ...' that is an energyplus error. Check the line with 'Error:' to see were the issue lies.")
            print("A few common ")
            print("")
            x = input("Press any key to continue. Type 'done' to end 'doc' screen")
            print("WIP not finished writing boo xael ")
        elif (ret == "view-res"):
            if echo:
                print("view-res")

            print("")
            if len(retString.split()) > 1:
                name_or_index = retString.split()[1]
                if len(retString.split()) > 2:
                    model_name = retString.split()[2]
                    var_array = retString.split()[3:]     # [fmu_name, var_name, fmu2_name, var2_name...]
                else:
                    model_name = None
                    var_array = None
                fmu.show_results(name_or_index, model_name, var_array)
            else:
                print("No RESULT name or index provided. Please include name or index in command. You can view RESULT names using command: 'list-res'")
        elif (ret == "graph-res"):
            if echo:
                print("graph-res")

            if len(retString.split()) > 3:
                name_or_index = retString.split()[1]
                x_axis_fmu = retString.split()[2]
                x_axis_var = retString.split()[3]
                end_str = retString.split()[4:]     # [fmu_name, var_name, fmu2_name, var2_name...]
                y_axis_fmus = end_str[::2]          # gets every odd element 
                y_axis_vars = end_str[1::2]         # gets every even element

                together = input("Have all y-axis on the same figure? [y/n] ")
                while (together.lower() not in ['y', 'n']):
                    together = input("Invalid input. Please enter 'y' or 'n': ")
                
                if together == 'y':
                    together = True
                else:
                    together = False

                fmu.graph_results(name_or_index=name_or_index, x_axis_fmu=x_axis_fmu, x_axis_var=x_axis_var, y_axis_fmu_names=y_axis_fmus, y_axis_vars=y_axis_vars, together=together)
            else:
                print("Not enough parameters. Please input result name/index, x and y axis FMUs, and x-axis and y-axis variables")
        elif (ret == "set-name"):
            if (echo):
                print("set-name")
                
            print("Setting name for FMUs:")
            if len(retString.split()) > 2:
                old_name = retString.split()[1]  # Get the FMU name from the input
                new_name = retString.split()[2]  # Give the new name to set for the FMU
                if fmu.set_name(old_name, new_name):  # Set the name for the FMU
                    print(f"FMU name changed from {old_name} to {new_name}.")
                else:
                    print(f"FMU with name {old_name} does not exist.")
            else:
                print("No name provided. Please provide a name to set for the FMU.")
        elif (ret == "save-directory"):
            if (echo):
                print("save-directory")

            if len(retString.split()) > 1:
                new_dir = retString.split()[1]
                ret = fmu.change_dir(new_dir)
                if ret:
                    print(f"Save directory changed to: {new_dir}")
            else:
                print("No new directory path was provided. Please provide new directory path in command call.")
        elif (ret == "current-setup"):
            if (echo):
                print("current-setup")

            print("Current FMUs:")
            fmu.list_fmus()
            print("")
            print("Current connections/links:")
            fmu.list_links()
            print("")
            fmu.list_data_input_vars()
            print("")
            fmu.list_results()
        elif (ret == "add-fmu"):
            if (echo):
                print("add-fmu")  

            if len(retString.split()) > 1:
                fmu_path = retString.split()[1]
                fmu_name = None
            else:
                print("No FMU path provided. Please provide FMU path to add.")
                continue
            
            if len(retString.split()) > 2:
                fmu_name = retString.split()[2]         # Get the FMU name from the input
                
            ret = fmu.add_fmu(fmu_path, fmu_name)
        elif (ret == "delete-fmu"):
            if (echo):
                print("delete-fmu")
            
            print("Deleting FMU from the list of FMUs:")
            if len(retString.split()) > 1:
                fmu_name = retString.split()[1]         # Get the FMU name from the input
                fmu.delete_fmu(fmu_name)                # Delete the FMU from the list
            else:
                print("No FMU name provided. Please provide an FMU name to delete.")
                continue
        elif (ret == "reset"):
            if (echo):
                print("reset")
            
            print("Resetting FMU files and save directory.")
            resetSaveDir = input("Also Reset Save Director [y/n]: ")

            while (resetSaveDir.lower() not in ['y', 'n']):
                resetSaveDir = input("Invalid input. Please enter 'y' or 'n': ")

            if resetSaveDir.lower() == 'y':
                while (1):
                    save_dir = input("Enter new save directory: ")
                    if save_dir == "" :
                        confirm = input("Confirm that you want the directory to be blank AKA current working directory [y]: ")
                        if (confirm == 'y'):
                            fmu.change_dir("")
                            break
                    else:
                        ret = fmu.change_dir(save_dir)
                        if not ret:
                            continue
                        break
            elif resetSaveDir.lower() == 'n':
                print("Save directory will not be changed.")

            fmu.reset()
        elif (ret == "add-data"):
            if echo:
                print("add-data")
            
            if len(retString.split()) > 2:
                is_seconds = input("CSV files must have a time column labeled 'time', with time in increasing increments in SECONDS. Continue? [y/n] ")
                while is_seconds.lower() not in ['y', 'n']:
                    is_seconds = input("Invalid input. Please enter 'y' or 'n': ")
                
                if is_seconds == 'y':
                    fmu_name = retString.split()[1]
                    data_path = retString.split()[2]

                    ret = fmu.add_data(fmu_name, data_path)

                    if ret:
                        print("Data successfully added.")
                        
                else:
                    print("Canceling adding data...")
            else:
                print("Not enough arguments provided. Please provide FMU name and path to Data file")
        elif (ret == "remove-data"):
            if echo:
                print("remove-data")
            
            if len(retString.split()) > 2:
                fmu_name = retString.split()[1]
                input_name = retString.split()[2]

                fmu.remove_data(fmu_name, input_name)
            else:
                print("Not enough arguments provided. Please provide FMU name and input name")
        elif (ret == "link"):
            if (echo):
                print("link")
            
            if len(retString.split()) > 4:
                fmu1 = retString.split()[1]
                output_name = retString.split()[2]
                fmu2 = retString.split()[3]
                input_name = retString.split()[4]

                try: 
                    output_name = int(output_name)
                except ValueError:
                    pass

                try:
                    input_name = int(input_name)
                except ValueError:
                    pass
            
                fmu.link_input_output(fmu1, output_name, fmu2, input_name)
            else:
                print("Not enough arguments provided. Please provide FMU names and input/output names to link.")
        elif (ret == "unlink"):
            if (echo):
                print("unlink")

            if len(retString.split()) > 4:
                fmu1 = retString.split()[1]
                output_name = retString.split()[2]
                fmu2 = retString.split()[3]
                input_name = retString.split()[4]

                fmu.unlink_input_output(fmu1, output_name, fmu2, input_name)
            elif len(retString.split()) > 2:
                fmu1 = retString.split()[1]
                input_or_output = retString.split()[2]

                if input_or_output.split("==")[0] == "input":
                    input_name = input_or_output.split("==")[1]
                    fmu.unlink_input_output(fmu1, input_name=input_name)

                elif input_or_output.split("==")[0] == "output":
                    output_name = input_or_output.split("==")[1]
                    fmu.unlink_input_output(fmu1, output_name=output_name)

                else:
                    print("Input or Output string is incorrectly formatted. Please use the following format:")
                    print("input==<input_name> or output==<output_name>")
            elif len(retString.split()) > 1:
                fmu.unlink_input_output(fmu1)
            else:
                print("Not enough arguments. Please input at least fmu_name.")
        elif (ret == "suppress"):
            if (echo):
                print("suppress")

            if len(retString.split()) > 1:
                fmu_name = retString.split()[1]
                input_name = None
                if len(retString.split()) > 2:
                    input_name = retString.split()[2]
                
                fmu.suppress_input(fmu_name, input_name)
            else:
                print("Not enough arguments. Please input at least fmu_name")
        elif (ret == "unsuppress"):
            if (echo):
                print("unsuppress")

            if len(retString.split()) > 1:
                fmu_name = retString.split()[1]
                input_name = None
                if len(retString.split()) > 2:
                    input_name = retString.split()[2]
                
                fmu.unsuppress_input(fmu_name, input_name)
            else:
                print("Not enough arguments. Please input at least fmu_name")
        elif (ret == "list"):
            if (echo):
                print("Listing FMUs:")

            fmu.list_fmus()
        elif (ret == "list-inputs"):
            if (echo):
                print("list_inputs")
            
            print("Listing inputs for FMUs:")
            if len(retString.split()) > 1:
                specificFmu = retString.split()[1]  # Get the FMU name from the input
                fmu.list_inputs(specificFmu)
            else:
                print("No FMU specified. Printing all inputs for all FMUs imported.")
                for fmu_name in fmu.fmu_objects.keys():
                    fmu.list_inputs(fmu_name)
        elif (ret == "list-outputs"):
            if (echo):
                print("list-outputs")

            print("Listing outputs for FMUs:")
            if len(retString.split()) > 1:
                specificFmu = retString.split()[1]
                fmu.list_outputs(specificFmu)
            else:
                print("No FMU specified. Printing all outputs for all FMUs imported.")
                for fmu_name in fmu.fmu_objects.keys():
                    fmu.list_outputs(fmu_name)
        elif (ret == "list-links"):
            if echo:
                print("list-links")

            if len(retString.split()) > 1:
                fmu_name = retString.split()[1]
                print(f"Listing links with {fmu_name}")
                fmu.list_link_for_fmu(fmu_name)
            else:
                print("No FMU specified. Listing all links.")
                fmu.list_links()
        elif (ret == "list-suppressed"):
            if echo:
                print("list-suppressed")

            fmu.list_suppressed()
        elif (ret == "list-res"):
            if echo:
                print("list-res")

            fmu.list_results()
        elif (ret == "export"):
            if echo:
                print("export")

            if len(retString.split()) > 1:
                workspace_name = retString.split()[1]
            else:
                print("Please input workspace name and try again.")
                continue

            if not login_or_reg():
                continue

            workspace_json, fmu_jsons, fmu_paths, connection_jsons = fmu.format_export_workspace(workspace_name)

            # TODO: figure out what we want to return. currently it just returns everything in a long string. format it better
            post_ret, get_ret = session.export_workspace(workspace_json, fmu_jsons, fmu_paths, connection_jsons)
            # if ret is not None:
            #     print(f"Workspace exported successfully, workspace id: {ret}")
            # else:
            #     print("Failed to export workspace.")
            print(post_ret)
            print(get_ret)
        elif (ret == "get-API-link"):
            if echo:
                print("get-API-link")

            print(session.base_url + "docs")

        else:
            print(f"Unknown command: {ret}. Type 'help' for a list of commands.")
            continue

        print("")