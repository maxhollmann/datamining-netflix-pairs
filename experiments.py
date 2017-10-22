import numpy as np
import multiprocessing as mp
from sklearn.model_selection import ParameterGrid
from datetime import datetime
import time
import subprocess
import os

from csv_writer import CsvWriter
from util import ensure_directory


csv = CsvWriter("out/experiments.csv", append = True)
csv.write_header(['batch_id', 'run_id', 'bands', 'rows', 'max_buckets', 'time', 'count'])

batch_id = datetime.now().isoformat()


def count_lines_in_file(filename):
    if not os.path.exists(filename):
        return 0

    count = 0
    with open(filename) as f:
        for l in f:
            if l.strip() != '':
                count += 1
    return count


def perform(params):
    ensure_directory('logs')

    run_id = datetime.now().isoformat()
    results_file = "results/experiment_{}.csv".format(run_id)
    stdout_file = open("logs/experiment_{}_stdout".format(run_id), "w")
    stderr_file = open("logs/experiment_{}_stderr".format(run_id), "w")

    cmd = [
        #"ulimit", "-Sv", "8000000000",
        "python3", "main.py",
    ] + ["--{}".format("=".join([k, str(v)])) for k, v in params.items()] + [
        str(int(np.random.uniform(0, 9999999))), "user_movie.npy",
        "default",
        "--extended",
        "--results", results_file,
    ]

    print("Run {}: {}".format(run_id, " ".join(cmd)))

    start_t = time.time()
    with subprocess.Popen(cmd, stdout=stdout_file, stderr=stderr_file) as proc:
        last_count = None
        running = True

        while True:
            elapsed = time.time() - start_t

            count = count_lines_in_file(results_file)
            if count != last_count:
                print("Run {}   Count at {}s: {}".format(run_id, int(elapsed), count))
                csv.write([batch_id, run_id,
                           params['bands'], params['rows'], params['max-buckets'],
                           elapsed, count])
                last_count = count

            if elapsed > 1805:
                proc.terminate()
            elif elapsed > 1800:
                proc.kill()

            try:
                proc.communicate(timeout=1)
                break
            except subprocess.TimeoutExpired:
                pass

            stdout_file.flush(); stderr_file.flush()


def main(args):
    grid = list(ParameterGrid({
        'bands': [18, 19, 20, 21, 22, 23, 24, 25, 26],
        'rows' : [6],
        'max-buckets': [5000000],
    })) * 40
    # grid = []

    # candidates = [
    #     {'bands': 30, 'rows': 6, 'max-buckets': 2800000},
    #     {'bands': 27, 'rows': 6, 'max-buckets': 2800000},
    #     {'bands': 32, 'rows': 7, 'max-buckets': 2800000},
    # ]
    # for i in range(1000):
    #     # grid += candidates
    #     grid.append({
    #         'bands': np.random.randint(3, 35),
    #         'rows': np.random.randint(3, 35),
    #         'max-buckets': 2800000,
    #     })

    # sensible limit for sig len
    grid = [p for p in grid if p['bands'] * p['rows'] <= 350]

    print("{} configurations".format(len(grid)))
    print("Starting {} workers".format(args.jobs))
    print("")

    with mp.Pool(processes = args.jobs) as pool:
        pool.map(perform, grid)


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Runs experiments.')
    parser.add_argument('--jobs', '-j', default = 1, type = int)
    args = parser.parse_args(sys.argv[1:])

    main(args)
