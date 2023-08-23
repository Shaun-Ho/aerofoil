from __future__ import annotations
import pandas as pd
import pathlib as plib
import glob
import re
import numpy as np

file_path = plib.Path(__file__).parent
xfoil_exe_path = file_path / "xfoil_6.99"
data_path = file_path / "data"

def read_content(string_list:list , header_line_num:int, start_line_num:int, Re_line_num: int = None, Re_default:float=None):
    data = dict()
    header_line = re.sub(r'\s+', ",", string_list[header_line_num])
    header_list = list(filter(lambda x: x not in ["", "#"], header_line.split(",")))
    if Re_line_num is not None:
        Re_line = string_list[Re_line_num]
        Re_line = re.sub(r'\s+', ",", Re_line)
        Re_line = Re_line.split(",")
        Re_position = Re_line.index("Re")

        # checking for Re
        
        try:
            if Re_line[Re_position + 3] == "e":
                Re = float(Re_line[Re_position + 2]) * 10 ** int(Re_line[Re_position + 4])
            else:
                Re = float(Re_line[Re_position + 2])
        except:
            Re = Re_default

        # checking for alpha
        try:
            alpha_position = Re_line.index("Alfa")
            alpha = float(Re_line[alpha_position + 2])
            data["alpha"] = np.full(len(string_list[start_line_num:]), alpha)
        except: 
            pass
        
        
        data["Re"] = np.full(len(string_list[start_line_num:]), Re)

    for i in range(len(header_list)):
        data[header_list[i]] = np.zeros(len(string_list[start_line_num:]))

    for line_i in range(0,len(string_list[start_line_num:])):
        line = string_list[line_i+start_line_num]
        line = re.sub(r'\s+', ",", line)
        line_list = list(filter(lambda x: x!="", line.split(",")))
        for j in range(len(header_list)):
            data[header_list[j]][line_i] = line_list[j]

    return data

def format_dataset(aerofoil_name:str):
    polar_file_path_list = glob.glob((data_path / f"{aerofoil_name}" / "**" / "polar_file.txt").as_posix(), recursive=True)
       
    Re_line_num = 8
    header_line_num = 10
    start_line_num = 12

    all_polar_data:dict[np.ndarray] = dict()
    # reference
    polar_file_name = polar_file_path_list[0]
    reference_polar_file = open(polar_file_name, "r")
    ref_string_list = reference_polar_file.readlines()
    reference_polar_file.close()
    ref_polar_data = read_content(ref_string_list, header_line_num, start_line_num, Re_line_num)
    for key in ref_polar_data:
        all_polar_data[key] = np.array([])

    #creating a master csv file for data
    for polar_file_path in polar_file_path_list:
        # polar_file = open(plib.Path(polar_file_path_list[0]), "r")
        polar_file = open(polar_file_path, "r")
        string_list = polar_file.readlines()
        polar_file.close()
        polar_data = read_content(string_list, header_line_num, start_line_num, Re_line_num)
        for key, value in polar_data.items():
            all_polar_data[key] = np.append(all_polar_data[key], value)
    
    # constructing the arrays for cps
    Re_list = np.unique(all_polar_data["Re"])
    # finding reference file (determining number of cp columns)
    Re_line_num = 1
    header_line_num = 2
    start_line_num = 3

    Re = Re_list[0]
    Re_str = f"Re{Re:.2e}"
    cp_files = glob.glob((data_path / f"{aerofoil_name}" / f"{Re_str}" / "cp_dist_alpha=*.txt").as_posix(), recursive=True)
    ref_cp_file = open(cp_files[0], "r")
    string_list = ref_cp_file.readlines()
    ref_cp_dist_data = read_content(string_list, header_line_num, start_line_num, Re_line_num)

    # storing coordinates
    coord_data = dict(
        x= ref_cp_dist_data["x"],
        y= ref_cp_dist_data["y"]
    )

    # initialising arrays for data
    for i in range(ref_cp_dist_data["Cp"].shape[0]):
        all_polar_data[f"Cp{i}"] = np.zeros(all_polar_data["alpha"].shape[0])

    for Re in Re_list:
        Re_str = f"Re{Re:.2e}"
        cp_files = glob.glob((data_path / f"{aerofoil_name}" / f"{Re_str}" / "cp_dist_alpha=*.txt").as_posix(), recursive=True)
        
        for cp_filename in cp_files:
            cp_file = open(cp_filename, "r")
            string_list = cp_file.readlines()
            single_cp_dist_data = read_content(string_list, header_line_num, start_line_num, Re_line_num, Re)
            # Re match
            Re_match = np.isclose(all_polar_data["Re"], single_cp_dist_data["Re"][0], rtol=1e-3)
            # alpha match
            alpha_match = all_polar_data["alpha"] == single_cp_dist_data["alpha"][0]
            match_index = np.logical_and(Re_match, alpha_match)

            for i in range(single_cp_dist_data["Cp"].shape[0]):
                cp_array = all_polar_data[f"Cp{i}"] 
                cp_array[match_index] = single_cp_dist_data["Cp"][i]
                all_polar_data[f"Cp{i}"] = cp_array
        
        

    df = pd.DataFrame(data=all_polar_data)
    coords = pd.DataFrame(data=coord_data)
    return df, coords
