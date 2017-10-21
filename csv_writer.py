import csv
import os

class CsvWriter:
    def __init__(self, filename, append = False):
        mode = 'a' if append else 'w'
        self.appending = append and os.path.exists(filename) and os.path.getsize(filename) > 0
        self.f = open(filename, mode)
        self.writer = csv.writer(self.f)

    def write_header(self, header):
        if not self.appending:
            self.write(header)

    def write(self, row):
        self.writer.writerow([str(field) for field in row])
        self.f.flush()
