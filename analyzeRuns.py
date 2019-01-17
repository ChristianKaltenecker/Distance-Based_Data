import sys
import os
import math
from shutil import copyfile

# The sampling strategies that should be analyzed
TYPES = ["local_"]  # , "binom_"] #["semi_", "solv_", "globOpt_", "locOpt_", "rand_", "henard_"]#, "solv_", "rand_"]

SEPARATOR = "/"
SPL_CONQUEROR_PREFIX = "out_"
ALL_RESULTS_PREFIX = "all_"
ERROR_PREFIX = "error_"
STANDARD_DEVIATION_PREFIX = "sd_"
T_TEST_PREFIX = "ttest_"
KOLMOGOROV_SMIRNOV_PREFIX = "kstest_"
WHOLE_POPULATION = "wp"
VARIANCE_RESULT_PREFIX = "var_"
OTHER_FILE_PREFIXES = ["dist_", "measurement_", "point_"]
OTHER_FILE_SUFFIX = ".txt"
SAMPLED_CONFIGURATIONS_FILE = ["sampledConfigurations"]
SAMPLED_CONFIGURATIONS_FILE_SUFFIX = ".csv"
CSV_SEPARATOR = ";"
TOTAL = "total"
SAMPLED_CONFIGURATIONS_STATS_SUFFIX = "_stat"
PERCENT = "%"


def print_usage():
    '''
    Prints the usage of this script.
    '''
    print("Usage: <RunDirectory> <OriginalDirectory>")
    print("RunDirectory\t The directory containing the data of all runs.")
    print("OriginalDirectory\t The directory where the average run should be copied to.")


def list_directories(path):
    '''
    Returns the subdirectories of the given path.
    :param path: the path to find the subdirectories from.
    :return: the subdirectories as list.
    '''
    for root, dirs, files in os.walk(path):
        return dirs


def get_specific_files_from_directory(path, prefixes, suffix, contains=None, excludes=None):
    '''
    Returns all files that begin with one of the given prefixes.
    :param path: the path to check the files from
    :param prefixes: the prefixes of the wanted files
    :return: a list containing the files
    '''
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            found = False
            for prefix in prefixes:
                if prefix in file and file.endswith(suffix):
                    found = True
                    break
            if not found:
                continue

            if contains is not None:
                found = False
                for containedString in contains:
                    if containedString in file:
                        found = True
                        break
                if not found:
                    continue

            if excludes is not None:
                skip = False
                for excludedString in excludes:
                    if excludedString in file:
                        skip = True
                        break
                if skip:
                    continue
            result.append(file)
    return result


def add_to_dictionary(dictionary, file_name, number_run, value):
    '''
    Adds the given data to the dictionary.
    :param dictionary: the dictionary to add to
    :param file_name: the file name
    :param number_run: the number of the random seed run
    :param value: the value to add to the dictionary
    '''
    if file_name not in dictionary:
        dictionary[file_name] = {}
    dictionary[file_name][number_run] = value


def add_bucket_to_dictionary(dict, bucket, numberRun, value):
    '''
    Adds the given bucket to the dictionary
    :param dict: the dictionary to add to
    :param bucket: the bucket (key)
    :param numberRun: the number of run
    :param value: the value to add
    '''
    if bucket not in dict:
        dict[bucket] = {}
    dict[bucket][numberRun] = int(value)


def analyze_log_file(path):
    '''
    Analyzes the log files of SPL Conqueror.
    :param path: the path to the log file
    :return: the error rate
    '''
    error_rate = sys.float_info.max
    python_learner = False

    file = open(path, 'r')
    parse_lines = False
    for line in file:
        # if "Models:" in line:
        #    continue;
        if "command: analyze-learning" in line:
            parse_lines = True
        elif "command: learn-python" in line:
            python_learner = True
        elif "command: clean-sampling" in line:
            parse_lines = False
        elif python_learner and "Error rate" in line:
            error_rate = float(line.strip().split(" ")[-1]) * 100
            return error_rate
        elif not python_learner and parse_lines and ";" in line and not "command" in line:
            split_line = line.strip().split(";")
            current_error_rate = float(split_line[len(split_line) - 1])
            if current_error_rate < error_rate:
                error_rate = current_error_rate
    file.close()

    return error_rate


