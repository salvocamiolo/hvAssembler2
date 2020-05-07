# hvAssembler

## Aim
The software aims to deduplicate the reads originated from the hyper variable
genes without providing an assembled genome. This will allow to deduplicate 
genes of different genotypes in the same time. An attempt to assemble new genotypes
is also attempted

## How does it work?
For each hypervariable gene, hvAssembler will align the reads to all the deposited
variants. Each deposited gene is used together with 300 nt down and upstream, which
should be less variable. 

The reads are deduplicated using picard based on the alignment coordinates. 
The alignment is performed with loose parameters and in --local mode. This (together
with the addition of the gene flanking regions) should allow to capture sequences 
that differ markedly from the deposited ones. The deduplicated reads are then assembled
using Spades, thus producing scaffolds that may contain eventual new genotypes.

## How to run it?
hvAssembler uses the following syntax

hvAssembler.py [-h] -1 READ1 -2 READ2 -c CONDA_DIRECTORY
                      [-t NUM_THREADS]  -o OUTPUT_FOLDER
                      
The fastq files for the paired end reads and the output folder must be provided.
Also the Conda_directory is compulsory and you can use that in my home (see example below)
If the number of threads is not specified it will run on 1 thread     

## What will it produce?
In the output folder you will find the following:

deduplicationStatistics.txt

this is a file reporting the number of mapped reads before and after the deduplication,
which should give you an idea of the clonality. In principle it should be similar to that
observed on Merlin, if Maha pipeline uses picard to mark duplicates

reads/

In this folder you will find for each gene the fastq file reporting the deduplicated reads
A concatenated fastq file is also generated, namely all_1.fastq /all_2.fastq. These can
be used to re-run the genotyping with only deduplicated reads

scaffolds/

In this folder you will find a spades assembly for the reads belonging to each hypervariable
gene. Here you may find some new genotype if present. 
        

