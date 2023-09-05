import pathlib as plib
import pandas as pd

current_file_path = plib.Path(__file__).parent
data_path = current_file_path.parents[1] / "data"


def read_aerofoil_data(aerofoil_name:str) -> dict[str, pd.DataFrame]:
    performance_data = pd.read_csv(data_path / f"{aerofoil_name}.csv")
    coords = pd.read_csv(data_path / "coords"/ f"{aerofoil_name}.csv")
    data = dict(
        coords=coords,
        data=performance_data
    )
    return data