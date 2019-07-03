#!/bin/bash
#$ -hard -l nastran=76
#$ -q nastran@*
#$ -soft -q nastran@mb-so1.cax.lan
#$ -cwd -V
#$ -j y
#$ -N control_arm_topo_controller_casting_01
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 05311657
#$ -M frantisek.siegl@idiada.cz
#$ -m bes
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir

/bin/uname -a

echo "Starting TOSCA"
tosca19 -cpus 4 -scpus 1  control_arm_topo_controller_casting_01.par > control_arm_topo_controller_casting_01.par.out
echo "TOSCA finished"
