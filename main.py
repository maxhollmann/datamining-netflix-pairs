import numpy as np
import time

import data
import pair_finder
from util import calculate_algorithm_params
import commands

""" This file mainly deals with command line arguments and setup of
the data and algorithm. The interesting parts are the algorithm in
pair_finder.py and it being used to write pairs to results.txt in the
default() function in commands.py.

Run `python main.py --help` for options on how to run this file."""


def main(args):
    start_t = time.time()

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

    return args.command(df, pairfinder, args, start_t)


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs the MinHash/LSH algorithm to find pairs of similar Netflix users.')

    ##### Global options
    # Algorithm parameters
    params_group = parser.add_argument_group('params',
                                             'Parameters for the algorithm. '
                                             'Leave all three empty for default settings, otherwise '
                                             'you need to specify exactly two of --sig-len, --rows, and --bands. '
                                             'The third one is calculated from the given two.')
    params_group.add_argument('--sig-len', type=int, help='Signature length.')
    params_group.add_argument('--rows', type=int, help='Signature rows per band.')
    params_group.add_argument('--bands', type=int, help='Number of bands.')
    params_group.add_argument('--max-buckets', type=int, default=2800000, help='Maximum number of buckets.')
    params_group.add_argument('--signature-method', default='minhash',
                              help='Method for generating signatures. '
                              'One of minhash (default) and permutation.')

    parser.add_argument('--use-cache', '-c', action='store_true',
                        help='Try to load objects from previous runs, and store them for future runs.')

    parser.add_argument('seed', metavar='random-seed', type=int,
                        help='Seed for the random number generator, set once at start of the program.')
    parser.add_argument('data', help='Path to the data in .npy format.')


    ##### Subcommands
    command_parsers = parser.add_subparsers(title='command', help='Command to run after preparing the algorithm.')
    cmd_help = lambda func: func.__doc__.split("\n")[0]

    # default command
    parser_default = command_parsers.add_parser('default', help=cmd_help(commands.default))
    parser.set_defaults(command=commands.default)
    parser_default.set_defaults(command=commands.default)
    parser_default.add_argument('--results', default="results.txt",
                                help='File to store pairs of user IDs in.')
    parser_default.add_argument('--extended', action='store_true',
                                help='Store more information than just the user IDs.')

    # candidate-dist command
    parser_candidate_dist = command_parsers.add_parser('candidate-dist',
                                                       help=cmd_help(commands.get_candidate_distribution))
    parser_candidate_dist.set_defaults(command=commands.get_candidate_distribution)
    parser_candidate_dist.add_argument('--results', default="out/candidate_dist.csv",
                                       help='File to store distribution in (CSV).')

    # jaccard-dist command
    parser_jaccard_dist = command_parsers.add_parser('jaccard-dist',
                                                     help=cmd_help(commands.get_jaccard_distribution))
    parser_jaccard_dist.set_defaults(command=commands.get_jaccard_distribution)
    parser_jaccard_dist.add_argument('--results', default="out/jaccard_dist.csv",
                                     help='File to store distribution in (CSV).')

    # console command
    parser_console = command_parsers.add_parser('console',
                                                help=cmd_help(commands.console))
    parser_console.set_defaults(command=commands.console)

    # benchmark command
    parser_benchmark = command_parsers.add_parser('benchmark',
                                                  help=cmd_help(commands.benchmark))
    parser_benchmark.set_defaults(command=commands.benchmark)
    parser_benchmark.add_argument('--run', default="all",
                                  help='Which benchmark to run. Default: all.')

    args = parser.parse_args(sys.argv[1:])


    if main(args):
        exit(0)
    else:
        exit(1)
