import numpy as np
from scipy import sparse
from collections import defaultdict
import time
import cache
import pickle


class PairFinder:
    """
    MinHash/LSH algorithm to find pairs of similar documents.
    """

    def __init__(self, data, sig_len, bands, max_buckets):
        if sig_len % bands != 0:
            raise Exception("sig_len ({}) must be divisible by bands ({})".format(sig_len, bands))

        self.data = data
        self.docs = self.data.iloc[:, 0]
        self.shingles = self.data.iloc[:, 1]
        self.n_docs = np.max(self.docs) + 1
        self.n_shingles = np.max(self.shingles) + 1
        self.sig_len = sig_len
        self.n_bands = bands
        self.max_buckets = max_buckets

    def prepare(self):
        """Initializes the signature matrix and fills buckets"""
        self._compute_document_shingle_matrix()
        self._compute_signatures()
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
    def _compute_document_shingle_matrix(self):
        # CSC -> 16s for creation, .988s per random row permutation
        # CSR -> 37s for creation, .537s per random row permutation
        print("Computing document-shingle matrix...")
        t = time.time()
        self.DS = sparse.csr_matrix((self.n_shingles + 1, self.n_docs + 1), dtype=np.uint8)
        self.DS[self.shingles, self.docs] = 1
        print("Done in {}s".format(time.time() - t))

    def _compute_signatures(self):
        self.S = np.zeros((self.sig_len, self.n_docs))

        print("Computing signatures...")
        t = time.time()
        for i in range(self.sig_len):
            t2 = time.time()

            # Generate random permutation of rows
            DSp = self.DS[np.random.permutation(self.DS.shape[0]), :]

            # get indices of nonzero elements
            nz_row, nz_col = DSp.nonzero()

            # get index of first nonzero index per column (user)
            _, first_nz_i = np.unique(nz_col, return_index=True)

            # index of first non-zero row per column (next part of S)
            self.S[i, :] = nz_row[first_nz_i]

            print("  {}/{} done in {}s".format(i, self.sig_len, time.time() - t2))

        print("Done in {}s".format(time.time() - t))


    def _fill_buckets(self):
        print("Filling buckets...")
        t = time.time()

        band_len = int(self.sig_len / self.n_bands)
        self.buckets = defaultdict(lambda: set())

        for b in range(self.n_bands):
            t2 = time.time()

            band_idx = slice(b*band_len, b*band_len + band_len)

            for d in range(self.n_docs):
                bucket = hash(tuple(self.S[band_idx, d])) % self.max_buckets
                self.buckets[bucket].add(d)

            print("  Band {}/{} done in {}s".format(b, self.n_bands, time.time() - t2))

        print("Done in {}s".format(time.time() - t))



class CachedPairFinder(PairFinder):
    """
    Subclass of PairFinder that wraps computing intensive methods
    to try loading the results from cache first.
    """

    def _compute_document_shingle_matrix(self):
        cache_file = "cached_docshingle.npz"
        #self.DS = sparse.load_npz(cache_file)
        try:
            self.DS = sparse.load_npz(cache_file)
            print("Using cached document-shingle matrix")
        except:
            super()._compute_document_shingle_matrix()
            sparse.save_npz(open(cache_file, "wb"), self.DS)

    def _compute_signatures(self):
        cache_file = "S_{}".format(self.sig_len)
        try:
            self.S = cache.load(cache_file)
            assert self.S.shape == (self.sig_len, self.n_docs)
            print("Using cached S")
        except:
            super()._compute_signatures()
            cache.save(self.S, cache_file)

    def _fill_buckets(self):
        cache_file = "cached_buckets_{}_{}_{}.pkl".format(
            self.sig_len, self.n_bands, self.max_buckets)
        try:
            self.buckets = pickle.load(open(cache_file, "rb"))
            print("Using cached buckets")
        except:
            super()._fill_buckets()
            pickle.dump(dict(self.buckets), open(cache_file, "wb"))



def build(*args, **kwargs):
    cached = kwargs.get('cached', False)
    del kwargs['cached']

    cls = CachedPairFinder if cached else PairFinder
    return cls(*args, **kwargs)
