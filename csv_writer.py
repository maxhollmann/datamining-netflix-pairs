import csv
import os

from util import ensure_directory


class CsvWriter:
    def __init__(self, filename, append = False, delimiter=","):
        ensure_directory(f=filename)

        # open file in appropriate mode
        mode = 'a' if append else 'w'
        self.appending = append and os.path.exists(filename) and os.path.getsize(filename) > 0
        self.f = open(filename, mode)

        self.writer = csv.writer(self.f, delimiter=delimiter)

    def write_header(self, header):
        if not self.appending:
            self.write(header)

    def write(self, row):
        self.writer.writerow([str(field) for field in row])
        self.f.flush()
