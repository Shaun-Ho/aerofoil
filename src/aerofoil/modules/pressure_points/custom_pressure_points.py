import numpy as np
import pandas as pd
import pathlib as plib

current_file_path = plib.Path(__file__).parent
data_path = current_file_path.parents[1] / "data"

def select_point(coords_df: pd.DataFrame, x:float, topbottom:str):
    x_coords = coords_df["x"].to_numpy()
    y_coords = coords_df["y"].to_numpy()

    x_top = x_coords[y_coords>=0]
    y_top = y_coords[y_coords>=0]

    x_bot = x_coords[y_coords<=0]
    y_bot = y_coords[y_coords<=0]

    if "t" in topbottom.lower():
        x_array = x_top
        y_array = y_top

    else:
        x_array = x_bot
        y_array = y_bot

    x_right = x_array[x_array > x]
    x_left = x_array[x_array < x]

    y_right = y_array[x_array > x]
    y_left = y_array[x_array < x]

    idx_min = np.argmax(x_left)
    idx_max = np.argmin(x_right)
    
    closest_x_min = x_left[idx_min]
    closest_x_max = x_right[idx_max]

    closest_y_max = y_right[idx_max]
    closest_y_min = y_left[idx_min]

    # linear interpolation
    e = (x-closest_x_min)/(closest_x_max-closest_x_min)
    y = closest_y_min + e * (closest_y_max - closest_y_min)
    return y

if __name__ == "__main__":
    aerofoil_name = "NACA0012"
    coords = pd.read_csv(data_path / "coords" /f"{aerofoil_name}.csv")
    select_point(coords, .5, "t")