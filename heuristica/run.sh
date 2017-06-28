#!/bin/bash

instance_file=$1
instance_name=$(basename "$instance_file")
instance_name="${instance_name%.*}"

alpha=0.2
giter=10
grep=100
lsiter=200
lsrep=10
pneigh=0.2

for seed in 0 1 2 3 4 5 6 7 8 9
do
	id=${alpha}_${seed}_${giter}_${grep}_${lsrep}_${lsiter}_${pneigh}
	result_file=results/${instance_name}_${id}.result
	solution_file=solutions/${instance_name}_${id}.solutions
	metadata_file=metadata/${instance_name}_${id}.metadata
	{ time python grasp.py $instance_file --alpha 0.2 --seed $seed --giter 10 --grep 10 --lsiter 100 --lsrep 5 --pneigh 0.1 --fsol $solution_file ; } 2> $metadata_file > $result_file
done

