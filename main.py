import numpy as np
import time

import data
import pair_finder
from csv_writer import CsvWriter


def main(args):
    np.random.seed(seed=args.seed)
    df = data.load(args.data)

    # Make IDs start at 0 for easier indexing
    df.user = df.user - 1
    df.movie = df.movie - 1


    if args.sig_len is None and args.bands is None and args.rows is None:
        sig_len = 105
        bands = 15
    elif args.sig_len and args.bands:
        sig_len = args.sig_len
        bands = args.bands
    elif args.sig_len and args.rows:
        sig_len = args.sig_len
        bands = int(sig_len / args.rows)
    elif args.rows and args.bands:
        sig_len = args.rows * args.bands
        bands = args.bands
    else:
        raise Exception("You need to specify two of the arguments --sig-len, --rows, and --bands")

    print("Sig len: {}    bands: {}    rows: {}".format(sig_len, bands, int(sig_len/bands)))

    pairfinder = pair_finder.build(
        data=df, sig_len=sig_len, bands=bands,
        max_buckets=args.max_buckets, cached=args.use_cache)
    pairfinder.prepare()

    print("Used {}/{} buckets".format(len(pairfinder.buckets), args.max_buckets))


    can1 = [c for c in pairfinder.candidates()]

    csv = CsvWriter("out/all.csv", append = False)
    csv.write_header(['u1', 'u2', 'sig_sim', 'jac_sim', 'n'])

    lim = 0; step = 1; n_per_step = 10000
    while lim < 1:
        can2 = [(c, sim) for c, sim in can1 if sim >= lim and sim < lim + step]
        n = len(can2)
        print(lim, n)

        for i in np.random.permutation(len(can2))[:n_per_step]:
            (c1, c2), sim = can2[i]
            csv.write([c1, c2, sim, pairfinder.jaccard_similarity(c1, c2), n])

        lim += step


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs the MinHash/LSH algorithm to find pairs of similar Netflix users.')
    parser.add_argument('--sig-len', type=int, help='Signature length.')
    parser.add_argument('--rows', type=int, help='Signature rows per band.')
    parser.add_argument('--bands', type=int, help='Number of bands.')
    parser.add_argument('--max-buckets', type=int, default=100000, help='Maximum number of buckets.')
    parser.add_argument('--results', default="results.txt", help='File to store pairs of user IDs in.')

    parser.add_argument('--use-cache', '-c', action='store_true',
                        help='Try to load objects from previous runs, and store them for future runs.')

    parser.add_argument('seed', metavar='random-seed', type=int,
                        help='Seed for the random number generator, set once at start of the program.')
    parser.add_argument('data', help='Path to the data in .npy format.')

    args = parser.parse_args(sys.argv[1:])

    main(args)
