import numpy as np
from datetime import datetime
import time

from csv_writer import CsvWriter

"""Commands that can be called from the command line."""


def default(data, pf, args, start_t):
    """Evaluates candidates, highest signature similarity first.

    Results are written to the file given by args.results (--results
    option).
    """

    print("Getting all candidates...")
    t = time.time()
    candidates = list(pf.candidates())
    print("Done in {}s".format(time.time() - t))

    print("Sorting candidates...")
    t = time.time()
    candidates = sorted(candidates, key = lambda c: -c[1])
    print("Done in {}s".format(time.time() - t))

    csv_file = args.results if 'results' in args else 'results.txt'
    csv = CsvWriter(csv_file, append = False)

    print("Verifying candidates...")
    found = 0
    found_times = np.array([])
    for i, ((c1, c2), sim) in enumerate(candidates):
        jac_sim = pf.jaccard_similarity(c1, c2)
        elapsed_t = time.time() - start_t

        if jac_sim >= .5:
            c1, c2 = min(c1, c2) + 1, max(c1, c2) + 1
            if args.extended:
                csv.write([c1, c2, sim, jac_sim, i, elapsed_t])
            else:
                csv.write([c1, c2])
            found += 1
            found_times = np.append(found_times, time.time() - start_t)
            print("Found {} (at signature similarity {}, after {}s)".format(found, sim, elapsed_t), end = '\r')

        # stop when 30 minutes are over
        if elapsed_t > 1800 - 2:
            print("\nTime's up, stopping.")
            break

        # every 1000 candidates, check whether rate is so low we should stop
        if found >= 100 and i % 100 == 0:
            if elapsed_t - found_times[-10] > 60: # less than 10 per minute
                print("\nRate is slowing down, stopping.")
                break

    print("Finished in {}s.".format(elapsed_t))
    print("Found {} pairs, {} per minute.".format(found, found / elapsed_t * 60))


    return True


def console(data, pf, args, start_t):
    """Simply opens a prompt after preparing the algorithm."""
    import code; code.interact(local=dict(globals(), **locals()))
    return True


def get_candidate_distribution(data, pf, args, start_t):
    """Samples pairs from candidates, stratified by signature similarity.

    The result is stored in a CSV, including the signature similarity,
    Jaccard similarity, and weight (> 1 if there were more samples in
    the stratum than max_per_step, to get approximately accurate
    frequencies).
    """
    candidates = list(pf.candidates())

    csv_file = "out/candidate_dist.csv".format(
        pf.n_bands, int(pf.sig_len / pf.n_bands), pf.max_buckets)
    csv = CsvWriter(csv_file, append = True)
    csv.write_header([
        'run_id',
        'u1', 'u2', 'sig_sim', 'jac_sim',
        'sig_len', 'bands', 'max_buckets', 'used_buckets',
        'weight'])

    run_id = datetime.now().isoformat()

    lim = 0; step = 0.05; max_per_step = 100
    while lim < 1:
        cand = [(c, sim) for c, sim in candidates if sim >= lim and sim < lim + step]
        n = len(cand)
        print("{} candidates between {} and {}".format(n, lim, lim+step))

        weight = max(n, max_per_step) / max_per_step
        for i in np.random.permutation(n)[:max_per_step]:
            (c1, c2), sim = cand[i]
            csv.write([
                run_id,
                c1, c2, sim, pf.jaccard_similarity(c1, c2),
                pf.sig_len, pf.n_bands, pf.max_buckets, len(pf.buckets),
                weight])

        lim += step

    return True


def get_jaccard_distribution(data, pf, args, start_t):
    """Samples random pairs and saves their Jaccard similarity to CSV.

    The result is used by jaccard_distribution.R to fit an
    distribution to the data.
    """
    csv = CsvWriter("out/jaccard_dist.csv", append = True)
    csv.write_header(['u1', 'u2', 'jac_sim', 'sig_sim'])

    for i, (u1, u2) in enumerate(zip(np.random.permutation(pf.n_docs),
                                     np.random.permutation(pf.n_docs))):
        if u1 == u2: next
        print("Wrote {} similarities".format(i), end = '\r')
        csv.write([u1, u2, pf.jaccard_similarity(u1, u2), pf.sig_sim(u1, u2)])

    return True


def benchmark(data, pf, args, start_t):
    """Runs benchmarks for different things."""
    print("Setup time: {}s".format(time.time() - start_t))

    run_all = args.run == 'all'

    if run_all or args.run == 'jaccard_similarity':
        i1 = np.random.permutation(pf.n_docs)
        i2 = np.random.permutation(pf.n_docs)

        print("Burn in...")
        for i in range(1000):
            pf.jaccard_similarity(i1[i], i2[i])

        print("Start... ")
        t = time.time()
        for i in range(3000):
            pf.jaccard_similarity(i1[i], i2[i])
        print("Done in {}s".format(time.time() - t))

    return True
