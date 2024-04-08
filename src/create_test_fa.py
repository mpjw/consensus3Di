#!/usr/bin/python
from Bio import SeqIO

# read test ids from file
test_ids = []
with open("data/test/scope_test_ids", "r") as t:
    test_ids = t.readlines()
 
test_ids = [i.replace(".pdb\n", "") for i in test_ids]

# write protein sequences of test ids to fasta file
out_file = open("data/test/test.fa", "w")
for entry in SeqIO.parse("data/test/astral-scopedom-seqres-gd-sel-gs-bib-40-2.01.fa", format="fasta"):
    if entry.id in test_ids:
        entry.seq = entry.seq.upper()
        print(entry)
        SeqIO.write(entry, out_file, "fasta")


out_file.close()

