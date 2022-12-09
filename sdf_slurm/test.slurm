#!/bin/bash

#SBATCH --partition=roma
#
#SBATCH --job-name=py_test
#SBATCH --output=output-%j.txt
#SBATCH --error=output-%j.txt
#
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1g
#
#SBATCH --time=0-00:10:00
#SBATCH --chdir=/sdf/home/y/yoachim/rubin-user/git_repos/23_Scratch/sdf_slurm

## Set up the evironment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate rubin
export OPENBLAS_NUM_THREADS=1

echo "testing 1 2 3"
python test.py
