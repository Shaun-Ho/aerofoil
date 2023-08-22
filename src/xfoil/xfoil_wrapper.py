from __future__ import annotations

import os
import pathlib as plib
import subprocess as sp
import multiprocessing

import numpy as np

file_path = plib.Path(__file__).parent
xfoil_exe_path = file_path / "xfoil_6.99"
data_path = file_path / "data"

def open_xfoil():
    xf = sp.Popen(
        [xfoil_exe_path /'xfoil.exe'],
        stdin=sp.PIPE,
        stdout=None,
        cwd=file_path
    )

    return xf

def run_performance(xf:sp.Popen, save_path:plib.Path, alpha_i:float, alpha_step:float, alpha_f:float=None):
    polar_name = (save_path / "polar_file.txt\n").relative_to(file_path).as_posix()

    # setting polar save path
    xf.stdin.write(b"PACC\n")
    xf.stdin.write(polar_name.encode())
    xf.stdin.write(b'\n')
    # running sequential alpha performance
    if alpha_f is None:
        xf.stdin.write(f"alfa {alpha_i}\n".encode())
    else:
        xf.stdin.write(f"ASEQ {alpha_i} {alpha_f} {alpha_step}\n".encode())
    xf.stdin.write(b'\n')
    xf.stdin.write(b"quit\n")
    xf.stdin.close()

def setup_run(xf:sp.Popen, aerofoil_name:str, Re:float, load:bool=False, n_iter_terminate:int=100):   
    # loading
    xf.stdin.write(b"PLOP\n")
    xf.stdin.write(b"G F\n")
    xf.stdin.write(b"\n")
    if load is True:
        xf.stdin.write(f"LOAD {aerofoil_name}".encode())
    xf.stdin.write(f"{aerofoil_name}\n".encode())
    xf.stdin.write(b"PANE\n")
    xf.stdin.write(b"OPER\n")
    xf.stdin.write(f"Visc {Re}\n".encode())
    xf.stdin.write(f"ITER {n_iter_terminate}\n".encode())
    
    # xf.stdin.write(b"VPAR\n")
    # xf.stdin.write("XTR {} {}\n".format(Xtrtop,Xtrbot)) TODO: implement transition
    # xf.stdin.write(f"N {kwargs['N_crit']}\n".encode())

    return xf
    
    
def run_pressure(xf:sp.Popen, save_path:plib.Path, alpha: float):
    cp_name = (save_path / f"cp_dist_alpha={alpha:.1f}.txt\n").relative_to(file_path).as_posix()
    # running specific alpha
    xf.stdin.write(f"alfa {alpha}\n".encode())
    # writing cp distribution
    xf.stdin.write(b"cpwr\n")
    xf.stdin.write(cp_name.encode())
    xf.stdin.write(b'\n')
    xf.stdin.write(b"quit\n")
    xf.stdin.close()

def run_xfoil(aerofoil_name:str, Re: float, alpha_i, alpha_step:float=.1, alpha_f:float=None):
    # creating directory for save path
    save_path = data_path / f"{aerofoil_name}/Re{Re:.2e}"
    if not save_path.exists():
        save_path.mkdir(parents=True)

    # deleting polar file if it already exists
    if len(list(save_path.glob("polar_file.txt")))>0:
        os.remove(save_path / "polar_file.txt")
        print
    # start new process for each Re
    xf = open_xfoil()
    xf = setup_run(xf, aerofoil_name, Re)

    # constructing alpha array
    if alpha_f is None:
        alpha_list = [alpha_i]
    else:
        alpha_list = np.arange(alpha_i, alpha_f + alpha_step, alpha_step).round(1).tolist()

    run_performance(xf, save_path, alpha_i, alpha_step, alpha_f=alpha_f)
    stdout, stderr = xf.communicate()

    # running presure
    for alpha in alpha_list:
        # start a new process for each cp
        xf = open_xfoil()
        xf = setup_run(xf, aerofoil_name, Re, load=False)
        run_pressure(xf, save_path, alpha)
        stdout, stderr = xf.communicate()

def call_xfoil(aerofoil_name:str, Re_start, alpha_i, alpha_f = None, alpha_step = .1, Re_end = None, n_Re_intervals = 10, **kwargs):
    # constructing Reynolds number array
    if Re_end is None:
        Re_list = [Re_start]
    else:
        Re_list = np.linspace(Re_start, Re_end, n_Re_intervals).tolist()
    # option to run multiprocessing
    if kwargs["run_multi"] == True:
            test = [(aerofoil_name, ) + (e,) + (alpha_i, alpha_step, alpha_f) for e in Re_list ]
    try: 
        if kwargs["run_multi"] == True:
            with multiprocessing.Pool(processes=kwargs["n_processes"]) as pool:
                pool.starmap(run_xfoil, [(aerofoil_name, ) + (e,) + (alpha_i, alpha_step, alpha_f) for e in Re_list ])
    except:
        for Re in Re_list:
            run_xfoil(aerofoil_name, Re, alpha_i, alpha_step, alpha_f)