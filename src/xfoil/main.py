from xfoil.xfoil_wrapper import call_xfoil
from xfoil.formatting import format_dataset
import pathlib as plib
import numpy as np
import pandas as pd

path = plib.Path(__file__).parent
save_path = path.parents[1] / "data"

if __name__ == "__main__":
    # user inputs
    aerofoil_name = "NACA0012"

    do = "format" 
    run_multi = True
    n_processes = 6

    # viscoscity
    Re_start = 3e6
    Re_end = 3e9
    n_Re_intervals = 200

    # angle 
    angle_of_attack_start = -5
    angle_of_attack_end = 5
    angle_of_attack_interval = 0.1

    # turbulence setting
    x_transition_top = None
    x_transition_bot = None
    N_crit = 9

    # xfoil config
    n_iter_terminate = 100

    if do == "run":
        call_xfoil(
        aerofoil_name=aerofoil_name,
        Re_start=Re_start, 
        Re_end=Re_end,
        n_Re_intervals=n_Re_intervals,
        alpha_i=angle_of_attack_start,
        alpha_f=angle_of_attack_end,
        alpha_step=angle_of_attack_interval,
        n_iter_terminate=n_iter_terminate,
        run_multi=run_multi,
        n_processes=n_processes
        # x_transition_top=x_transition_top,
        # x_transition_bot=x_transition_bot,
        # N_crit=N_crit,
    )
    elif do == "format":
        df, coords = format_dataset(aerofoil_name)
        # df.to_csv(save_path / f"{aerofoil_name}.csv")
        # coords.to_csv(save_path / "coords" / f"{aerofoil_name}.csv")
            
        df.attrs["Re_range"]=np.unique(df["Re"].to_numpy())
        df.attrs["alpha_range"]=np.unique(df["alpha"].to_numpy())
        df.attrs["x_coords"]=coords["x"]
        df.attrs["y_coords"]=coords["y"]
        
        df.to_hdf(save_path / f"{aerofoil_name}.h5", key="performance_data")
