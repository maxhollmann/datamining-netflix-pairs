import numpy as np
from scipy import sparse
from collections import defaultdict
import time
import pickle

from util import ensure_directory


"""Pair-finder algorithm using min-hashing and location sensitive hashing.

Args:
    data (pandas.DataFrame): Data frame with two columns (document_ids,
        shingle_ids).
    sig_len (int): Number of hashes per signature.
    bands (int): Number of signature segments.
    max_buckets (int): Maximum number of buckets. Should be high enough
        to prevent collisions.
    signature_method (string): Method of generating signatures. Can be
        'minhash' or 'permutation'.
    use_sparse (bool): Whether to use a sparse or dense document-shingle
        matrix. Dense consumes more memory, but makes computing Jaccard-
        similarities many orders of magnitude faster.

    sig_len must be divisible by bands.
"""


class PairFinder:
    """MinHash/LSH algorithm to find pairs of similar documents."""

    def __init__(self, data, sig_len, bands, max_buckets,
                 signature_method='minhash', use_sparse=False):
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
        self.signature_method = signature_method
        self.sparse_ds = use_sparse

        if self.signature_method == 'permutation' and !self.sparse_ds:
            raise RuntimeError("Permutation is only supported with a sparse matrix.")

    def prepare(self):
        """Initialize everything that's required."""
        self._compute_document_shingle_matrix()
        self._compute_signatures()
        self._fill_buckets()

    def candidates(self):
        """Yields all candidate pairs and the similarity of their signatures.

        This will filter out duplicate pairs (from different buckets)
        and return the smaller document IDs first.

        Yields:
            tuple: ((c1, c2), similarity)
        """
        done = set()

        for b in self.buckets.values():
            b = list(b)
            for i in range(len(b)):
                for j in range(i + 1, len(b)):
                    c1, c2 = min(b[i], b[j]), max(b[i], b[j])
                    c = (c1, c2)
                    if c not in done:
                        done.add(c)
                        sim = self.sig_sim(c1, c2)
                        yield ((c1, c2), sim)

    def count_candidates(self):
        """Returns the number of candidate pairs without iterating over all of them.

        This is an estimate an can overestimate the true value quite a
        bit, due to duplicates.
        """
        return int(np.sum([
            n * (n - 1) / 2
            for n in [len(b) for b in self.buckets.values()]
        ]))

    def sig_sim(self, i, j):
        """Returns the similarity of signatures for documents i and j."""
        return np.mean(self.S[:, i] == self.S[:, j])

    def jaccard_similarity(self, i, j):
        """Returns the Jaccard similarity of documents i and j from the document-shingle matrix."""
        if self.sparse_ds:
            d1 = self.DS[:, i].toarray()
            d2 = self.DS[:, j].toarray()
        else:
            d1 = self.DS[:, i]
            d2 = self.DS[:, j]
        return np.logical_and(d1, d2).sum() / np.logical_or(d1, d2).sum()


    def print_stats(self):
        """Prints useful stats for model diagnostics."""
        print("Used {}/{} buckets".format(len(self.buckets), self.max_buckets))
        print("{} candidate pairs".format(self.count_candidates()))



    ##### Private methods

    def _compute_document_shingle_matrix(self):
        # CSC -> 16s for creation, .988s per random row permutation
        # CSR -> 37s for creation, .537s per random row permutation
        print("Computing document-shingle matrix...")
        t = time.time()
        if self.sparse_ds:
            self.DS = sparse.csr_matrix((self.n_shingles + 1, self.n_docs + 1), dtype=np.uint8)
        else:
            self.DS = np.zeros((self.n_shingles + 1, self.n_docs + 1), dtype=np.uint8)
        self.DS[self.shingles, self.docs] = 1
        print("Done in {}s".format(time.time() - t))

    def _compute_signatures(self):
        # 12.7523s * siglen
        print("Computing signatures using {}...".format(self.signature_method))
        t = time.time()

        if self.signature_method == 'minhash':
            self._compute_signatures_minhash()
        elif self.signature_method == 'permutation':
            self._compute_signatures_permutation()
        else:
            raise ValueError("'{}' is not a signature method.".format(self.signature_method))

        print("Done in {}s".format(time.time() - t))

    def _compute_signatures_minhash(self):
        """Creates document signatures using min-hashing."""
        # Generate sig_len hashfunctions (hash(x) = (a*x + b) % prime)
        prime = 17783 # prime number > number of shingles
        a = np.random.choice(self.n_shingles, size=self.sig_len, replace=False)
        b = np.random.choice(self.n_shingles, size=self.sig_len, replace=False)
        b.shape = (self.sig_len, 1)

        self.S = np.full((self.sig_len, self.n_docs), prime)

        if self.sparse_ds:
            csr = self.DS
        else:
            csr = sparse.csr_matrix(self.DS, dtype=np.uint8)

        for r in range(self.n_shingles): # row r
            if r % 100 == 0:
                print("{}% done".format(int(r / self.n_shingles * 100)), end = '\r')

            _, docs = np.nonzero(csr[r, :])
            h = np.add(np.outer(a, r), b) % prime
            self.S[:, docs] = np.minimum(self.S[:, docs], h)

    def _compute_signatures_permutation(self):
        """Creates document signatures using random row permutations.

        Not supported when using a dense document-shingle matrix.
        """
        self.S = np.zeros((self.sig_len, self.n_docs))

        for i in range(self.sig_len):
            # Generate random permutation of rows
            DSp = self.DS[np.random.permutation(self.DS.shape[0]), :]

            # get indices of nonzero elements
            nz_row, nz_col = DSp.nonzero()

            # get index of first nonzero index per column (user)
            _, first_nz_i = np.unique(nz_col, return_index=True)

            # index of first non-zero row per column (next part of S)
            self.S[i, :] = nz_row[first_nz_i]

            print("  {}/{} done in {}s".format(i+1, self.sig_len, time.time() - t), end = '\r')


    def _fill_buckets(self):
        print("Filling buckets...")
        t = time.time()

        band_len = int(self.sig_len / self.n_bands)
        self.buckets = defaultdict(lambda: set())

        for b in range(self.n_bands):
            band_idx = slice(b*band_len, b*band_len + band_len)

            for d in range(self.n_docs):
                bucket = hash(tuple(self.S[band_idx, d])) % self.max_buckets
                self.buckets[bucket].add(d)

            print("  {}/{} done in {}s".format(b+1, self.n_bands, time.time() - t), end = '\r')

        print("Done in {}s".format(time.time() - t))




