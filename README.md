# NIST Co-Sim

NIST Co-Sim is an open source Co-Simulation platform that allows connection to Labview
for real time simulation between the lab and the digital twin. NIST Co-sim uses 
Functional Mock-Up Units (FMUs) with python package PyFMI for Co-Simulation, which
are compliant with the Functional Mock-Up Interface (FMI) ([FMI] (https://fmi-standard.org/))

## Overview

NIST Co-Sim offers an open source alternative for running cross-platform Co-Simulation. 
Communication between models is facilitated through FMUs.
Currently, exportation from original modeling programs is not a feature of NIST Co-Sim; 
contributors are working on expanding it to become a native tool.

Currently, FMUs must be compliant with FMI version 2.0 and only for Co-Simulation; 
Model Exchange FMUs are not compatable with NIST Co-Sim.

While running a Co-Simulation Environment through NIST Co-Sim is open source, connection 
to NIST onsight labs must be through NIST approved LabView/network. 
If you are a guest researcher, please reach out to a NIST employee for access beforehand.

## Current Release Status

Release 1.0 -- Working on implementing LabView interface and Exportation Tool

## Installation

```
git clone ... (link here)
pip install -r requirements.txt
```

## NIST Co-Sim User's Guide

### Running Through Terminal Interface
xael move this?

```
## 3 options to start the terminal interface:
## All 3 will create a "Result_and_Logs" folder in your save/current directory. This will 
## be where your runs logs, results, and plot.pngs will be saved

## Run terminal with no FMUs added and Save Directory is set to current directory:
python run.py

## Run terminal with no FMUs added and Save Directory is set to 'save-dir'
python run.py C:\user\save-dir

## Run terminal with FMUs added and Save Directory is set to 'save-dir'
python run.py C:\user\save-dir C:\path\to\FMU1.fmu C:\path\to\FMU2.fmu

=============================================

          running co-sim environment

=============================================

Save Directory is defaulted to current directory.
To change save directory, type 'save-directory <path>'

No FMUs were added.
To add FMUs type:
add-FMU <filePath>
or
add-FMU <fmu_path> <fmu_name>


Type 'help' for more information

[cosim_fmu]: help
This is a program to cosimulate FMUs with different programs.
You can export an FMU from a program if FMU is not already exported.
You can also run the FMU in real-time with a specific model and a specific database.
All result FMUs will be saved in the directory .
Correct usage of program:
python run.py                                   -                                run with default current directory as save directory
python run.py <save_dir>                        -                                run with specified save directory
python run.py <save_dir> <FMU1> <FMU2> ...      -                                run with specified save directory and fmus

add echo option at the end to echo commands

Examples:
python run.py /path/to/save_dir
python run.py /path/to/save_dir /path/to/FMU1.fmu /path/to/FMU2.fmu echo
Press any key to continue. Enter 'done' to quit the help menu.


Available commands:

Commands for running and viewing results:
run :                                                                                                            run simulation or real-time FMUs
name-res <old_name> <new_name> :                                                                      rename a result from the default 'result_#'
view-res <result_name/result_index> :                                                  view result via result_name or index, array of all outputs
view-res <result_name/result_index> <FMU> <variables> :                  view result via result_name or index, array of specific output variables
graph-res <result_name/result_index> <x-axis_fmu> <x-axis_variable> 
<y-axis_fmu1> <y-axis_variable1> <y-axis_fmu2> <y-axis_variable2>... :        graph result with x-axis result variable and y-axis result variable
doc :                                                                                                   doc about general errors and helpful tips

Press any key to continue. Enter 'done' to quit the help menu.


Commands for setting up workspace:

set-name <fmu_name> <new_name> :                                                                                        set a new name for an FMU
save-directory <dirPath> :                                                                                    set new save results directory path
current-setup :                                                                                               prints your current workspace setup

add-FMU <fmu_path> :                                                                                            add an FMU to current list of FMUs
add-FMU <fmu_path> <fmu_name> :                                                                add an FMU with a specific name to the list of FMUs
delete-FMU <fmu_name> :                                                                                        delete an FMU from the list of FMUs
reset :                                                                                                     reset the FMU files and save directory


Press any enter to continue. Enter 'done' to quit the help menu.


Altering data commands:
add-data <fmu_name> <data_path> :                                                        add data to input rather than connection to another model
remove-data <fmu_name> <input_name> :                                                                                       remove data from input

Linking commands:
link <fmu_name> <output_name> <fmu_name> <intputName> :                                                  link an input and output for variable name
link <fmu_name> <outputIndex> <fmu_name> <inputIndex> :                                                  link an output and input by variable index

Unlinking commands:
unlink <fmu_name> :                                                                                       removes all connections/links to fmu_name
unlink <fmu_name> input==all :                                                                   removes all links where fmu_name is the input port
unlink <fmu_name> input==<input_name> :                                                         removes specific link with input_name from fmu_name
unlink <fmu_name> output==all :                                                                 removes all links where fmu_name is the output port
unlink <fmu_name> output==<output_name> :                                                  removes specific link where output_name is from fmu_name
unlink <input_fmu_name> <input_name> <output_fmu_name> <output_name> :                        unlink specific input_name and output_name connection


Press any enter to continue. Enter 'done' to quit the help menu.


suppress <fmu_name> :                                                                              suppress warnings about all inputs from fmu_name
suppress <fmu_name> <input_name> :                                                        suppress warnings about specific input_name from fmu_name
unsuppress <fmu_name> :                                                                          unsuppress warnings about all inputs from fmu_name
unsuppress <fmu_name> <input_name>:                                                     unsuppress warnings about specific input_name from fmu_name

list :                                                                                                                               list all FMUs
list-links :                                                                                                           list all links between FMUs
list-links <fmu_name> :                                                                                           list all links for a certain FMU
list-inputs <fmu_name> :                                                                                        list all inputs for a specific FMU
list-outputs <fmu_name> :                                                                                      list all outputs for a specific FMU
list-suppressed <fmu_name> :                                                                                            list all suppressed inputs
list-res :                                                                                              list all result names and result variables


To exit, type 'exit' or 'quit'.
[cosim_fmu]: exit
```

### Running Digital Twin/Co-Simulation
xael make this it's own page?
```
## Adding an EnergyPlus model
[cosim_fmu]: add-FMU C:\path\to\FMU1.fmu
C:\Users\...\JModelica.org\...\variables.cfg
1 File(s) copied
Adding FMU to the list of FMUs: 'FMU1'

[cosim_fmu]: add-FMU C:\path\to\FMU2.fmu
Adding FMU to the list of FMUs: 'FMU2'

## Connecting/linking FMU input and outputs
[cosim_fmu]: link FMU1 FMU1_output_name FMU2 FMU2_input_name
Linking input and output for FMUs:
Linked output 'FMU1_output_name' of FMU 'FMU1' to input 'FMU2_input_name' of FMU 'FMU2'.

[cosim_fmu]: add-data FMU1 C:\path\to\data.csv
No input with 'Var1_Name' found in FMU1. Skipping.
No input with 'Var2_Name' found in FMU1. Skipping.
Data successfully added.

[cosim_fmu]: run

Running FMUs with the following parameters:
Save Dir: Current Directory
Current FMUs:
 - FMU1
 - FMU2
Current connections/links:
Output:                                         Input:
(FMU1) FMU1_output_name                         (FMU2) FMU2_input_name
Warning: input variable Input_Var_Name from FMU1 does not have data input or connection to another model

There are inputs missing either connection or data.

Warning: no initial data. May cause errors to arise.

Results will be saved in: 'C:\Users\...\Result_and_Logs'

## Be careful when running EnergyPlus models, as they call EnergyPlus on terminal
## If the EnergyPlus model terminates due to user failure to setup model, NIST Co-Sim will also terminate.
## If the run does terminate, you can press the 'up-arrow' to get back previous commands fast to reset workspace.
Confirm continue to run? [Y/y] y

Run with simulation or to lab [sim/lab]: sim
Running FMUs in simulation mode...

Input start time: 0
Input finale_time: 86400
Input additional options, type 'list options' to see the full list of options, type 'done' if done inputting additional options.
Input additional options: done

...
NOT ACTUAL OUTPUT, PLACEHOLDER FOR SIMPLICITY FOR README.MD
Various Outputs from Energyplus and JModelica Solvers... See Doc for more help
...
Simulation interval      : 0.0 - 86400.0 seconds.
Elapsed simulation time  : 27.077421099995263 seconds.
 0.922578 seconds spent in FMU2.
 0.539237 seconds spent in FMU1.idf.
 18.769513 seconds spent saving simulation result.

Run finished...
Saved result as 'result'. To view result use command 'view-res <result_name/result_index>' 'view-res <result_name/result_index> <variable_list>'
or 'graph-res <result_name/result_index> <x-axis_variable> <y-axis_variable>'
Rename the result with 'name-res <old_name> <new_name>'
Would you like to reset your workspace, or keep current FMU/Links? [reset/keep] keep

...
NOT ACTUAL OUTPUT, PLACEHOLDER FOR SIMPLICITY FOR README.MD
Various Outputs cleaning up simulation files
...

```

### Connecting to Lab

1. Through terminal:


2. Through LabView python block:

## License
xael check if this is the most up to date license
[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)

This Software (NIST Co-Sim) is being made available as a public service by the [National Institute of Standards and Technology (NIST)](https://www.nist.gov/), an Agency of the United States Department of Commerce.
This software was developed in part by employees of NIST and in part by NIST contractors.
Copyright in portions of this software that were developed by NIST contractors has been licensed or assigned to NIST.
Pursuant to Title 17 United States Code Section 105, works of NIST employees are not subject to copyright protection in the United States.
However, NIST may hold international copyright in software created by its employees and domestic copyright (or licensing rights) in portions of software that were assigned or licensed to NIST.
To the extent that NIST holds copyright in this software, it is being made available under the [Creative Commons Attribution 4.0 International license (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/).
The disclaimers of the CC BY 4.0 license apply to all parts of the software developed or licensed by NIST.

## How to Cite