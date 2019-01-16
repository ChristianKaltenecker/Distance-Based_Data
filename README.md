[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

# Distance-Based Sampling

Distance-based sampling is a novel black-box sampling approach as described in the paper "Distance-Based Sampling of Software Configuration Spaces" by Christian Kaltenecker, Alexander Grebhahn, Norbert Siegmund, Jianmei Guo, and Sven Apel submitted to ICSE 2019.
In this repository, we extensively describe how to reproduce our results in the paper. 

## Overview

![Sketch](https://github.com/ChristianKaltenecker/Distance-Based_Data/raw/master/Sketch.png)

## Data 

In our paper, we use the sampling strategies to predict the performance of all valid configurations (i.e., the whole population) by only using a few configurations (i.e., a sample set).
For this process, we distinguish between the following data:
* <i>Raw Performance Measurements</i>: Contains the performance values for the whole population of all case studies.
* <i>Predictions</i>: Contains the prediction error that are a result by applying the machine-learning technique on the sample set.

The data is published in the [Distance-Based Data](https://github.com/se-passau/Distance-Based_Data) repository.

### Raw Measurements

We have acquired the raw performance measurements for all used case studies in previous studies and selected a subset of it by using different sampling strategies.
To replicate the raw performance measurements, we also provide detailed description files describing the environment and the used workload.
However, we do not advise the replication of the raw data, since this process needs multiple months of CPU time per case study and has to be performed on a hardware with the same characteristics.

### Predictions

For comparing the different sampling strategies, we applied a machine-learning technique to learn performance models that can be used for performance prediction.
For answering our research questions and, thus, for comparing the sampling strategies, we used the prediction error of these performance models.
Since using a random seed in all sampling strategies (except for t-wise) results in different sample sets, we have performed the case studies with 100 different seeds from 1 to 100.

## Programs & Scripts

### SPL Conqueror
The distance-based sampling strategy was implemented in [SPL Conqueror](https://github.com/se-passau/SPLConqueror), which is a library that currently contains the implementations of all sampling strategies considered in the paper, as well as the machine-learning technique (i.e., multiple linear regression).
So, to perform sampling and to learn performance models, we depend only on SPL Conqueror.

### Scripts

To process the prediction data and automatically generate tables as presented in Section V (Results), we additionally provide python scripts for data processing, which further invoke an R script for the significance tests.
The output of the scrips are tex files that can be embedded in LaTeX.

## Installation
<!-- TODO: Put the following text also in INSTALL -->
For the reproduction of our results, one can use the provided Dockerfile to automatically deploy a docker container with a fully initialized environment.
Alternatively, it is also possible to manually setup on a Linux-based operating system.

### Setup via Dockerfile

To ease the installation of our tool, we also provide a [Dockerfile](./Dockerfile) for setting up a docker container.
Please note that the container will use up to 5 GB of space after the setup.

For setting up a docker container, docker is needed. 
Please refer to the [documentation](https://docs.docker.com/install/linux/docker-ce/ubuntu/) on how to install docker on your Linux operating system.

After docker is installed, make sure that the docker daemon is running. On systemd, you can use ```sudo systemctl status docker``` to check the status of the daemon and ```sudo systemctl start docker``` to start the daemon.

Next, the container can be set up by invoking ```sudo docker build -t distance-based ./```.
By invoking this script, all dependencies as described in Section [Manual Setup](#manual-setup) are installed, which might take a while.

After setting up the docker container, all needed ressources (i.e., packages, programs, and scripts) are installed and can now be used inside the container.
To begin an interactive session, the command ```sudo docker run -i -t distance-based /bin/bash```.


### Manual setup

Requirements:
  * Operating system: Ubuntu/Debian
  * Mono (for running SPL Conqueror)
  * git (for cloning the needed repositories)
  * Python (for the analysis):
    * scipy
  * R (for the analysis)

#### Data

To clone the repository containing the data (variability models, raw performance measurements and predictions), use the following command:

```
git clone https://github.com/ChristianKaltenecker/Distance-Based_Data.git
```

#### SPL Conqueror

Since we performed SPL Conqueror with a specific version, additional steps are needed to reset the repository to the version from the paper.
```
git clone https://github.com/se-passau/SPLConqueror.git
cd SPLConqueror
git reset --hard 8d5e442f0e085f8df6d7807ca69c65deeae7e0b3
```

SPL Conqueror is written in C# and, thus, depends on [Mono](https://www.mono-project.com/) and [NuGet](https://www.nuget.org/).
The Mono packages can be downloaded by using a package manager, such as apt:
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
xbuild /p:Configuration=Release SPLConqueror.sln
cd ~
```

#### z3 Constraint solver

Since we used the [z3](https://github.com/Z3Prover/z3) constraint solver to find solutions (i.e., valid configurations), the library for the z3 solver has to be additionally downloaded.
This can be done as follows:
```
wget https://github.com/Z3Prover/z3/releases/download/z3-4.7.1/z3-4.7.1-x64-debian-8.10.zip
unzip z3-4.7.1-x64-debian-8.10.zip -d z3
rm z3-4.7.1-x64-debian-8.10.zip
```

#### Scripts

To execute the scripts, [python3](https://www.python.org/download/releases/3.0/) and [R](https://www.r-project.org/) are needed.
These can be installed using apt as follows:
```
sudo apt install -y python3 r-recommend
```



<!-- Python and R packages? -->

The data processing scripts are provided by this repository. You can clone it by using:
```
git clone https://github.com/se-passau/Distance-Based_Sampling.git
```

## Usage

<!-- 
Which scripts are available?
How to configure the script?
How to execute specific runs of given sampling strategies and use cases?
 -->
TODO