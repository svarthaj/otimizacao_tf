#!/bin/bash

instance_file=$1
instance_name=$(basename "$instance_file")
instance_name="${instance_name%.*}"

lsiter=150
lsrep=10

for giter in 10 100
do
	for alpha in 0.1 0.25
	do
		for pneigh in 0.1 0.25
		do
			grep=$[ giter/5 ]
			for seed in 0 1 2 3 4 5 6 7 8 9
			do
				id=${alpha}_${seed}_${giter}_${grep}_${lsrep}_${lsiter}_${pneigh}
				result_file=results/${instance_name}_${id}.result
				solution_file=solutions/${instance_name}_${id}.solutions
				metadata_file=metadata/${instance_name}_${id}.metadata
				echo
				echo "$instance_name alpha:$alpha seed:$seed giter:$giter grep:$grep lsiter:$lsiter lsrep:$lsrep pneigh:$pneigh"
				{ time python grasp.py $instance_file --alpha $alpha --seed $seed --giter $giter --grep $grep --lsiter $lsiter --lsrep $lsrep --pneigh $pneigh --fsol $solution_file ; } 2> $metadata_file > $result_file
			done
		done
	done
done
