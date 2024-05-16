#!/bin/bash

## start timing
date 

## foldseek easy-search (combination of all convert2db + prefilter + align)
./lib/foldseek/build/src/foldseek easy-search ./out/dbs/foldseek_recoded/ ./data/dbs/subset_scope/ ./out/benchmark/foldseek/results ./out/benchmark/foldseek/tmp/ --threads 64 -s 9.5 --max-seqs 2000 -e 10

## end timing
date
