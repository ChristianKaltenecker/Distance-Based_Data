#!/bin/bash

cluster=${SLURM_JOB_PARTITION}

file="${cluster}_jobs_$1.txt"
filePath="/scratch/${USER}/Jobs/$file"
taskID=${SLURM_ARRAY_TASK_ID}
lineToRead=${taskID}
# execute all arguments (script with parameters)
commandLine=$(sed "${lineToRead}q;d" ${filePath})
bash -c "${commandLine}"