def add_to_sum_dict(dict, file, value):
    '''
    Adds the given value to the dictionary.
    :param dict: the dictionary to add up to
    :param file: the file (key)
    :param value: the value to add
    :return:
    '''
    if file not in dict:
        dict[file] = 0
    dict[file] += value


def copy_file_content(openedFile, target, run):
    '''
    Copies the file content
    :param openedFile: the file stream
    :param target: the targeted file to read from
    :param run: the run to write
    '''
    targetFile = open(target, 'r')
    # Skip the header
    next(targetFile)
    for line in targetFile:
        openedFile.write(str(run) + ";" + line)
    targetFile.close()


def get_header_of(file):
    '''
    Returns the header of the file
    :param file: the file to read the header from
    :return: the header of the file
    '''
    f = open(file, 'r')
    result = next(f)
    return result


def add_values_from_file_to_dict(dictionary, run, filePath):
    ''''
    Reads in the current content of the file into the dictionary
    :param dictionary: the dictionary to save the content of the file into
    :param run: the random seed run
    :param filePath: the path to the file
    '''
    valueFile = open(filePath, 'r')

    # Skip the header
    next(valueFile)

    # The files have to be written in a csv-like manner, where ';' is taken as element separator and
    # '\n' as row separator
    for line in valueFile:
        elements = line.split(';')
        add_bucket_to_dictionary(dictionary, elements[0], run, elements[1])


def convert_dict_to_list(dictionary):
    '''
    Converts the given dictionary to a list.
    :param dictionary: the dictionary to convert
    :return: the dictionary as list
    '''
    result = []
    for key in dictionary.keys():
        result.append(dictionary[key])
    return result


