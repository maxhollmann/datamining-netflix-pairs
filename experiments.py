import numpy as np
import multiprocessing as mp
from sklearn.model_selection import ParameterGrid
from datetime import datetime
import time
import subprocess
import os
from csv_writer import CsvWriter


csv = CsvWriter("out/experiments.csv", append = True)
csv.write_header(['run_id', 'bands', 'rows', 'max_buckets', 'time', 'count'])


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
    run_id = datetime.now().isoformat()
    results_file = "experiment_{}.txt".format(run_id)

    cmd = [
        "python3", "main.py",
        "--results={}".format(results_file)
    ] + ["--{}".format("=".join([k, str(v)])) for k, v in params.items()] + [
        str(int(np.random.uniform(0, 9999999))), "user_movie.npy"
    ]

    print("Run {}: {}".format(run_id, " ".join(cmd)))

    start_t = time.time()
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        last_count = None
        running = True

        while True:
            elapsed = time.time() - start_t

            count = count_lines_in_file(results_file)
            if count != last_count:
                print("Run {}   Count at {}: {}".format(run_id, elapsed, count))
                csv.write([run_id, params['bands'], params['rows'], params['max-buckets'],
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

        print(proc.returncode)


def main(args):
    grid = list(ParameterGrid({
        'bands': [7, 3, 11, 15, 20, 30, 40],
        'rows' : [7, 3, 11, 15, 20, 30, 40],
        'max-buckets': [5000000],
    }))

    for i in range(10000):
        grid.append({
            'bands': np.random.randint(2, 100),
            'rows': np.random.randint(2, 100),
            'max-buckets': 100000 * np.random.randint(1, 100),
        })

    # sensible limit for sig len
    grid = [p for p in grid if p['bands'] * p['rows'] <= 150]

    print("{} configurations".format(len(grid)))
    print(grid)
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
