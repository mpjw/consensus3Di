# Consensus 3Di feasibility study
11th May 2024
@author Marcus Wagner


This project investigates the feasibility of inferring consensus 3Di information from amino acid sequence.
Therefore we compare ProstT5 recoded 3Di sequences to foldseek consensus sequences to clarify of the transformer picks up a family consensus signal.
Recoding means a double inferrence of 3Di to AA to 3Di.
We expect the ProstT5 bias towards certain letters (particularly D, V and P) to be a potential issue.
The goal is to improve ProstT5 protein family consnesus predictions.

## Setup
The required software for this project can be installed with conda using the following commands
```bash
conda create -n prostt5 -c conda-forge python=3.10
conda activate prostt5
pip install torch transformers sentencepiece
```

Required [ProstT5](https://github.com/mheinzinger/ProstT5) software must be cloned from github.
```bash
mkdir -p lib/ProtstT5
git clone git@github.com:mheinzinger/ProstT5.git lib/ProtstT5
```
Additionally, the foldseek [benchmarking script](https://github.com/steineggerlab/foldseek-analysis/blob/main/scopbenchmark/scripts/runFoldseek.sh) is needed.
```bash
git clone git@github.com:steineggerlab/foldseek-analysis.git lib/foldseek-analysis
```

## Test data
As test data we use 500 randomly selected SCOPe entries taken from SCOPe v2.01 at 40% sequence identity.
Of there 2 entries had no sequence annotated in the [corresponding fasta file](https://scop.berkeley.edu/downloads/scopeseq-2.01/astral-scopedom-seqres-gd-sel-gs-bib-40-2.01.fa
).
Thus, we end up with 498 entries, which are stored in `data/test/scope.test.fasta`.
To download the SCOPe v2.01 40% sequence redundancy fasta file used here, please run the command below.
```bash
wget https://scop.berkeley.edu/downloads/scopeseq-2.01/astral-scopedom-seqres-gd-sel-gs-bib-40-2.01.fa
```
Location on cluster `/home/sukhwan/foldseek-analysis/scope_pdb`.
SCOPe entries with no sequence in 2.01: `'d3n55.1', 'd1sse.1'`

### foldseek database
First, create a foldseek database for the whole of SCOPe 20.1 40%
Compile foldseek databases on the full SCOPe v2.01 and the 498 subsequences

```bash
# create foldseek database on full SCOPe 2.01
mkdir -p data/dbs/scope_full
foldseek createdb --mask-bfactor-threshold -10000 data/structures/full_scope_pdb scope_full/scope_full

# create subset database from SCOPe
mkdir -p data/dbs/subset_scope
foldseek createdb --mask-bfactor-threshold -10000 data/structures/subsset_scope_pdb subset_scope/subset_scope
```

In order to create test data fasta files, use foldseeks `convert2fasta` utility.
First create a fasta file of amino acid sequences for the SCOPe subset database.
```bash
foldseek convert2fasta data/dbs/subset_scope/subset_scope data/dbs/subset_scope.AA.fasta
```
Next, generate 3Di sequences from foldseek and compile a fasta for these.
```bash
foldseek lndb data/dbs/subset_scope/subset_scope.db_h data/dbs/subset_scope/subset_scope.db_ss_h
foldseek convert2fasta data/dbs/subset_scope/subset_scope.db_ss data/dbs/subset_scope.3Di.fasta
```

##  Approach
For feasability testing use the `predict_3Di_encoderOnly.py` and `predict_AA_encoderOnly.py` in `ProstT5/scripts/` in concatenation.
Alternatively we use foldseek generated 3Di sequences as starting point.
Infer 3Di sequences using ProstT5 as follows
```bash
python lib/ProstT5/scripts/predict_3Di_encoderOnly.py --input data/test/test.fasta --output out/test/test.output.3Di.fasta --half 1 --model models/test/
```
The idea bind this is basically, if ProstT5 learns a family consensus component, this should be reflected in a 3Di to AA to 3Di inferrence concatenation.
Herein, the 3Di to AA step should detect a family consensus of aminoacids for such 3Di structure.
Afterwards, the AA to 3Di step is used to generate the 3Di family consensus from AA family consensus.
Lastly, we want to compare the family consensus deteted by ProtstT5 to the profile search results from foldseek.

### 3Di to AA
From the two different 3Di input files, we can either use the `translate.py` file which includes running the decoder or `predict_AA_encoderOnly.py`.
```bash
python lib/ProstT5/scripts/translate.py --input out/test/scope.foldseek.3Di.fasta --output /path/to/output_directory --half 1 --is_3Di 1
```
```bash
python lib/ProstT5/scripts/predict_AA_encoderOnly.py --input out/test/scope.foldseek.3Di.fasta --output out/test/test.output.3Di.fasta --half 1 --model models/test/
```

### Foldseek 3Di profile computation
To compare the 3Di sequences predicted by ProstT5 double prediction, we use foldseek 3Di sequence profiles.
Now run two searches one with one iteration and one with two.
```bash
foldseek search subset_scope scope_full res_it_1 tmp1
# two iterations
foldseek search subset_scope scope_full res_it_2 tmp2 --num-iterations 2
```
Next, we need to compute a 3Di profile from the search results
```bash
foldseek result2profile subset_scope_ss scope_full_ss result_it_2 profile_it_2
```
With this we can compute consensus sequences.
```bash
foldseek profile2consensus profile_it_2 cons_db
```
Now, link the full database header file to the concensus_db folder
```bash
foldseek lndb path/to/scope.full_h path/to/consenesus_db_h
```

Finally, compile a fasta file from the consensus database.
```bash
foldseek convert2fasta cons_db cons.fasta
```

## Comparison
The comparison of 3Di sequences used mainly sequence identity and a 3Di substitution matrix based comparison.
Results show that all 3Di sequences recoded from a ProstT5 3Di inferred baseline show very low sequence identity with foldseek consensus.
![foldseek consensus ProstT5](out/foldseek_consensus.prostt5.3Di.seq_identity.hist.png)
Results recoded from folseek baseline look more promising but still somewhat scattery.
![foldseek consensus scatter](out/baseline_seq_ident.fsk_pt5_seq_ident.point.png)

Reason for this seems to be the 3Di letter bias of ProstT5, which amplifies significantly over three inferrences.
![ProstT5 recoding 3Di distritbution](out/pt5_pt5.3Di.bar.png)
![foldseek recoding 3Di distribution](out/fsk_pt5.3Di.bar.png)
![ProstT5 baseline 3Di histribution](out/pt5_base.3Di.bar.png)
![foldseek baseline 3Di distribution](out/foldseek_baseline.3Di.bar.png)


## Foldseek benchmark recomputation with 3Di consensus
### Build foldseek db from ProstT5 3Di predictions
Im order to create a foldseek database with the ProstT5 recoded 3Di sequences use `generate_foldseek_db.py`.
```bash
python lib/ProstT5/scripts/generate_foldseek_db.py data/subset_scope.AA.fasta out/scope/foldseek/foldseek3Di.recoded.3Di.fasta out/dbs/foldseek_recoded/subset_scope_recoded
```
Next link the lookup file of the SCOPe subset database
```bash
ln data/dbs/subset_scope/subset_scope.lookup out/dbs/foldseek_recoded/subset_scope_recoded.lookup
```
### Paper benchmark
Next we use the ProstT5 recoded 3Di sequences from foldseek baseline 3Di for recompiling the [foldseek papaer](https://doi.org/10.1038/s41587-023-01773-0) benchmark. 
Therefore we initially need the [SCOPe](https://wwwuser.gwdg.de/~compbiol/foldseek/scop40pdb.tar.gz) 40% sequence redundance database.
This data can be found on hulk at ´/path/to/scope´
```bash
# cloning and compiling foldseek
git clone git@github.com:steineggerlab/foldseek.git lib/foldseek
mkdir lib/foldseek/build
cd lib/foldseek/build
# required conda packages: c-compiler cxx-compiler rust cmake
cmake ..
make -j
```
Now we can run the foldseek benchmark
```bash
# fist get a cluster node
srun -c 64 -t 1-0 --pty /bin/bash

./lib/foldseek/build/src/foldseek search ./out/dbs/foldseek_recoded/subset_scope_recoded ./data/dbs/subset_scope_no_ca/subset_scope ./out/benchmark/foldseek/results ./out/benchmark/foldseek/tmp/ --threads 64 -s 9.5 --max-seqs 2000 -e 10

./lib/foldseek/build/src/foldseek convertalis ./out/dbs/foldseek_recoded/subset_scope_recoded ./data/dbs/subset_scope_no_ca/subset_scope ./out/benchmark/foldseek/results ./out/benchmark/foldseek/alignment.ma

# run foldseek benchmark and pipe std out
./src/benchmark_foldseek.sh > log/foldseek.benchmark.log
```
Next evaluate the benchmark using the `scopbenchmark/scripts/bench.noselfhit.awk` script in the `foldseek-analysis` repository.
```bash
lib/foldseek-analysis/scopbenchmark/scripts/bench.noselfhit.awk lib/foldseek-analysis/scopbenchmark/data/scop_lookup.fix.tsv <(cat out/benchmark/foldseek/alignment.ma | sed -E 's|.pdb||g') > out/benchmark/foldseek.rocx
awk '{ famsum+=$3; supfamsum+=$4; foldsum+=$5}END{print famsum/NR,supfamsum/NR,foldsum/NR}' out/benchmark/foldseek.rocx
# 0.00183202 0.00117703 0.000271187
```

Now repeat the same process for the unmodified foldseek database for the subset SCOPe database.
```bash
mkdir out/benchmark/foldseek/baseline_iter2
./lib/foldseek/build/src/foldseek search ./data/dbs/subset_scope_no_ca/subset_scope ./data/dbs/subset_scope_no_ca/subset_scope ./out/benchmark/foldseek/baseline_iter2/scope_subset ./out/benchmark/foldseek/tmp_baseline/ --threads 64 -s 9.5 --max-seqs 2000 -e 10 --num-iterations 2
./lib/foldseek/build/src/foldseek convertalis data/dbs/subset_scope_no_ca/subset_scope ./data/dbs/subset_scope_no_ca/subset_scope ./out/benchmark/foldseek/baseline_iter2/scope_subset ./out/benchmark/foldseek/baseline_aln.ma
lib/foldseek-analysis/scopbenchmark/scripts/bench.noselfhit.awk lib/foldseek-analysis/scopbenchmark/data/scop_lookup.fix.tsv <(cat out/benchmark/foldseek/baseline_aln.ma | sed -E 's|.pdb||g') > out/benchmark/baseline.rocx
awk '{ famsum+=$3; supfamsum+=$4; foldsum+=$5}END{print famsum/NR,supfamsum/NR,foldsum/NR}' out/benchmark/baseline.rocx
# 0.00203293 0.00147389 0.00036441
```

Benchmarking full scope structures
```bash
# old command generating foldseekaln which compiled correct benchmark statistics
# 1058  2024/05/20 15:41:38 lib/foldseek/build/src/foldseek easy-search data/structures/full_scope_pdb/ data/structures/full_scope_pdb/ out/benchmark/foldseek/scope_full/foldseekaln out/benchmark/foldseek/tmp/ --threads 64 -s 9.5 --max-seqs 2000 -e 10
# mpjw@hulk:consensus3Di(main)$ ll out/benchmark/foldseek/scope_full/foldseekaln
# -rw-rw-r-- 1 mpjw mpjw 284M May 20 15:43 out/benchmark/foldseek/scope_full/foldseekaln

mkdir out/benchmark/foldseek/scope_full
foldseek easy-search data/structures/full_scope_pdb/ data/structures/full_scope_pdb/ out/benchmark/foldseek/scope_full/scope_full.ma out/benchmark/foldseek/tmp2/ --threads 64 -s 9.5 --max-seqs 2000 -e 10
lib/foldseek-analysis/scopbenchmark/scripts/bench.noselfhit.awk lib/foldseek-analysis/scopbenchmark/data/scop_lookup.fix.tsv <(cat out/benchmark/foldseek/scope_full/scope_full.ma) > out/benchmark/scope_full.rocx
awk '{ famsum+=$3; supfamsum+=$4; foldsum+=$5}END{print famsum/NR,supfamsum/NR,foldsum/NR}' out/benchmark/scope_full.rocx
# 0.861651 0.48617 0.105976

```

### Plotting benchmark results
First we need to prepare plotting data from `.rocx` file.

## ProstT5 recoding of whole SCOPe set
Benchmark results from the subset show wierd perfomance statistics.
Thus, we compile the benchmark with 3Di for the whole SCOPe data.
```bash
# get the 3Di fasta file from the database
foldseek lndb data/dbs/scope_full/scope_full_h data/dbs/scope_full/scope_full_ss_h
foldseek convert2fasta data/dbs/scope_full/scope_full_ss data/scope.3Di.fasta

# next recode 3Di sequences with ProstT5
python lib/ProstT5/scripts/predict_AA_encoderOnly.py --input data/scope.3Di.fasta --output out/prostt5/scope.recoded.AA.fasta --half 1 --model model/test/
python lib/ProstT5/scripts/predict_3Di_encoderOnly.py --input out/prostt5/scope.recoded.AA.fasta --output out/prostt5/scope.foldseek3Di.recoded.3Di.fasta --half 1 --model model/test/

# generate foldseek database
python lib/ProstT5/scripts/generate_foldseek_db.py data/scope.AA.fasta out/prostt5/scope.foldseek3Di.recoded.3Di.fasta out/dbs/scope_recoded/scope_recoded

ln data/dbs/scope_full/scope_full.lookup out/dbs/scope_recoded/scope_recoded.lookup

# benchmarking
srun -c 64 -t 1-0 --pty /bin/bash
./lib/foldseek/build/src/foldseek search ./out/dbs/scope_recoded/scope_recoded ./data/dbs/scope_full_no_ca/scope_full ./out/benchmark/foldseek/scope_full/results ./out/benchmark/foldseek/scope_full/tmp/ --threads 64 -s 9.5 --max-seqs 2000 -e 10

./lib/foldseek/build/src/foldseek convertalis ./out/dbs/scope_recoded/scope_recoded ./data/dbs/scope_full_no_ca/scope_full ./out/benchmark/foldseek/scope_full/results ./out/benchmark/foldseek/scope_full/alignment.ma

lib/foldseek-analysis/scopbenchmark/scripts/bench.noselfhit.awk lib/foldseek-analysis/scopbenchmark/data/scop_lookup.fix.tsv <(cat out/benchmark/foldseek/scope_full/alignment.ma | sed -E 's|.pdb||g') > out/benchmark/scope_full.recoded.rocx

awk '{ famsum+=$3; supfamsum+=$4; foldsum+=$5}END{print famsum/NR,supfamsum/NR,foldsum/NR}' out/benchmark/scope_full.recoded.rocx
# 0 0 0
```
Same result for using a search with two iterations search
```bash
./lib/foldseek/build/src/foldseek search ./out/dbs/scope_recoded/scope_recoded ./data/dbs/scope_full_no_ca/scope_full ./out/benchmark/foldseek/scope_full/iter2/results ./out/benchmark/foldseek/scope_full/tmp/ --threads 64 -s 9.5 --max-seqs 2000 -e 10 --num-iterations 2 > 20240522.foldseek.cope_full.bench.iter2.log

./lib/foldseek/build/src/foldseek convertalis ./out/dbs/scope_recoded/scope_recoded ./data/dbs/scope_full_no_ca/scope_full ./out/benchmark/foldseek/scope_full/iter2/results ./out/benchmark/foldseek/scope_full/alignment.iter2.ma

lib/foldseek-analysis/scopbenchmark/scripts/bench.noselfhit.awk lib/foldseek-analysis/scopbenchmark/data/scop_lookup.fix.tsv <(cat out/benchmark/foldseek/scope_full/alignment.iter2.ma) > out/benchmark/scope_full.recoded.iter2.rocx

awk '{ famsum+=$3; supfamsum+=$4; foldsum+=$5}END{print famsum/NR,supfamsum/NR,foldsum/NR}' out/benchmark/scope_full.recoded.iter2.rocx
# 0 0 0
```

## Validating the hypothesis
The hypothesis from Victors work was that structural comparison is more sensitive when generating 3Di sturcture information from AA information using ProstT5 (encoder only), compared to foldseek generated 3Di data, if disregarding c_alpha information for foldseek.
(And also for supplying extra c_alpha informsation)

Therefore, we first infer 3Di structers using the encoder only ProstT5.
```bash
# predict 3Di structures using encoder only from ProstT5
# srun -p gpu --gres=gpu:1 -c 4 -t 1-0 --pty /bin/bash
python lib/ProstT5/scripts/predict_3Di_encoderOnly.py --input data/scope.AA.fasta --output out/prostt5/scope.prostt5.3Di.fasta --half 1 --model model/test/

# create foldseek database from ProstT5 3Di structures
python lib/ProstT5/scripts/generate_foldseek_db.py data/scope.AA.fasta out/prostt5/scope.prostt5.3Di.fasta out/dbs/prostt5_scope/prostt5_scope | tee log/$(date +%Y%m%d).scope_full.prostt5.3Di.generate_foldseek_db.log
ln data/dbs/scope_full/scope_full.lookup out/dbs/prostt5_scope/prostt5_scope.lookup

# benchmarking
# srun -c 64 -t 1-0 --pty /bin/bash
mkdir -p out/benchmark/foldseek/prostt5_scope/tmp
./lib/foldseek/build/src/foldseek search ./out/dbs/prostt5_scope/prostt5_scope ./data/dbs/scope_full_no_ca/scope_full ./out/benchmark/foldseek/prostt5_scope/pt5_scope_bench ./out/benchmark/foldseek/prostt5_scope/tmp/ --threads 64 -s 9.5 --max-seqs 2000 -e 10 | tee log/$(date +%Y%m%d).pt5_scope_benchmark.log

./lib/foldseek/build/src/foldseek convertalis ./out/dbs/prostt5_scope/prostt5_scope ./data/dbs/scope_full_no_ca/scope_full ./out/benchmark/foldseek/prostt5_scope/pt5_scope_bench ./out/benchmark/foldseek/prostt5_scope/alignment.ma | tee log/$(date +%Y%m%d).pt5_scope_benchmark.convertalis.log

lib/foldseek-analysis/scopbenchmark/scripts/bench.noselfhit.awk lib/foldseek-analysis/scopbenchmark/data/scop_lookup.fix.tsv <(cat out/benchmark/foldseek/prostt5_scope/alignment.ma | sed -E 's|.pdb||g') > out/benchmark/scope_full.prostt5.3Di.rocx

awk '{ famsum+=$3; supfamsum+=$4; foldsum+=$5}END{print famsum/NR,supfamsum/NR,foldsum/NR}' out/benchmark/scope_full.prostt5.3Di.rocx | tee out/$(date +%Y%m%d).scope_full.prostt5_3Di.foldseek_benchmark.txt
# 0.841136 0.444706 0.0848822
```


## Temporary notes
Want to compare PSI Blast like foldseek (profile) searches -> are ProstT5 generated 3Di sequences really closer to the family consensus?

Questions
- execute foldseek benchmarking from `/home/sukhwan/foldseek-analysis/`