############
#   MAIN   #
############
def main():
    '''
    This is the main method, which (1) gathers and (2) processes the information of all the runs.
    The accumulated information is stored in another directory.
    '''
    if len(sys.argv) != 3:
        print_usage()
        exit(0)

    run_directory = sys.argv[1]
    original_directory = sys.argv[2]

    if not run_directory.endswith(SEPARATOR):
        run_directory = run_directory + SEPARATOR

    if not original_directory.endswith(SEPARATOR):
        original_directory = original_directory + SEPARATOR

    run_statistic = {}

    # Precompute the prefixes of the files to analyze
    prefixes = []
    for type in TYPES:
        prefixes.append(SPL_CONQUEROR_PREFIX + type[:len(type) - 1])
    suffix = ".log"
    name = ""

    sampled_config_contains = ["_rand_", "_uni_"]
    sampled_exclude = ["_stat"]

    directories = list_directories(run_directory)
    average_values = {}
    for directory in sorted(directories):
        split_name = directory.split("_")
        tmp_name = ""
        print("Scanning " + split_name[len(split_name) - 1] + ". directory.")

        for i in range(0, len(split_name) - 1):
            if i != 0:
                tmp_name += "_"
            tmp_name += split_name[i]
        name = tmp_name
        number_run = int(split_name[len(split_name) - 1])
        files = get_specific_files_from_directory(run_directory + directory, prefixes, suffix)
        for file in sorted(files):
            error = analyze_log_file(run_directory + directory + SEPARATOR + file)
            add_to_sum_dict(average_values, file, error)
            add_to_dictionary(run_statistic, file, number_run, error)

        # Analyze the files containing the samples for the appearance of each feature
        sample_files = get_specific_files_from_directory(run_directory + directory, SAMPLED_CONFIGURATIONS_FILE,
                                                         SAMPLED_CONFIGURATIONS_FILE_SUFFIX, sampled_config_contains,
                                                         sampled_exclude)

        for sampleFile in sample_files:
            input_file = open(run_directory + directory + SEPARATOR + sampleFile, 'r')
            header = input_file.readline().split(CSV_SEPARATOR)
            header = header[:len(header) - 1]
            feature_dictionary = {}
            total_lines = 0.0

            # Initialize the dictionary
            for feature in header:
                feature_dictionary[feature] = {}
                feature_dictionary[feature][TOTAL] = 0
                for innerFeature in header:
                    if feature != innerFeature:
                        feature_dictionary[feature][innerFeature] = 0

            # Collect the data
            for line in input_file:
                total_lines += 1.0
                splitLine = line.split(CSV_SEPARATOR)
                for i in range(0, len(splitLine) - 1):
                    if int(splitLine[i]) != 0:
                        feature_dictionary[header[i]][TOTAL] += 1
                        for j in range(0, len(splitLine) - 1):
                            if i != j and int(splitLine[j]) != 0:
                                feature_dictionary[header[i]][header[j]] += 1

            # Print the data
            sample_file_prefix = sampleFile[:sampleFile.rfind('.')]
            sample_file_suffix = sampleFile[sampleFile.rfind('.'):]
            output = open(
                run_directory + directory + SEPARATOR + sample_file_prefix + SAMPLED_CONFIGURATIONS_STATS_SUFFIX +
                sample_file_suffix, 'w')
            output.write(CSV_SEPARATOR)
            # Print the header
            for feature in header:
                output.write(feature + CSV_SEPARATOR)
            output.write("\n")

            # Print the first row with the total results
            output.write(TOTAL + CSV_SEPARATOR)
            for feature in header:
                if feature_dictionary[feature][TOTAL] == 0:
                    output.write(
                        str(0) + PERCENT + CSV_SEPARATOR)
                else:
                    output.write(str(round(feature_dictionary[feature][TOTAL] / total_lines, 2)) + PERCENT +
                                 CSV_SEPARATOR)
            output.write("\n")

            # Print the remaining rows
            for feature in header:
                output.write(feature + CSV_SEPARATOR)
                for innerFeature in header:
                    if innerFeature != feature:
                        if feature_dictionary[feature][TOTAL] == 0:
                            output.write(str(0) + PERCENT + CSV_SEPARATOR)
                        else:
                            output.write(str(round(feature_dictionary[feature][innerFeature] / total_lines, 2)) +
                                         PERCENT + CSV_SEPARATOR)
                    else:
                        output.write(CSV_SEPARATOR)
                output.write("\n")

    for key in average_values.keys():
        average_values[key] = average_values[key] / len(run_statistic[key])

    # Retrieve the most average runs, print the error rates into a file
    avg_runs = {}
    best_runs = {}
    worst_runs = {}
    best_score = {}
    worst_score = {}
    standard_deviation = {}
    for file in run_statistic.keys():
        best_score[file] = 1000
        worst_score[file] = 0

        min_deviation = sys.float_info.max

        standard_deviation[file] = 0

        # Save the error rates in the following file (needed for box-plots)
        mid_file_name = file[len(SPL_CONQUEROR_PREFIX):len(file) - len(suffix)]
        error_rate_file = open(original_directory + ALL_RESULTS_PREFIX + ERROR_PREFIX + mid_file_name +
                               OTHER_FILE_SUFFIX, 'w')
        error_rate_file.write("Run;Error\n")

        for run in run_statistic[file].keys():
            error = run_statistic[file][run]

            # Ignore runs where the error rate is Inf (in C#)
            if error >= 1.79769313486e+308:
                continue

            if error < best_score[file]:
                best_score[file] = error
                best_runs[file] = run
            if error > worst_score[file]:
                worst_score[file] = error
                worst_runs[file] = run

            try:
                standard_deviation[file] += (average_values[file] - error) ** 2
            except:
                print("Error of run " + str(run) + " too high.")
                continue

            error_rate_file.write(str(run) + ";" + str(error) + "\n")

            deviation = abs(average_values[file] - error)
            if deviation < min_deviation:
                min_deviation = deviation
                avg_runs[file] = run

        error_rate_file.close()

        # Compute the relative standard deviation
        standard_deviation[file] /= len(run_statistic[file].keys())
        standard_deviation[file] = math.sqrt(standard_deviation[file])
        standard_deviation[file] /= average_values[file]

        standard_deviation_file = open(original_directory + ALL_RESULTS_PREFIX + STANDARD_DEVIATION_PREFIX +
                                       mid_file_name + OTHER_FILE_SUFFIX, 'w')
        standard_deviation_file.write(str(standard_deviation[file]) + "\n")
        standard_deviation_file.close()

    complete = True

    for file in run_statistic.keys():
        mid_file_name = file[len(SPL_CONQUEROR_PREFIX):len(file) - len(suffix)]

        for oFP in OTHER_FILE_PREFIXES:
            target_file = run_directory + name + "_" + str(1) + SEPARATOR + oFP + mid_file_name + OTHER_FILE_SUFFIX
            if not os.path.exists(target_file):
                not_complete = False
                break
            # Open a file for including all runs
            all_runs_distributions = open(original_directory + ALL_RESULTS_PREFIX + oFP + mid_file_name +
                                          OTHER_FILE_SUFFIX, 'w')
            all_runs_distributions.write("Runs;" + get_header_of(target_file))

            dist_dict = {}

            for run in run_statistic[file].keys():
                target_file = run_directory + name + "_" + str(
                    run) + SEPARATOR + oFP + mid_file_name + OTHER_FILE_SUFFIX

                if not os.path.exists(target_file):
                    all_runs_distributions.close()
                    not_complete = False
                    break

                add_values_from_file_to_dict(dist_dict, run, target_file)
                copy_file_content(all_runs_distributions, target_file, run)

            all_runs_distributions.close()

    for file in avg_runs.keys():
        source_dir = run_directory + name + "_" + str(avg_runs[file]) + SEPARATOR
        target_dir = original_directory

        # Firstly, copy the distribution, measurements and point data

        # Assuming that the files are always starting with the SPL_CONQUEROR_PREFIX
        file_name = file[len(SPL_CONQUEROR_PREFIX):]
        file_name = file_name[:file_name.rfind(".")]
        if not complete:
            for oFP in OTHER_FILE_PREFIXES:
                file_to_transfer = oFP + file_name + OTHER_FILE_SUFFIX
                source = source_dir + file_to_transfer
                target = target_dir + file_to_transfer
                copyfile(source, target)

        # Copy the sampled configuration files
        sampled_file = SAMPLED_CONFIGURATIONS_FILE[0] + "_" + file_name + SAMPLED_CONFIGURATIONS_FILE_SUFFIX
        source = source_dir + sampled_file
        target = target_dir + sampled_file
        copyfile(source, target)

        # Copy the performance models
        source = source_dir + file
        target = target_dir + file
        copyfile(source, target)

    # Extract the best and worst runs
    for file in best_runs.keys():
        source_dir = run_directory + name + "_" + str(best_runs[file]) + SEPARATOR
        target_dir = original_directory

        # Assuming that the files are always starting with the SPL_CONQUEROR_PREFIX
        file_name = file[len(SPL_CONQUEROR_PREFIX):]
        file_name = file_name[:file_name.rfind(".")]
        # Copy the sampled configuration files
        sampled_source_file = SAMPLED_CONFIGURATIONS_FILE[0] + "_" + file_name + SAMPLED_CONFIGURATIONS_FILE_SUFFIX
        sampled_target_file = SAMPLED_CONFIGURATIONS_FILE[
                                  0] + "_" + file_name + "_best" + SAMPLED_CONFIGURATIONS_FILE_SUFFIX
        source = source_dir + sampled_source_file
        target = target_dir + sampled_target_file
        copyfile(source, target)

        # Copy the performance models
        source = source_dir + file
        target = target_dir + file + "_best"
        copyfile(source, target)

    for file in worst_runs.keys():
        source_dir = run_directory + name + "_" + str(worst_runs[file]) + SEPARATOR
        target_dir = original_directory

        # Assuming that the files are always starting with the SPL_CONQUEROR_PREFIX
        file_name = file[len(SPL_CONQUEROR_PREFIX):]
        file_name = file_name[:file_name.rfind(".")]
        # Copy the sampled configuration files
        sampled_source_file = SAMPLED_CONFIGURATIONS_FILE[0] + "_" + file_name + SAMPLED_CONFIGURATIONS_FILE_SUFFIX
        sampled_target_file = SAMPLED_CONFIGURATIONS_FILE[
                                  0] + "_" + file_name + "_worst" + SAMPLED_CONFIGURATIONS_FILE_SUFFIX
        source = source_dir + sampled_source_file
        target = target_dir + sampled_target_file
        copyfile(source, target)

        # Copy the performance models
        source = source_dir + file
        target = target_dir + file + "_worst"
        copyfile(source, target)


if "__main__" == __name__:
    main()
