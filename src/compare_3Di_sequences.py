#!/usr/bin/python

# Script to compare sequence similarity between foldseek and ProstT5 generated 3Di sequences
from Bio import SeqIO

foldseek_start_file = "out/scope/scope.foldseek.3Di.fasta"
prostt5_start_file = "out/scope/scope.prostt5.3Di.fasta"
fold_start_file = SeqIO.parse(foldseek_fasta,  "fasta")
prost_start_file = SeqIO.parse(prostt5_fasta, "fasta") 

scope_aa = "data/test/scope.test.AA.fasta"
scope_3di = "data/test/scope.test.3Di.fasta"

scope_aa_file = SeqIO.parse(scope_aa, "fasta") 
scope_3di_file = SeqIO.parse(scope_3di, "fasta") 

foldseek_fasta = "out/scope/foldseek/foldseek3Di.encoderOnlyAA.encoderOnly3Di.fasta"
prostt5_fasta = "out/scope/prostt5/prostt53Di.encoderOnlyAA.encoderOnly3Di.fasta"
similarity_file = 'out/distances.fasta'

fold_file = SeqIO.parse(foldseek_fasta,  "fasta")
prost_file = SeqIO.parse(prostt5_fasta, "fasta") 

# use https://github.com/Victor-Mihaila/Thesis/blob/master/jac_cpu/identity_visualization.ipynb

def hamming_distance(seq1: str, seq2: str) -> int:
    """
    Funciton to compute hamming distance between two DNA strings.
    """
    assert len(seq1) == len(seq1)
    
    # naive approach: count differences
    return len([i for i in range(len(seq1)) if seq1[i] != seq2[i]])

def sequence_identity(seq1: str, seq2: str, method='hamming') -> float:
    """
    Function to calculate sequence identiy.
    """
    assert len(seq1) == len(seq2)

    match method:
        case 'hamming':
            return ( len(seq1) - hamming_distance(seq1, seq2) ) / len(seq1)


# compute sequence identity based on hamming distance for all 3Di sequences
seq_ids = [sequence_identity(fi.seq, pi.seq) for fi, pi in zip(fold_file, prost_file)]









