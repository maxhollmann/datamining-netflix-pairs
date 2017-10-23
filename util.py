import os


def calculate_algorithm_params(args):
    if args.sig_len is None and args.bands is None and args.rows is None:
        sig_len = 132
        bands = 22
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
        raise ValueError("You need to specify none or two of the arguments --sig-len, --rows, and --bands")

    return sig_len, bands


def ensure_directory(d = None, f = None):
    """Create directory if it doesn't exist."""
    if d is None:
        assert f is not None
        d = os.path.dirname(f)

    if d != '' and not os.path.exists(d):
        os.makedirs(d)
