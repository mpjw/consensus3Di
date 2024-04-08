# Consensus 3Di feasibility study
This work investigates the feasibility of inferring consensus 3Di information from amino acid sequence.
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

## Test data
As test data we use 500 randomly selected SCOPe entries taken from SCOPe v2.01 at 40% sequence identity.
Of there 2 entries had no sequence annotated in the [corresponding fasta file](https://scop.berkeley.edu/downloads/scopeseq-2.01/astral-scopedom-seqres-gd-sel-gs-bib-40-2.01.fa
).
Thus, we end up with 498 entries, which are stored in `data/test/scope.test.fasta`.
To download the SCOPe v2.01 40% sequence redundancy fasta file used here, please run the command below.
```
wget https://scop.berkeley.edu/downloads/scopeseq-2.01/astral-scopedom-seqres-gd-sel-gs-bib-40-2.01.fa
```
Location on cluster `/home/sukhwan/foldseek-analysis/scope_pdb`.
SCOPe entries with no sequence in 2.01: `'d3n55.1', 'd1sse.1'`

##  Approach
For feasability testing use the `predict_3Di_encoderOnly.py` and `predict_AA_encoderOnly.py` in `ProstT5/scripts/` in concatenation.
Alternatively we use foldseek generated 3Di sequences as starting point.
Infer 3Di sequences using ProstT5 as follows
```bash
python lib/ProstT5/scripts/predict_3Di_encoderOnly.py --input data/test/test.fasta --output out/test/test.output.3Di.fasta --half 1 --model models/test/
```
To generate 3Di sequences from foldseek use
```bash
foldseek createdb structures/* scope.test.db
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

## Temporary notes
Want to compare PSI Blast like foldseek (profile) searches -> are ProstT5 generated 3Di sequences really closer to the family consensus?




