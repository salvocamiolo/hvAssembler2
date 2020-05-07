import os,sys
import argparse

parser = argparse.ArgumentParser(description="Deduplicate reads for hypervariable genes")
parser.add_argument("-1", "--read1", type=str, required=True, help="Path to the fastq file 1")
parser.add_argument("-2", "--read2", type=str, required=True, help="Path to the fastq file 2")
parser.add_argument("-c","--conda_directory",type=str, required=True,help="Path to the conda 3 environment")
parser.add_argument("-t","--num_threads",type=str, required=False,help="number of threads")
parser.add_argument("-s","--savage_folder",type=str, required=True,help="Savage executable folder")
args = vars(parser.parse_args())
condaDir = args['conda_directory']
read1 = args['read1']
read2 = args['read2']
if not args['num_threads']:
	threads = 1
else:
	threads = args['num_threads']


hvg = ['RL12','RL13','RL5A','RL6','UL11','UL120','UL139','UL146','UL1','UL20','UL73','UL74','UL9']

for gene in hvg:
	print("Indexing reference for gene %s" %gene)
	os.system(condaDir+"/bin/bowtie2-build -q ./elongedCDS/"+gene+"_elongedCDS.fasta reference > null 2>&1")
	print("Aligning reads to reference....")
	os.system(condaDir+"/bin/bowtie2 --very-sensitive-local -1 "+read1+" -2 "+read2+" -x reference -S alignment.sam -a -p "+threads+" > null 2>&1")
	print("Coverting sam to bam....")
	os.system(condaDir+"/bin/samtools view -h -bS alignment.sam > alignment.bam")
	print("Collecting first mapped reads....")
	os.system(condaDir+"/bin/samtools view -h -b -F 4 -f 8 alignment.bam > firstMapped.bam")
	print("Collecting second mapped reads....")
	os.system(condaDir+"/bin/samtools view -h -b -F 8 -f 4 alignment.bam > secondMapped.bam")
	print("Collecting both mapped reads....")
	os.system(condaDir+"/bin/samtools view -h -b -F12 alignment.bam > bothMapped.bam")
	print("Merging alignments....")
	os.system(condaDir+"/bin/samtools merge merged.bam firstMapped.bam secondMapped.bam bothMapped.bam")
	print("Extracting reads....")
	os.system(condaDir+"/bin/bamToFastq -i merged.bam -fq read_1.fastq -fq2 read_2.fastq")

	print("finished")
	sys.stdin.read(1)





