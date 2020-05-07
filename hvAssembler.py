import os,sys
import argparse

parser = argparse.ArgumentParser(description="Deduplicate reads for hypervariable genes")
parser.add_argument("-1", "--read1", type=str, required=True, help="Path to the fastq file 1")
parser.add_argument("-2", "--read2", type=str, required=True, help="Path to the fastq file 2")
parser.add_argument("-c","--conda_directory",type=str, required=True,help="Path to the conda 3 environment")
parser.add_argument("-t","--num_threads",type=str, required=False,help="number of threads")
parser.add_argument("-s","--savage_folder",type=str, required=True,help="Savage executable folder")
parser.add_argument("-o","--output_folder",type=str, required=True,help="The name of the output folder")
args = vars(parser.parse_args())
condaDir = args['conda_directory']
read1 = args['read1']
read2 = args['read2']
outputFolder = args['output_folder']
if not args['num_threads']:
	threads = 1
else:
	threads = args['num_threads']


hvg = ['RL12','RL13','RL5A','RL6','UL11','UL120','UL139','UL146','UL1','UL20','UL73','UL74','UL9']
os.system("mkdir -p "+outputFolder+"./reads")
os.system("mkdir -p "+outputFolder+"./scaffolds")

for gene in hvg:
	print("Indexing reference for gene %s" %gene)
	os.system(condaDir+"/bin/bowtie2-build -q ./elongedCDS/"+gene+"_elongedCDS.fasta reference > null 2>&1")
	print("Aligning reads to reference....")
	os.system(condaDir+"/bin/bowtie2 --very-sensitive-local -1 "+read1+" -2 "+read2+" -x reference -S alignment.sam -p "+threads+" > null 2>&1")
	print("Coverting sam to bam....")
	os.system(condaDir+"/bin/samtools view -h -bS alignment.sam > alignment.bam")
	print("Collecting first mapped reads....")
	os.system(condaDir+"/bin/samtools view -h -b -F 4 -f 8 alignment.bam > firstMapped.bam")
	print("Collecting second mapped reads....")
	os.system(condaDir+"/bin/samtools view -h -b -F 8 -f 4 alignment.bam > secondMapped.bam")
	print("Collecting both mapped reads....")
	os.system(condaDir+"/bin/samtools view -h -b -F12 alignment.bam > bothMapped.bam")
	print("Merging alignments....")
	os.system(condaDir+"/bin/samtools merge -f merged.bam firstMapped.bam secondMapped.bam bothMapped.bam")
	print("Calculating number of original reads....")
	os.system(condaDir+"/bin/samtools view merged.bam | wc -l >readCount")
	infile = open("readCount")
	beforeDedupReads = int(infile.readline().rstrip())
	infile.close()
	print("Picard add groups....")
	os.system(condaDir+"/bin/picard AddOrReplaceReadGroups I=merged.bam O=rg_added_sorted.bam SO=coordinate RGID=id RGLB=library RGPL=Ilumina RGPU=machine RGSM=Consensus >null 2>&1")
	print("Picard mark duplicates....")
	os.system(condaDir+"/bin/picard MarkDuplicates I=rg_added_sorted.bam O=dedupped.bam  CREATE_INDEX=true VALIDATION_STRINGENCY=SILENT M=output.metrics >null 2>&1")
	print("Discarding reads with duplicates....")
	os.system(condaDir+"/bin/samtools view -h -b -F 1024 dedupped.bam > alignment_removedDup.bam")
	print("Calculating number of deduplicated reads....")
	os.system(condaDir+"/bin/samtools view alignment_removedDup.bam | wc -l >readCount")
	infile = open("readCount")
	afterDedupReads = int(infile.readline().rstrip())
	infile.close()
	print("Extracting reads....")
	os.system(condaDir+"/bin/bam2fastq  -o read#.fq alignment_removedDup.bam")

	print("Performing denovo using spades")
	os.system(condaDir+"/bin/spades.py -1 read_1.fq -2 read_2.fq --cov-cutoff auto --careful -o outputSpades -t "+threads+" >null 2>&1")

	os.system("mv read_1.fq ./"+outputFolder+"/reads/"+gene+"_dedup_1.fastq")
	os.system("mv read_2.fq ./"+outputFolder+"/reads/"+gene+"_dedup_2.fastq")
	if os.path.isfile("./outputSpades/scaffolds.fasta") == True:
		os.system("mv ./outputSpades/scaffolds.fasta ./"+outputFolder+"/scaffolds/"+gene+"_scaffolds.fasta")

	os.system("rm -rf alignment* merged.bam firstMapped.bam readCount secondMapped.bam bothMapped.bam reference* outputSpades dedupped.bam rg_added_sorted.bam")


os.system("cat ./reads/*dedup_1.fastq > all_1.fastq")
os.system("cat ./reads/*dedup_2.fastq > all_2.fastq")






