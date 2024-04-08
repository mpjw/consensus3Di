#!/usr/bin/python

db_ss_file = "data/test/scope.test.db_ss"
db_source_file = "data/test/scope.test.db.source"
out_fasta = "out/test/scope.foldseek.3Di.fasta"

file_3Di = open(db_ss_file, "r")
file_ids = open(db_source_file, "r")
out_file = open(out_fasta, "w")

for _3di, id in zip(file_3Di, file_ids):
    out_file.write(">" + id.split("\t")[1].strip("\.pdb\n") + "\n" + _3di) 

file_3Di.close()
file_ids.close()
out_file.close()
