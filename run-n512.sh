#!/bin/bash

pushcode

ssh owl8.uio.no -t "

export DATA=/mn/stornext/d1/dagss
export PATH=/mn/stornext/d1/dagss/opt/epd-7.3.1/bin:$PATH
export PYTHONPATH=~/code/oomatrix:~/code/commander

cd /mn/stornext/d1/dagss/wmap

#OMP_NUM_THREADS=32 python ~/runs/wmap/n512.py

#OMP_NUM_THREADS=32 numactl --membind=0-3 --cpunodebind=0-3 python ~/runs/wmap/n512.py
OMP_NUM_THREADS=32 numactl --membind=4-7 --cpunodebind=4-7 python ~/runs/wmap/n512.py

"
