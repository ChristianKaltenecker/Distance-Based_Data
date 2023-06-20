#!/bin/bash

REPETITIONS=100;
BEGIN_AT=1;
CONFIGS_TO_SAMPLE=100;
DRY_RUN=false;
INSERT_CONFIGS=true;

TW_COUNTER="1 2 3"

SAMPLED_CONFIGURATION_FILE_PREFIX="sampledConfigurations_"
OUT_PREFIX="out_"
TXT_SUFIX=".txt"
LOG_SUFIX=".log"

SUPER_SCRIPT_NAME="sampleAll.a"

createAFiles () {
        path=$1
        tmp=$2
        seed=$3

        scriptFile="${tmp}${SUPER_SCRIPT_NAME}"


        scriptPath="./";

        > $scriptFile;
        for twCounter in $TW_COUNTER
        do
          file="${tmp}learn_${FILE_NAME}_t$((${twCounter})).a";
          sampleFile="${scriptPath}${SAMPLED_CONFIGURATION_FILE_PREFIX}${FILE_NAME}_t$((${twCounter})).csv";
                
          # Write in the super-script
          echo "script ./learn_${FILE_NAME}_t$((${twCounter})).a" >> $scriptFile;

          echo "clean-global" >> $scriptFile;

          fromFile="";

          if [ ${FILE_NAME} = "random" ]; then
            fromFile="fromFile:${allConfigFile}";
          fi

          numConfigs="asTW${twCounter}";

          # Write in a-file
          > ${file};
          echo "log ${scriptPath}${OUT_PREFIX}${FILE_NAME}_t$((${twCounter}))${LOG_SUFIX}" >> ${file};
          echo "solver z3" >> ${file}
          echo "vm ${path}FeatureModel.xml" >> ${file};
          if [ "${SAMPLING_STRATEGY}" = "select-all-measurements true" ]; then
            echo "${SAMPLING_STRATEGY}" >> ${file};
          elif [ "${SAMPLING_STRATEGY}" = "binary twise" ]; then
            echo "${SAMPLING_STRATEGY} t:${twCounter}" >> ${file};
          else
            echo "${SAMPLING_STRATEGY} numConfigs:${CONFIGS_TO_SAMPLE} seed:${seed}" >> ${file};
          fi
          echo "printconfigs ${tmp}${OUT_PREFIX}${FILE_NAME}_t$((${twCounter})).csv" >> ${file};
          echo "clean-sampling" >> ${file};

        done
}

if [ $# -ne 3 ] && [ $# -ne 5 ]; then
        echo "Usage: <CaseStudy> <Strategy> <SaveLocation> [FirstIteration] [LastIteration]";
        exit;
fi

CASE_STUDY=$1;
MULTIPLICATION_FACTOR=$2;
TYPE=$2;
LOCATION=$3;
LOCATION=$(echo $LOCATION | sed 's:/*$::')
LOCATION="${LOCATION}/"
CURRENT_SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ "${TYPE}" = "twise" ]; then
  SAMPLING_STRATEGY="binary twise";
  FILE_NAME="twise";
  BEGIN_AT=1;
  REPETITIONS=1;
elif [ "${TYPE}" = "distBased" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:uniform onlyBinary:true selection:SolverSelection number-weight-optimization:1";
  # number-weight-optimization:1-1";
  FILE_NAME="distBased";
elif [ "${TYPE}" = "divDistBased" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:uniform onlyBinary:true selection:SolverSelection optimization:local number-weight-optimization:1";
  FILE_NAME="divDistBased";
elif [ "${TYPE}" = "solvBased" ]; then
  SAMPLING_STRATEGY="binary satoutput henard:false";
  FILE_NAME="solverBased";
elif [ "${TYPE}" = "rand" ]; then
  SAMPLING_STRATEGY="binary random";
  FILE_NAME="random";
elif [ "${TYPE}" = "henard" ]; then
  SAMPLING_STRATEGY="binary satoutput henard:true";
  FILE_NAME="henard";
elif [ "${TYPE}" = "all" ]; then
  SAMPLING_STRATEGY="select-all-measurements true";
  FILE_NAME="all"
  BEGIN_AT=1;
  REPETITIONS=1;
else
  echo "Only t-wise, distanceBased, diversified, solverBased, random, or henard as type."
  exit;
fi

if [ $# -eq 5 ]; then
      BEGIN_AT=$4;
      REPETITIONS=$5;
fi

# Mono variables
MONO_PATH="/usr/bin/mono"

# SPL Conqueror variables
SPL_CONQUEROR_PATH="${CURRENT_SOURCE_DIR}/../SPLConqueror/SPLConqueror/CommandLine/bin/Release/CommandLine.exe"


caseStudyPath="${CURRENT_SOURCE_DIR}/SupplementaryWebsite/FeatureModels/${CASE_STUDY}/"

for i in `seq ${BEGIN_AT} ${REPETITIONS}`; do
        echo "Run $i out of ${REPETITIONS}.";
        currentTmp="${LOCATION}${CASE_STUDY}_${i}/";
        mkdir -p $currentTmp;
        # SPL Conqueror call
        createAFiles ${caseStudyPath} ${currentTmp} ${i}
        cd ${currentTmp}

        if [ "${DRY_RUN}" = false ]; then
          echo "${MONO_PATH} ${SPL_CONQUEROR_PATH} ${currentTmp}${SUPER_SCRIPT_NAME} >> /dev/null;";
          ${MONO_PATH} ${SPL_CONQUEROR_PATH} ${currentTmp}${SUPER_SCRIPT_NAME} >> /dev/null;
        fi

        if [ $? -ne 0 ]
        then 
          echo "An error occurred when performing SPL Conqueror.";
          exit -1; 
        fi
done
