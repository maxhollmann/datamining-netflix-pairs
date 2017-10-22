#!/usr/bin/env bash

server=${1:-ec}

rsync  -vr *.py user_movie.npy $server:pairs/
