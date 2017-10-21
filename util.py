def calculate_algorithm_params(args):
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
        raise ValueError("You need to specify two of the arguments --sig-len, --rows, and --bands")

    return sig_len, bands
