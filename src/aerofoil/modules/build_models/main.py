import pathlib as plib
import pandas as pd
import numpy as np

current_file_path = plib.Path(__file__).parent
data_path = current_file_path.parents[1] / "data"


def read_aerofoil_data(aerofoil_name:str) -> dict[str, pd.DataFrame]:
    # performance_data = pd.read_hdf(data_path / f"{aerofoil_name}.h5",key="data")
    with pd.HDFStore(data_path / f'{aerofoil_name}.h5') as storedata:
        data = storedata['data']
        metadata = storedata.get_storer('data').attrs.metadata
    return data, metadata

def h5_aerofoil_data(aerofoil_name):
    performance_data = pd.read_csv(data_path / f"{aerofoil_name}.csv")
    coords = pd.read_csv(data_path / "coords" / f"{aerofoil_name}.csv")
    metadata = dict(
        x=coords["x"],
        y=coords["y"],
        alpha_list=np.unique(performance_data["alpha"].to_numpy()),
        Re_list=np.unique(performance_data["Re"].to_numpy())
    )
    storedata = pd.HDFStore(data_path / f"{aerofoil_name}.h5")
    storedata.put("data", performance_data)
    storedata.get_storer("data").attrs.metadata = metadata
    storedata.close()

if __name__ == "__main__":
    read_aerofoil_data("NACA0012")
    # h5_aerofoil_data("NACA0012")