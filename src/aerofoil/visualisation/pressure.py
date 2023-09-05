import pathlib as plib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from aerofoil import read_aerofoil_data

current_file_path = plib.Path(__file__).parent
data_path = current_file_path.parents[1] / "data"

def pressure_vs_alpha(aerofoil_data:dict[str, pd.DataFrame]):
    df = aerofoil_data["data"]
    headers = list(df.columns)
    Re_list = np.unique(df["Re"].to_numpy())
    fig = go.Figure()

    for Re in Re_list:
        index = df["Re"] == Re
        test = df["Re"][index].to_numpy()
        fig.add_trace(
            go.Scatter3d(
                
            )
        )
    
    return fig
    

if __name__ == "__main__":
    aerofoil_name = "NACA0012"
    aerofoil_data = read_aerofoil_data(aerofoil_name)

    # filtering data
    
    pressure_vs_alpha(aerofoil_data)

