#!/bin/bash

(cd ~/code/commander && git push -f owl wip/master)
git wip
git push -f owl wip/master
ssh owl8.uio.no -t "

export DATA=/mn/stornext/d1/dagss
export PATH=/mn/stornext/d1/dagss/opt/epd-7.3.1/bin:$PATH
export PYTHONPATH=~/code/oomatrix:~/code/commander

cd ~/code/commander;
git checkout wip/master; 
cd ~/runs/wmap;
git checkout wip/master;

#cd /mn/stornext/d1/dagss/

OMP_NUM_THREADS=16 python ~/runs/wmap/n512.py

"
