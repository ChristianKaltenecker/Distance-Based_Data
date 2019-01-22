[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

# Distance-Based Sampling

Distance-based sampling is a novel black-box sampling approach as described in the paper "Distance-Based Sampling of Software Configuration Spaces" by Christian Kaltenecker, Alexander Grebhahn, Norbert Siegmund, Jianmei Guo, and Sven Apel submitted to ICSE 2019.
In this repository, we describe how to reproduce our results in the paper. 

## Overview

![Sketch](https://github.com/ChristianKaltenecker/Distance-Based_Data/raw/master/Sketch.png)

The picture above contains the sketch of our approach.
The input are the variability model and the raw performance measurements from the given case study.
Generally, our approach consists of 3 stages:

**I. Sampling**: SPL Conqueror provides different sampling strategies to select a few configurations from the set of all valid configurations.
The sample set is used afterwards as input for the machine-learning technique.

**II. Machine Learning**: Uses a set of configurations to derive a performance model for performance predictions.
The difference between the performance predictions and the real performance values is given by the error rate.

**III. Aggregation (Python scripts)**: Because of the high amount of data, we provide scripts to process the whole data and to generate the table in the paper, we further provide scripts.

## Data 

In our paper, we use the sampling strategies to predict the performance of all valid configurations (i.e., the whole population) by only using a few configurations (i.e., a sample set).
For this process, we distinguish between the following data:
* *Raw Performance Measurements*: Contains the performance values for the whole population of all case studies.
* *Predictions*: Contains the prediction error that is a result by applying the machine-learning technique on the sample set.

The data is published in the [Distance-Based Data](https://github.com/ChristianKaltenecker/Distance-Based_Data/tree/master/SupplementaryWebsite) repository.

### Measured Performance Values

We have acquired the performance measurements for all used case studies in previous studies and selected a subset of them by using different sampling strategies.
To replicate the raw performance measurements, we also provide detailed description files describing the environment and the used workload.
However, the replication of the raw data required multiple months of CPU time per case study and has to be performed on a hardware with the same characteristics and, thus, can be avoided.

### Predicted Performance Values

For comparing the different sampling strategies, we applied a machine-learning technique to learn performance models that can be used for performance prediction.
For answering our research questions and, thus, for comparing the sampling strategies, we used the prediction error of these performance models.
Since using a random seed in all sampling strategies (except for t-wise) leads to different sample sets, we have performed the case studies with 100 different seeds from 1 to 100.

## Programs & Scripts

### SPL Conqueror
The distance-based sampling strategy was implemented in [SPL Conqueror](https://github.com/se-passau/SPLConqueror), which is a library that currently contains the implementations of all sampling strategies considered in the paper, as well as the machine-learning technique (i.e., multiple linear regression).
To perform sampling and to learn performance models, we depend only on SPL Conqueror.

### Scripts

To process the prediction data and automatically generate tables as presented in Section V (Results), we additionally provide Python scripts for data processing, which further invoke an R script for the significance tests.
The output of the scripts are tex files that can be embedded in LaTeX.

## Installation
<!-- TODO: Put the following text also in INSTALL -->
For the reproduction of our results, one can use the provided Dockerfile to automatically deploy a docker container with a fully initialized environment.
Alternatively, it is also possible to [manually setup](#manual-setup) the tooling on a Linux-based operating system.

### Setup via Dockerfile

To ease the installation of our tool, we also provide a [Dockerfile](./Dockerfile) for setting up a docker container.
Please note that the container will use up to 5 GB of space after the setup.

For setting up a docker container, docker is needed. 
Please refer to the [documentation](https://docs.docker.com/install/linux/docker-ce/ubuntu/) on how to install docker on your Linux operating system.

After docker is installed, make sure that the docker daemon is running. On systemd, you can use ```systemctl status docker``` to check the status of the daemon and ```sudo systemctl start docker``` to start the daemon.

Next, the container can be set up by invoking ```sudo docker build -t distance-based ./```.
By invoking this script, all dependencies as described in Section [Manual Setup](#manual-setup) are installed, which might take a while.

After setting up the docker container, all required ressources (i.e., packages, programs, and scripts) are installed and can now be used inside the container.
To begin an interactive session, the command ```sudo docker run -i -t distance-based /bin/bash``` can be used.
After starting the interactive session, you can continue [here](#usage).


### Manual Setup

Requirements:
  * Operating system: Ubuntu/Debian
  * Mono (for running SPL Conqueror)
  * git (for cloning the required repositories)
  * wget
  * unzip, tar
  * texlive (for generating the table)
  * Python (for the aggregation of the results):
    * numpy
    * scipy
  * R (for the significance tests)

#### Data

To clone the repository containing the data (variability models, measured performance values, and predicted performance values), use the following command:

```
git clone https://github.com/ChristianKaltenecker/Distance-Based_Data.git
```

Since the measured performance values of JavaGC and VP9 are compressed because of size restrictions, they have to be uncompressed by using `tar` with the following commands:

```
tar -xzf Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/JavaGC/measurements.tar.gz -C Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/JavaGC/
tar -xzf Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/VP9/measurements.tar.gz -C Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/VP9/
```

#### SPL Conqueror

Since we executed SPL Conqueror in our paper with a specific version, additional steps are required to reset the repository to the version from the paper.
```
git clone https://github.com/se-passau/SPLConqueror.git
cd SPLConqueror
git reset --hard 8d5e442f0e085f8df6d7807ca69c65deeae7e0b3
```

SPL Conqueror is written in C# and, thus, depends on [Mono](https://www.mono-project.com/) and [NuGet](https://www.nuget.org/).
The Mono packages can be downloaded by using a package manager, such as `apt`:
```
sudo apt install -y mono-complete
```
The current version of NuGet can be downloaded by using the command:
```
cd SPLConqueror
wget https://dist.nuget.org/win-x86-commandline/latest/nuget.exe 
``` 

After cloning the repository with the given version, SPL Conqueror has to be built. This can be done by using the following commands:
```
mono nuget.exe restore ./
xbuild /p:Configuration=Release /p:TargetFrameworkVersion="v4.5" /p:TargetFrameworkProfile="" ./SPLConqueror.sln
cd ../../
```

#### z3 Constraint solver

Since we used the [z3](https://github.com/Z3Prover/z3) constraint solver to find solutions (i.e., valid configurations), the library for the z3 solver has to be additionally downloaded.
This can be done as follows:
```
wget https://github.com/Z3Prover/z3/releases/download/z3-4.7.1/z3-4.7.1-x64-debian-8.10.zip
unzip z3-4.7.1-x64-debian-8.10.zip -d z3
rm z3-4.7.1-x64-debian-8.10.zip
mv z3-4.7.1-x64-debian-8.10/bin/libz3.so /usr/lib/libz3.so
```

#### Scripts

To execute the scripts, [python3](https://www.python.org/download/releases/3.0/) and [R](https://www.r-project.org/) are required.
These can be installed on Debian using `apt` as follows:
```
sudo apt install -y python3 python3-numpy python3-scipy r-recommend
```
For the installation of the dependencies for R, we provide an installation file, which can be invoked as follows:
```
Rscript InstallPackages.R
```
Please be aware that this installation process might take a while.


## Usage

Note that the complexity of the case studies differs, which is why some case studies need more time than others. 
We advise you to take a look on the performance values on the [supplementary website](https://github.com/ChristianKaltenecker/Distance-Based_Data/tree/master/SupplementaryWebsite) to simplify the decision on which results to replicate.
For a better demonstration of the usage, we show it exemplarily on the case study x264.

The location of the measured performance values is ```Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues```.
The predicted performance values of all random seeds are stored in ```Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/AllRuns```, whereas the summarized data is stored in ```Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/Summary```.

### Replication of a random seed

The following commands have to be executed inside the repository "Distance-Based_Data"
```
cd Distance-Based_Data/
```
To execute the sampling and machine-learning process, we provide the script SPLConquerorExecuter.py.
```
./SPLConquerorExecuter.py <caseStudy> <strategy> <saveLocation> [run_start] [run_end]
```
For the arguments, the *case study* (7z, BerkeleyDBC, Dune, Hipacc, JavaGC, lrzip, LLVM, Polly, VP9, x264), the *sampling strategy* (t-wise, solverBased, henard, distanceBased, diversified, random), the *location* for the results have to be known.
Additionally, if not all 100 runs should be reproduced, the interval of the random seed can be specified.

In our example, we firstly create a new directory for storing the new results.
```
mkdir -p /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/NewRuns
```
Afterwards, we can use the script to perform diversified distance-based sampling for the case study x264 by using the random seeds 42-43.
```
./SPLConquerorExecuter.py x264 diversified /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/NewRuns 42 43
```
By executing this script, new directories are created for the case study and the random seed.
The structure is as follows:
  * run directory (e.g., NewRuns)
    * case study (e.g., x264)
      * case study with random seed (e.g., x264_42)
        * SPL Conqueror log files for a sampling strategy and different sample sizes (e.g., out_diversified_t1.log)
        * SPL Conqueror sample set files for a sampling strategy and  (e.g., sampledConfigurations_diversified_t1.csv)

To compare the results, one has to compare the results of (1) the same case study using (2) the same sampling strategy, (3) the same random seed, and (4) the same sample size.
The results can be compared by comparing (I.) error rates or/and (II.) sample sets.

**I. Error Rates**: 
For comparing the error rates, the SPL Conqueror log files are required, since they contain the error rate.
The error rate is the last number in the last line before `Analyze finished`.
In this example, the error rate is 10.481%.
```
[...]
3;472.586666666666 * no_asm + -29.8533333333331 * no_mixed_refs + -212.187499999999 * ref_1 + 214.236666666666 * ref_9;5.75863710582891;5.75863710582891;5.75863710582891;5.75863710582891;0.05085;4;214.236666666666 * ref_9;1;7.31333436817488;10.4810287299971
Analyze finished
[...]
```
These error rates should be the same for our provided predictions and the replicated predictions.

**II. Sample Sets**:
Comparing the sample sets can be done by using the `diff` tool.
The usage is as follows:
```
diff <file1> <file2>
```

In our example, we would compare the new sample set with the provided sample set.
```
diff /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/NewRuns/x264/x264_42/sampledConfigurations_divDistBased_t1.log /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/AllRuns/x264/x264_42/sampledConfigurations_divDistBased_t1.log
```

### Aggregation

For the aggregation of our results, we provide two scripts:
**I. analyzeRuns.py**: 
  Gathers all information about the runs of all case studies and stores it in a given summary directory.
  Usage: `./analyzeRuns.py <runDirectory> <summaryDirectory>`
  `runDirectory` is the directory where all runs of all case studies are stored. 
  `summaryDirectory` is the directory where the accumulated results should be written to.

  In our example, we aggregate the results of `AllRuns` and write them into `Summary`:
  ```
  ./analyzeRuns.py /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/AllRuns/ /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/Summary/
  ```
**II. ErrorRateTableCreator.py**:
  Reads in the information gathered by `analyzeRuns.py` and uses `PerformKruskalWallis.R` to perform the significance tests (e.g., Kruskal Wallis, Mann Whitney U) on them.
  The results are written in multiple different table files.
  Usage: `./ErrorRateTableCreator.py <inputDirectory> <typesToAdd> <labelsOfTypes> <outputDirectory>`

  `inputDirectory` the directory containing the summary files.

  `typesToAdd` the sampling file labels to add (e.g., distBased, divDistBased).

  `lablesOfTypes` the labels of the sampling strategies that should be used in the table (e.g., Distance-based, Diversified distance-based). Please be aware that the order of the arguments has to be the same as in `typesToAdd`.

  `outputDirectory` the directory where the tex files should be written to.

  In our example, we use the aggregated results of all sampling strategies.
  ```
  ./ErrorRateTableCreator.py /application/Distance-Based_Data/SupplementaryWebsite/PredictedPerformanceValues/Summary/ "twise,solvBased,henard,distBased,divDistBased,rand" "Coverage-based,Solver-based,Randomized solver-based,Distance-based,Diversified distance-based,Random" /application/Distance-Based_Data
  ```

  Afterwards, `pdflatex` and the file `TableStandalone.tex` should be used to create the table.
  ```
  pdflatex TableStandalone.tex
  ```
  To view the pdf file in a docker container, the pdf file can be copied to the host system.
  ```
  sudo docker cp <containerId>:/application/Distance-Based_Data ~
  ```