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
```
git clone git@github.com:mheinzinger/ProstT5.git
```



