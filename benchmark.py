import numpy as np
from timeit import Timer

import data
from alg import *


def test_jaccard_similarity(d):
    jaccard_similarity(d.loc[d.user == 1].movie, d.loc[d.user == 2].movie)


d = data.load()


def main(args):
    if len(args) != 1:
        raise Exception("1 argument required: test to run")

    test = args[0]


    def time(stmt, setup):
        t = Timer(stmt, setup=setup, globals = globals())
        return t.timeit(150) / 150

    if test == "jaccard":
        t = time("test_jaccard_similarity(d)", setup="from __main__ import test_jaccard_similarity")
        print("Python set:", t)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
