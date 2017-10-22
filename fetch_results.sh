#!/usr/bin/env bash

scp ec:pairs/out/experiments.csv out/ec_experiments.csv
rsync -r ec:pairs/results ec_results
