#!/bin/env python3
import math
import os
import sys

from scipy.stats import mannwhitneyu

from typing import List, Dict

import numpy as np

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


def rank_list(all_runs: Dict[str, List[int]]) -> List[int]:
    # Create new list with the mean values
    list_to_rank = list()
    strategy_to_rank = list()
    for strategy in all_runs.keys():
        strategy_to_rank.append(strategy)
        if len(all_runs[strategy]) > 0:
            list_to_rank.append(np.mean(all_runs[strategy]))
        else:
            list_to_rank.append(float('inf'))

    order = sorted(list_to_rank, key=lambda x : float('inf') if math.isnan(x) else x)

    ranking = list(list_to_rank)
    for i in range(0, len(list_to_rank)):
        ranking[i] = order.index(list_to_rank[i]) + 1

    first_to_compare = all_runs[strategy_to_rank[ranking.index(1)]]

    # find the second rank (which can be 2 or a larger number)
    tmp_rank = list(ranking)
    tmp_rank.remove(1)
    reduced_ranking = sorted(list(set(tmp_rank)))
    second_to_compare = all_runs[strategy_to_rank[ranking.index(reduced_ranking[reduced_ranking.index(min(reduced_ranking))])]]

    if len(second_to_compare) == 0:
        return ranking

    _, pvalue = mannwhitneyu(first_to_compare, second_to_compare)

    if pvalue > 0.05:
        ranking[ranking.index(1)] = 2

    return ranking


def write_to_latex_file(path: str, performance_data: Dict[str, Dict[str, Dict[int, List[int]]]]) -> None:
    with open(path, 'w') as latex_file:
        case_studies = list(performance_data.keys())
        strategies = performance_data[case_studies[0]]
        latex_file.write("\\toprule\n")
        # Write header
        for strategy in sorted(strategies):
            latex_file.write(f"& \\multicolumn{{{len(SIZES)}}}{{c}}{{{strategy}}}")
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

        for case_study in sorted(case_studies, key=str.casefold):
            latex_file.write(f"\\textsc{{{case_study}}}")
            # Prepare data for ranking
            case_study_data: Dict[int, Dict[str, List[int]]] = dict()
            for strategy in sorted(strategies):
                for size in SIZES:
                    if size not in case_study_data:
                        case_study_data[size] = dict()
                    if size not in performance_data[case_study][strategy]:
                        case_study_data[size][strategy] = list()
                    else:
                        case_study_data[size][strategy] = performance_data[case_study][strategy][size]
            ranking_per_size = dict()
            for size in SIZES:
                ranking_per_size[size] = rank_list(case_study_data[size])

            for strategy in sorted(strategies):
                strategy_index = list(sorted(strategies)).index(strategy)
                for size in SIZES:
                    latex_file.write(" & ")
                    if size in performance_data[case_study][strategy]:
                        if ranking_per_size[size][strategy_index] == 1:
                            latex_file.write("\\textbf{\\color{Green}")
                            latex_file.write(time_to_str(avg(performance_data[case_study][strategy][size])))
                            latex_file.write("}")
                        else:
                            latex_file.write(time_to_str(avg(performance_data[case_study][strategy][size])))
                    else:
                        latex_file.write("$>3$h")
            latex_file.write("\\\\\n")
        latex_file.write("\\bottomrule\n")

def avg(int_list: List[int]) -> int:
    if len(int_list) == 0:
        return -1
    return int(sum(int_list) / len(int_list))

def time_to_str(time: int) -> str:
    if time == -1:
        return "$>3$h"
    hours = int(time / 3600)
    minutes = int(time % 3600 / 60)
    seconds = int(time % 60)
    if hours >= 1:
        return "$" + str(hours) + "$h $" + str(minutes).rjust(2, '0') + "$m"
    elif minutes >= 2:
        return "$" + str(minutes) + "$m $" + str(seconds).rjust(2, '0') + "$s"
    elif minutes == 0 and seconds == 0:
        return "$<1$s"
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
