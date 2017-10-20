import numpy as np
import pandas as pd


def load(filename = "user_movie.npy"):
    data = pd.DataFrame(np.load(filename), columns=("user", "movie"))
    return data
