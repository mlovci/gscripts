from glob import glob
from qtools import Submitter
import sys

species = sys.argv[1]

for file in glob('*Rd1*fastq'):

	pair = file.replace('Rd1', 'Rd2')
	name = file.replace('_Rd1', '')
	cmd_list = []
	cmd_list.append('/home/yeo-lab/software/STAR_2.3.0e/STAR \
--runMode alignReads \
--runThreadN 16 \
--genomeDir /projects/ps-yeolab/genomes/{}/star/ \
--genomeLoad LoadAndRemove \
--readFilesIn {}, {} \
--outFileNamePrefix {}. \
--outSAMunmapped Within \
--outFilterMultimapNmax 1'.format(species, file, pair, name))

	sub = Submitter(queue_type='PBS', sh_file='map_'+file+'.sh', command_list=cmd_list, job_name='map_'+file)
	sub.write_sh(submit=True, nodes=1, ppn=16)


for file in glob('*Rd1*gz'):

	pair = file.replace('Rd1', 'Rd2')
	name = file.replace('_Rd1', '')
	cmd_list = []
	cmd_list.append('/home/yeo-lab/software/STAR_2.3.0e/STAR \
--runMode alignReads \
--runThreadN 16 \
--genomeDir /projects/ps-yeolab/genomes/{}/star/ \
--genomeLoad LoadAndRemove \
--readFilesCommand zcat \
--readFilesIn {},{} \
--outFileNamePrefix {}. \
--outSAMunmapped Within \
--outFilterMultimapNmax 1'.format(species, file, pair, name))

	sub = Submitter(queue_type='PBS', sh_file='map_'+file+'.sh', command_list=cmd_list, job_name='map_'+file)
	sub.write_sh(submit=True, nodes=1, ppn=16)
