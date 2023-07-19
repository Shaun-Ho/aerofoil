from __future__ import annotations
import pathlib as plib
import subprocess as sp
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

def run_performance(xf:sp.Popen, Re:float, **kwargs):
    save_path = data_path / f"{aerofoil_name}/Re{Re:.0e}"
    polar_name = (save_path / "polar_file.txt\n").relative_to(file_path).as_posix()

    # setting polar save path
    xf.stdin.write(b"PACC\n")
    xf.stdin.write(polar_name.encode())
    xf.stdin.write(b'\n')
    # running sequential alpha performance
    xf.stdin.write(f"ASEQ {kwargs['alpha_i']} {kwargs['alpha_f']} {kwargs['alpha_step']}\n".encode())
    xf.stdin.write(b'\n')
    xf.stdin.write(b"quit\n")
    xf.stdin.close()

def setup_run(xf:sp.Popen, aerofoil_name:str, Re:float, load=False, **kwargs):
    save_path = data_path / f"{aerofoil_name}/Re{Re:.0e}"
    if not save_path.exists():
        save_path.mkdir(parents=True)
    
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
    
    
def run_pressure(xf:sp.Popen, Re:float, alpha: float, **kwargs):
    save_path = data_path / f"{aerofoil_name}/Re{Re:.0e}"
    cp_name = (save_path / f"{alpha:.1f}cp.txt\n").relative_to(file_path).as_posix()
    # running specific alpha
    xf.stdin.write(f"alfa {alpha}\n".encode())
    # writing cp distribution
    xf.stdin.write(b"cpwr\n")
    xf.stdin.write(cp_name.encode())
    xf.stdin.write(b'\n')
    xf.stdin.write(b"quit\n")
    xf.stdin.close()


def call_xfoil(aerofoil_name:str, **kwargs):
    if kwargs["Re_start"] == kwargs["Re_end"]:
        Re_list = [kwargs["Re_start"]]
    else:
        Re_list = np.linspace(kwargs["Re_start"], kwargs["Re_end"], kwargs["n_Re_intervals"]).tolist()

    if kwargs["alpha_i"] == kwargs["alpha_f"]:
        alpha_list = [kwargs["alpha_i"]]
    else:
        alpha_list = np.arange(kwargs["alpha_i"], kwargs["alpha_f"]+kwargs["alpha_step"], kwargs["alpha_step"]).tolist()

    # start a new process for each Re
    for Re in Re_list:
        xf = open_xfoil()
        xf = setup_run(xf, aerofoil_name, Re, load=False ,**kwargs)
        run_performance(xf=xf, Re=Re, **kwargs)

        # running presure
        for alpha in alpha_list:
            # start a new process for each cp
            xf = open_xfoil()
            xf = setup_run(xf, aerofoil_name, Re, load=False ,**kwargs)
            run_pressure(xf, Re, alpha, **kwargs)
        
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
    angle_of_attack_interval = 0.5

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