import numpy as np
import time

import data
import pair_finder
from util import calculate_algorithm_params
import commands


def main(args):
    np.random.seed(seed=args.seed)
    df = data.load(args.data)

    # Make IDs start at 0 for easier indexing
    df.user = df.user - 1
    df.movie = df.movie - 1

    sig_len, bands = calculate_algorithm_params(args)
    print("Sig len: {}    bands: {}    rows: {}".format(sig_len, bands, int(sig_len/bands)))

    pairfinder = pair_finder.build(
        data=df, sig_len=sig_len, bands=bands,
        max_buckets=args.max_buckets, cached=args.use_cache)
    pairfinder.prepare()
    pairfinder.print_stats()
    print("")

    try:
        cmd = getattr(commands, args.cmd)
        print("Running {}".format(args.cmd or "default"))
        print("")
    except:
        print("Command '{}' is not implemented.".format(args.cmd))
        return False

    return cmd(df, pairfinder, args)


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs the MinHash/LSH algorithm to find pairs of similar Netflix users.')
    parser.add_argument('--sig-len', type=int, help='Signature length.')
    parser.add_argument('--rows', type=int, help='Signature rows per band.')
    parser.add_argument('--bands', type=int, help='Number of bands.')
    parser.add_argument('--max-buckets', type=int, default=100000, help='Maximum number of buckets.')
    parser.add_argument('--results', default="results.txt", help='File to store pairs of user IDs in.')
    parser.add_argument('--cmd', default="default", help='Command to run after preparing the algorithm.')

    parser.add_argument('--use-cache', '-c', action='store_true',
                        help='Try to load objects from previous runs, and store them for future runs.')

    parser.add_argument('seed', metavar='random-seed', type=int,
                        help='Seed for the random number generator, set once at start of the program.')
    parser.add_argument('data', help='Path to the data in .npy format.')

    args = parser.parse_args(sys.argv[1:])

    if main(args):
        exit(0)
    else:
        exit(1)
