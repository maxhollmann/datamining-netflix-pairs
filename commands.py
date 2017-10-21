import numpy as np
from datetime import datetime

from csv_writer import CsvWriter


def default(data, pf, args):
    """Evaluates candidates, highest signature similarity first.

    Results are written to the file given by args.results (--results
    option).
    """
    candidates = list(pf.candidates())
    candidates = sorted(candidates, key = lambda c: -c[1])

    csv_file = args.results
    csv = CsvWriter(csv_file, append = False)

    found = 0
    for i, ((c1, c2), sim) in enumerate(candidates):
        if pf.jaccard_similarity(c1, c2) >= .5:
            csv.write([c1 + 1, c2 + 1])
            found += 1
            print("Found {} (at signature similarity {})".format(found, sim), end = '\r')

    return True


def get_candidate_distribution(data, pf, args):
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


def get_jaccard_distribution(data, pf, args):
    """Samples random pairs and saves their Jaccard similarity to CSV.

    The result is used by jaccard_distribution.R to fit an
    distribution to the data.
    """
    csv = CsvWriter("out/jaccard_dist.csv", append = True)
    csv.write_header(['u1', 'u2', 'jac_sim'])

    for i, (u1, u2) in enumerate(zip(np.random.permutation(pf.n_docs),
                                     np.random.permutation(pf.n_docs))):
        if u1 == u2: next
        print("Wrote {} similarities".format(i), end = '\r')
        csv.write([u1, u2, pf.jaccard_similarity(u1, u2)])

    return True