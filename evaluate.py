import numpy as np
import time
import subprocess
import os

import data
from csv_writer import CsvWriter
from util import ensure_directory


"""
This file simulates the evaluation environment and stores results
of the algorithm with default settings.
"""


csv = CsvWriter("diagnostics/out/evaluation.csv", append = True)
csv.write_header(['batch', 'run', 'found', 'incorrect', 'time', 'ppm', 'terminated'])

def jaccard_sim(data, u1, u2):
    m1 = data.movie[data.user == u1]
    m2 = data.movie[data.user == u2]
    return len(np.intersect1d(m1, m2)) / len(np.union1d(m1, m2))


def run_evaluation(batch = 0, runs = 5):
    for run in range(runs):
        cmd = [
            "python3", "main.py",
            str(int(np.random.uniform(0, 9999999))), "user_movie.npy",
        ]

        print("\nRun {}/{}: {}".format(run+1, runs, " ".join(cmd)))


        try: os.remove("results.txt")
        except: pass

        start_t = time.time()
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            running = True
            terminated = False

            while True:
                elapsed = time.time() - start_t
                print("Elapsed time: {}m {}s".format(int(elapsed/60), int(elapsed)%60), end='\r')

                if elapsed >= 1800:
                    print("\nTimeout, terminating!")
                    terminated = True
                    proc.terminate()

                try:
                    proc.communicate(timeout=1)
                    print("\nProcess stopped.")
                    break
                except subprocess.TimeoutExpired:
                    pass


            # Evaluate
            found = 0
            incorrect = 0

            with data.load() as df:
                with open("results.txt") as f:
                    for l in f:
                        u1, u2 = l.split(",")
                        u1, u2 = int(u1), int(u2)
                        if u1 >= u2:
                            incorrect += 1
                        elif jaccard_sim(df, u1, u2) <= 0.5:
                            incorrect += 1
                        else:
                            found += 1

            csv.write([
                batch, run,
                found, incorrect,
                elapsed, found / elapsed * 60,
                terminated
            ])



def main(args):
    for batch in range(args.batches):
        print("Batch {}/{}\n".format(batch+1, args.batches))
        run_evaluation(batch, args.runs)


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Evaluates the default setup.')
    parser.add_argument('--batches', default = 1, type = int)
    parser.add_argument('--runs', default = 5, type = int)
    args = parser.parse_args(sys.argv[1:])

    main(args)
