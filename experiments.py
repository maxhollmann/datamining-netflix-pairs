import multiprocessing as mp
import numpy as np
import time
import logging

import data
import pair_finder


def main(args):
    np.random.seed(seed=args.seed)
    df = data.load(args.data)

    # Make IDs start at 0 for easier indexing
    df.user = df.user - 1
    df.movie = df.movie - 1


    pairfinder = pair_finder.build(
        data=df, sig_len=50, bands=5,
        max_buckets=100000, cached=True)

    for siglen in [50, 100, 150]:
        for bands in [5, 10, 15]:
            pairfinder.sig_len = siglen
            pairfinder.n_bands = bands
            pairfinder.prepare()


    import code; code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs experiments.')

    parser.add_argument('--seed', metavar='random-seed', type=int,
                        help='Seed for the random number generator, set once at start of the program.')
    parser.add_argument('--data', default='user_movie.npy', help='Path to the data in .npy format.')

    args = parser.parse_args(sys.argv[1:])

    main(args)
