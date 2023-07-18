from __future__ import annotations
import pathlib as pl
import subprocess as sp
import sys
from decimal import Decimal
import numpy as np


file_path = pl.Path(__file__).parent
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

def run_performance(xf:sp.Popen, **kwargs):
    # check if data path is available
    save_path = data_path / f"{kwargs['aerofoil_name']}/Re{int(kwargs['Re']):.0e}"
    
    polar_path = (save_path / "polar_file.txt\n").relative_to(file_path).as_posix()

    if not save_path.exists():
        save_path.mkdir(parents=True)
    
    # check OS TODO: implement support for non windows
    # if sys.platform.startswith("win"):
    #     save_path = pl.PureWindowsPath(save_path)

    
    load = False
    name = "J30"
    # disabling popup
    xf.stdin.write(b"PLOP\n")
    xf.stdin.write(b"G F\n")
    xf.stdin.write(b"\n")
    if load is True:
        xf.stdin.write(f"LOAD {name}".encode())
    xf.stdin.write(b"NACA 0012\n")
    xf.stdin.write(b"PANE\n")
    xf.stdin.write(b"OPER\n")
    xf.stdin.write(f"Visc {kwargs['Re']}\n".encode())
    xf.stdin.write(f"ITER {n_iter_terminate}\n".encode())
    # xf.stdin.write(b"VPAR\n")
    # xf.stdin.write("XTR {} {}\n".format(Xtrtop,Xtrbot)) TODO: implement transition
    # xf.stdin.write(f"N {kwargs['N_crit']}\n".encode())
    xf.stdin.write(b"PACC\n")

    xf.stdin.write(polar_path.encode())
    xf.stdin.write(b'\n')
    
    xf.stdin.write(f"aseq {kwargs['alpha_i']} {kwargs['alpha_f']} {kwargs['alpha_step']}\n".encode())
    xf.stdin.write(b"\n\n")

    xf.stdin.write(b"quit\n")
    xf.stdin.close()

    xf.stdin.close()
    
def run_pressure(xf: sp.Popen):
    xf.stdin.write(b"")


def call_xfoil(**kwargs):
    if kwargs["Re_start"] == kwargs["Re_end"]:
        Re_list = [kwargs["Re_start"]]
    else:
        Re_list = np.linspace(kwargs["Re_start"], kwargs["Re_end"], kwargs["n_Re_intervals"]).tolist()

    # start a new process for each Re
    for Re in Re_list:
        xf = open_xfoil()
        run_performance(xf=xf, Re=Re, **kwargs)
    return

if __name__ == "__main__":
    # user inputs
    aerofoil_name = "NACA0012"

    # viscoscity
    Re_start = 3e6
    Re_end = 3e6
    n_Re_intervals = 10

    # angle 
    angle_of_attack_start = -2
    angle_of_attack_end = 2
    angle_of_attack_interval = .5

    # turbulence setting
    x_transition_top = None
    x_transition_bot = None
    N_crit = 9

    # xfoil config
    n_iter_terminate = 50
   
    call_xfoil(
        aerofoil_name=aerofoil_name,
        Re_start=Re_start, 
        Re_end=Re_end,
        n_Re_intervals=n_Re_intervals,
        alpha_i=angle_of_attack_start,
        alpha_f=angle_of_attack_end,
        alpha_step=angle_of_attack_interval,
        x_transition_top=x_transition_top,
        x_transition_bot=x_transition_bot,
        n_iter_terminate=n_iter_terminate,
        N_crit=N_crit,
    )