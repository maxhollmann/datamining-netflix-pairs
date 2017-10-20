import numpy as np
from scipy import sparse
import time

import data
import cache
import pair_finder


def main(args):
    np.random.seed(seed=args.seed)
    df = data.load(args.data)

    # Make IDs start at 0 for easier indexing
    df.user = df.user - 1
    df.movie = df.movie - 1

    try:
        if not args.use_cache: raise Exception()
        UM = sparse.load_npz("cached_UM.npz")
        print("Using cached UM")
    except:
        # CSC -> 16s init, .988s per random row permutation
        # CSR -> 37s init, .537s per random row permutation
        print("Loading UM...")
        t = time.time()
        UM = sparse.csr_matrix((np.max(df.movie) + 1, np.max(df.user) + 1), dtype=np.uint8)
        UM[df.movie, df.user] = 1
        print("Done in {}s".format(time.time() - t))
        sparse.save_npz(open("cached_UM.npz", "wb"), UM)

    pairfinder = pair_finder.build(UM, sig_len=21, bands=5, max_buckets = 100000, cached = args.use_cache)
    pairfinder.prepare()

    import code; code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs the MinHash/LSH algorithm to find pairs of similar Netflix users.')
    parser.add_argument('--use-cache', '-c', action='store_true',
                        help='Try to load objects from previous runs, and store them for future runs.')

    parser.add_argument('seed', metavar='random-seed', type=int,
                        help='Seed for the random number generator, set once at start of the program.')
    parser.add_argument('data', help='Path to the data in .npy format.')

    args = parser.parse_args(sys.argv[1:])

    main(args)
