import pathlib as plib
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import plotly.offline as pyo
from aerofoil import read_aerofoil_data

current_file_path = plib.Path(__file__).parent
data_path = current_file_path.parents[1] / "data"


def Cp_vs_alpha(aerofoil_data:pd.DataFrame, metadata:dict[str, np.ndarray], Re:float, p_n_list: list=None):
    df = aerofoil_data
    x_list = metadata["x"]
    alpha_list = metadata["alpha_list"]
    
    Re_index = df["Re"] == Re
    alpha_index = df["alpha"].isin(alpha_list)
    index = np.logical_and(Re_index, alpha_index)
    filtered_df = df[index]

    test = filtered_df.columns
    if p_n_list is None:
        filter_cp_n= [col for col in filtered_df if col.startswith("Cp")]
        x_values = x_list
    else:
        p_n_list:np.ndarray = np.array(p_n_list)
        filter_cp_n = [f"Cp{i}" for i in p_n_list]
        x_values = x_list[p_n_list]

    # extracting the data
    
    cp_df = filtered_df[filter_cp_n]
    alpha_values = filtered_df["alpha"]
    cp_values = cp_df.values
    
    x_mesh, alpha_mesh = np.meshgrid(x_values, alpha_values)

    
    fig = go.Figure()
    fig.add_trace(
            go.Scatter3d(
                x=x_mesh.flatten(),
                z=cp_values.flatten(),
                y=alpha_mesh.flatten(),
                mode="markers"
                
            )
        )

    pyo.plot(fig, filename='offline_plot.html')
    
    return fig
    

if __name__ == "__main__":
    aerofoil_name = "NACA0012"
    aerofoil_data, metadata = read_aerofoil_data(aerofoil_name)

    # filtering data
    p_n_list = [1, 2]
    p_n_list = None

    Re = metadata["Re_list"][0]
    
    Cp_vs_alpha(aerofoil_data, metadata, p_n_list=p_n_list, Re=Re)

