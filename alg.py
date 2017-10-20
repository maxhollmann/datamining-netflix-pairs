import numpy as np

def jaccard_similarity(x, y):
    return len(np.intersect1d(x, y)) / len(np.union1d(x, y))

    # using two columns from UM:
    a1 = UM[:, 11].toarray()
    a2 = UM[:, 10].toarray()
    return np.sum(np.logical_and(a1, a2)) / np.sum(np.logical_or(a1, a2))
