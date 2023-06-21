#!/bin/env python3

import time
import subprocess
import sys
import os
from typing import List

RUNS_FROM = 1
RUNS_TO = 10
CLUSTER = "maxl"

JOB_ID=int(time.time() * 1000)

HOME = "/scratch/kaltenec/"
PREFIX = os.path.join(HOME, "Distance-Based_Scalability")

SBATCH = "sbatch"
SBATCH_OPTIONS = f"--constraints={CLUSTER} --exclusive --exclude='maxl[17-20]' -n 1 -c 1 --mem=255000M --time='07:00:00' --qos=norm " \
                 f"--output={PREFIX}/slurm_out.log "
SBATCH_SCRIPT = os.path.join(PREFIX, "Scripts", "runDistributionAware.sh")

JOB_DIR = HOME + "Jobs/"
JOB_FILE_PREFIX = "_jobs_"
JOB_FILE_SUFFIX = ".txt"
JOB_SCRIPT = os.path.join(PREFIX, "Scripts", "runRandomHundredTimes.sh")

STRATEGIES = ["solvBased", "henard", "distBased", "divDistBased"]

def print_usage() -> None:
    print("Usage:")
    print("./JobSubmitter")


def execute_command(command : str) -> str:
    output = subprocess.getstatusoutput(command)
    status_code = output[0]
    message = output[1]

    # Throw an error if the command was not successfully executed
    if status_code != 0:
        raise RuntimeError(message)

    return message


def write_to_file(file_path : str, lines_to_write : List[str]):
    with open(file_path, 'a') as file:
        for line in lines_to_write:
            file.write(line + "\n")


def list_directories(path: str) -> List[str]:
    """
    Returns the subdirectories of the given path.
    :param path: the path to find the subdirectories from.
    :return: the subdirectories as list.
    """
    for root, dirs, files in os.walk(path):
        return list(filter(lambda x: not x.startswith("."), dirs))


def main() -> None:
    global SBATCH_OPTIONS
    if len(sys.argv) != 1:
        print_usage()
        exit(-1)


    options_to_add = "-A anywhere -p anywhere "
    options_to_add += " --constraint=\"" + CLUSTER

    options_to_add += "\""
    SBATCH_OPTIONS = f"{options_to_add} {SBATCH_OPTIONS} -J SamplingScalability"

    # Construct the jobs for the job-file
    jobs = []
    case_studies = list_directories(os.path.join(PREFIX, "FeatureModels"))
    save_location = os.path.join(PREFIX, "Results")
    for case_study in case_studies:
        for sampling_strategy in STRATEGIES:
            for run in range(RUNS_FROM, RUNS_TO + 1):
                job_string = "export LD_LIBRARY_PATH=/scratch/kaltenec/lib:$LD_LIBRARY_PATH && "
                log_location = os.path.join(PREFIX, f"{case_study}_{sampling_strategy}_{run}.log")
                job_string += f"{JOB_SCRIPT} {case_study} {sampling_strategy} {save_location} {run} {run} >> {log_location}"
                jobs.append(job_string)

    # Write to the job file
    job_file = f"{JOB_DIR}anywhere{JOB_FILE_PREFIX}{JOB_ID}{JOB_FILE_SUFFIX}"
    write_to_file(job_file, jobs)

    # Submit the array job
    sbatch_options = f"{SBATCH_OPTIONS} --array=1-{len(jobs)}"
    command_to_submit = f"{SBATCH} {sbatch_options} {SBATCH_SCRIPT} {JOB_ID}"
    print(command_to_submit)
    #output_string = execute_command(command_to_submit)
    #print(output_string)


if __name__ == "__main__":
    main()
