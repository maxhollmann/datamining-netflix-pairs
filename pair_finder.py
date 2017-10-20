import numpy as np
from collections import defaultdict
import time
import cache


class PairFinder:
    """
    Algorithm to find pairs of similar documents.
    """

    def __init__(self, document_matrix, sig_len, bands, max_buckets):
        if sig_len % bands != 0:
            raise Exception("sig_len ({}) must be divisible by bands ({})".format(sig_len, bands))

        self.D = document_matrix
        self.sig_len = sig_len
        self.n_bands = bands
        self.max_buckets = max_buckets

    def prepare(self):
        """Initializes the signature matrix and fills buckets"""
        self._compute_S()
        self._fill_buckets()

    def candidates(self):
        """Iterates over all candidates pairs, yielded as tuples of indices"""
        for b in self.buckets.values():
            b = list(b)
            for i in range(len(b)):
                for j in range(i, len(b)):
                    yield (b[i], b[j])

    def sig_sim(self, i, j):
        """Returns the similarity of signatures for documents i and j"""
        return np.sum(self.S[:, i] == self.S[:, j]) / self.sig_len


    ##### Private methods
    def _compute_S(self):
        self.S = np.zeros((self.sig_len, self.D.shape[1]))

        print("Computing S...")
        t = time.time()
        for i in range(self.sig_len):
            t2 = time.time()

            # Generate random permutation of rows
            Dp = self.D[np.random.permutation(self.D.shape[0]), :]

            # get indices of nonzero elements
            nz_row, nz_col = Dp.nonzero()

            # get index of first nonzero index per column (user)
            _, first_nz_i = np.unique(nz_col, return_index=True)

            # index of first non-zero row per column (next part of S)
            self.S[i, :] = nz_row[first_nz_i]

            print("  S[{}, :] done in {}s".format(i, time.time() - t2))

        print("Done in {}s".format(time.time() - t))


    def _fill_buckets(self):
        print("Filling buckets...")
        t = time.time()

        band_len = int(self.sig_len / self.n_bands)
        self.buckets = defaultdict(lambda: set())

        for b in range(self.n_bands):
            print("  Band {}...".format(b))
            t2 = time.time()

            band_idx = range(b*band_len, b*band_len + band_len)

            for d in range(self.S.shape[1]):
                bucket = hash(tuple(self.S[band_idx, d])) % self.max_buckets
                self.buckets[bucket].add(d)

            print("  Done in {}s".format(time.time() - t2))

        print("Done in {}s".format(time.time() - t))



class CachedPairFinder(PairFinder):
    def _compute_S(self):
        try:
            self.S = cache.load("S_{}".format(self.sig_len))
            assert self.S.shape == (self.sig_len, self.D.shape[1])
            print("Using cached S")
        except:
            super()._compute_S()
            cache.save(self.S, "S_{}".format(self.sig_len))



def build(*args, **kwargs):
    cached = kwargs.get('cached', False)
    del kwargs['cached']

    cls = CachedPairFinder if cached else PairFinder
    return cls(*args, **kwargs)