class CachedPairFinder(PairFinder):
    """Cached version of PairFinder.

    This class wraps computing intensive methods to try loading the
    results from cache first.

    If no cache is found, the computation is done by PairFinder and
    the result saved for the next run.
    """

    def _compute_document_shingle_matrix(self):
        cache_file = "cache/docshingle.npz"
        #self.DS = sparse.load_npz(cache_file)
        try:
            self.DS = sparse.load_npz(cache_file)
            print("Using cached document-shingle matrix")
        except:
            super()._compute_document_shingle_matrix()
            sparse.save_npz(open(cache_file, "wb"), self.DS)

    def _compute_signatures(self):
        cache_file = "cache/signature_{}_{}.npy".format(self.sig_len, self.signature_method)
        try:
            self.S = np.load(cache_file)
            assert self.S.shape == (self.sig_len, self.n_docs)
            print("Using cached signatures")
        except:
            super()._compute_signatures()
            np.save(open(cache_file, "wb"), self.S)

    def _fill_buckets(self):
        cache_file = "cache/buckets_{}_{}_{}.pkl".format(
            self.sig_len, self.n_bands, self.max_buckets)
        try:
            self.buckets = pickle.load(open(cache_file, "rb"))
            print("Using cached buckets")
        except:
            super()._fill_buckets()
            pickle.dump(dict(self.buckets), open(cache_file, "wb"))



def build(*args, **kwargs):
    """Builds either PairFinder or CachedPairFinder.

    Args:
        cached (bool, optional): When true, builds a CachedPairFinder. Defaults to False.
        All other arguments are forwarded to the constructor of the class being built.
    """
    cached = kwargs.get('cached', False)
    del kwargs['cached']

    if cached:
        ensure_directory('cache')

    cls = CachedPairFinder if cached else PairFinder
    return cls(*args, **kwargs)
