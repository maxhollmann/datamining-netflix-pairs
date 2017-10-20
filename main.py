import numpy as np
import time

import data
import pair_finder


def main(args):
    np.random.seed(seed=args.seed)
    df = data.load(args.data)

    # Make IDs start at 0 for easier indexing
    df.user = df.user - 1
    df.movie = df.movie - 1

    pairfinder = pair_finder.build(
        data=df, sig_len=args.sig_len, bands=args.bands,
        max_buckets=100000, cached=args.use_cache)
    pairfinder.prepare()


    import code; code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs the MinHash/LSH algorithm to find pairs of similar Netflix users.')
    parser.add_argument('--sig-len', type=int, default=20, help='Signature length.')
    parser.add_argument('--bands', type=int, default=5, help='Number of bands.')
    parser.add_argument('--max-buckets', type=int, default=100000, help='Maximum number of buckets.')
    parser.add_argument('--results', default="results.txt", help='File to store pairs of user IDs in.')

    parser.add_argument('--use-cache', '-c', action='store_true',
                        help='Try to load objects from previous runs, and store them for future runs.')

    parser.add_argument('seed', metavar='random-seed', type=int,
                        help='Seed for the random number generator, set once at start of the program.')
    parser.add_argument('data', help='Path to the data in .npy format.')

    args = parser.parse_args(sys.argv[1:])

    main(args)
