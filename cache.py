import numpy as np

def save(obj, name):
    f = open("cached_{}.npy".format(name), "wb")
    np.save(f, obj)

def load(name):
    obj = np.load("cached_{}.npy".format(name))
    #raise Exception("No cache found for {}".format(name))
    return obj
