#!/bin/bash
#$ -hard -l qxt3=215 -l excl=true -l hostname=mb-so4.cax.lan
#$ -q abaqus3@*
#$ -cwd -V
#$ -j y
#$ -N control_arm_topo_controller_casting_01
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 04080943
#$ -M frantisek.siegl@idiada.cz
#$ -m beas
#$ -v input_files_count=2
#$ -v input_file_1=control_arm_topo_controller_casting_01.par
#$ -v input_file_2=control_arm_whole.inp
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir

/bin/uname -a

echo "Starting TOSCA"
tosca19 -cpus 12 -scpus 1  control_arm_topo_controller_casting_01.par > control_arm_topo_controller_casting_01.par.out
echo "TOSCA finished with the status:" $?

# now sleep
sleep 10
