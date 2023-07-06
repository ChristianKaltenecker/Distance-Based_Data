#!/bin/env python3
import os
import sys

import numpy as np

from typing import List, Dict


SIZES = [10, 100, 1000]

def print_usage() -> None:
    print("./process_scalability_experiments.py <ResultDirectory> <outputTexFile>")
    print("ResultDirectory\t The path to the directory containing the results of the scalability measurements.")
    print("outputTexFile\t The path to the file where the LaTeX table should be written to.")

def list_path(path: str, files: bool = False) -> List[str]:
    '''
    Returns the subdirectories of the given path.
    :param path: the path to find the subdirectories from.
    :param files: whether to return the files or directories.
    :return: the subdirectories or files as list.
    '''
    for root, dirs, files in os.walk(path):
        if files:
            return files
        return dirs


def get_sampling_time(path: str) -> int:
    with open(path, 'r') as log_file:
        for line in log_file:
            if "Total sampling time" in line:
                return parse_time(line.replace("Total sampling time: ", ""))
    return -1


def parse_time(time: str) -> int:
    split_time = time.split(":")
    seconds = split_time[-1].split(".")
    return 3600 * int(split_time[0]) + 60 * int(split_time[1]) + int(seconds[0])


def write_to_latex_file(path: str, performance_data: Dict[str, Dict[str, Dict[int, List[int]]]]) -> None:
    with open(path, 'w') as latex_file:
        case_studies = list(performance_data.keys())
        strategies = performance_data[case_studies[0]]
        latex_file.write("\\toprule\n")
        # Write header
        for strategy in sorted(strategies):
            latex_file.write(f"& \\multirow{{{len(SIZES)}}}{{c}}{{{strategy}}}")
        latex_file.write("\\\\")
        current_column = 1
        for _ in sorted(strategies):
            latex_file.write(f"\\cmidrule{{{current_column}-{current_column + len(SIZES) - 1}}}")
            current_column += len(SIZES)
        latex_file.write("\n")
        for _ in sorted(strategies):
            for size in SIZES:
                latex_file.write(f"& ${size}$")
        latex_file.write("\\\\\n")

        latex_file.write("\\midrule\n")

        for case_study in case_studies:
            latex_file.write(case_study)
            for strategy in sorted(strategies):
                for size in SIZES:
                    latex_file.write(" & ")
                    latex_file.write(time_to_str(avg(performance_data[case_study][strategy][size])))
            latex_file.write("\\\\\n")
        latex_file.write("\\bottomrule\n")

def avg(int_list: List[int]) -> int:
    if len(int_list) == 0:
        return -1
    return int(sum(int_list) / len(int_list))

def time_to_str(time: int) -> str:
    if time == -1:
        return "$>$3h"
    hours = int(time / 3600)
    minutes = int(time % 3600 / 60)
    seconds = int(time % 60)
    if hours >= 1:
        return str(hours) + "h " + str(minutes).rjust(2, '0') + "m"
    elif (minutes >= 2):
        return str(minutes) + "m " + str(seconds).rjust(2, '0') + "s"
    elif minutes == 0 and seconds == 0:
        return "$<$1s"
    else:
        return str(minutes * 60 + seconds) + "s"

def main() -> None:
    if len(sys.argv) != 3:
        print_usage()
        exit(-1)
    result_dir_path = sys.argv[1]
    output_file_path = sys.argv[2]
    result_dirs = list_path(result_dir_path)

    performance_results: Dict[str, Dict[str, Dict[int, List[int]]]] = dict()

    for result_dir in result_dirs:
        split_name = result_dir.split("_")
        case_study = split_name[0]
        if case_study not in performance_results:
            performance_results[case_study] = dict()
        files_in_result_dir = list_path(os.path.join(result_dir_path, result_dir), True)
        files_in_result_dir = [x for x in files_in_result_dir if x.startswith("out_") and x.endswith(".log")]
        for log_file in files_in_result_dir:
            split_file_name = log_file.split("_")
            strategy = split_file_name[1]
            if strategy not in performance_results[case_study]:
                performance_results[case_study][strategy] = dict()
            number_samples = int(split_file_name[2].split(".")[0])
            if number_samples not in performance_results[case_study][strategy]:
                performance_results[case_study][strategy][number_samples] = list()
            performance_result = get_sampling_time(os.path.join(result_dir_path, result_dir, log_file))
            if performance_result != -1:
                performance_results[case_study][strategy][number_samples].append(performance_result)
    write_to_latex_file(output_file_path, performance_results)


if __name__ == "__main__":
    main()
