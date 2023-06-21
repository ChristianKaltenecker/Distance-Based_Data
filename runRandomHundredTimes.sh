#!/bin/bash

REPETITIONS=100;
BEGIN_AT=1;
DRY_RUN=false;
INSERT_CONFIGS=true;

CONFIG_COUNTER="10 100 1000"

SAMPLED_CONFIGURATION_FILE_PREFIX="sampledConfigurations_"
OUT_PREFIX="out_"
LOG_SUFIX=".log"

SUPER_SCRIPT_NAME="learnAll.sh"

createAFiles () {
        path=$1
        tmp=$2
        seed=$3

        scriptFile="${tmp}${SUPER_SCRIPT_NAME}"


        scriptPath="./";

        echo "#/bin/bash" > $scriptFile;
        echo "set -e" >> $scriptFile;
        for twCounter in $CONFIG_COUNTER
        do
          file="${tmp}learn_${FILE_NAME}_$((${twCounter})).a";
          sampleFile="${scriptPath}${SAMPLED_CONFIGURATION_FILE_PREFIX}${FILE_NAME}_$((${twCounter})).csv";

          echo "timeout 10s ${MONO_PATH} ${SPL_CONQUEROR_PATH} ${file}" >> $scriptFile;

          # Write in a-file
          true > ${file};
          echo "log ${scriptPath}${OUT_PREFIX}${FILE_NAME}_$((${twCounter}))${LOG_SUFIX}" >> ${file};
          echo "solver z3" >> ${file}
          echo "vm ${path}FeatureModel.xml" >> ${file};
          if [ "${SAMPLING_STRATEGY}" = "select-all-measurements true" ]; then
            echo "${SAMPLING_STRATEGY}" >> ${file};
          elif [ "${SAMPLING_STRATEGY}" = "binary twise" ]; then
            echo "${SAMPLING_STRATEGY} t:${twCounter}" >> ${file};
          else
            echo "${SAMPLING_STRATEGY} numConfigs:${twCounter} seed:${seed}" >> ${file};
          fi
          echo "printconfigs ${sampleFile}" >> ${file};
          echo "clean-sampling" >> ${file};

        done
}

if [ $# -ne 3 ] && [ $# -ne 5 ]; then
        echo "Usage: <CaseStudy> <SAMPLING_STRATEGY> <SaveLocation> [FirstIteration] [LastIteration]";
        exit;
fi

CASE_STUDY=$1;
SAMPLING_STRATEGY=$2;
LOCATION=$3;
LOCATION=$(echo $LOCATION | sed 's:/*$::')
LOCATION="${LOCATION}/"
CURRENT_SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ "${SAMPLING_STRATEGY}" = "twise" ]; then
  SAMPLING_STRATEGY="binary twise";
  FILE_NAME="twise";
  BEGIN_AT=1;
  REPETITIONS=1;
elif [ "${SAMPLING_STRATEGY}" = "distBased" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:uniform onlyBinary:true selection:SolverSelection number-weight-optimization:1";
  # number-weight-optimization:1-1";
  FILE_NAME="distBased";
elif [ "${SAMPLING_STRATEGY}" = "divDistBased" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:uniform onlyBinary:true selection:SolverSelection optimization:local number-weight-optimization:1";
  FILE_NAME="divDistBased";
elif [ "${SAMPLING_STRATEGY}" = "solvBased" ]; then
  SAMPLING_STRATEGY="binary satoutput henard:false";
  FILE_NAME="solverBased";
elif [ "${SAMPLING_STRATEGY}" = "rand" ]; then
  SAMPLING_STRATEGY="binary random";
  FILE_NAME="random";
elif [ "${SAMPLING_STRATEGY}" = "henard" ]; then
  SAMPLING_STRATEGY="binary satoutput henard:true";
  FILE_NAME="henard";
elif [ "${SAMPLING_STRATEGY}" = "all" ]; then
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
twisePath="${CURRENT_SOURCE_DIR}/SupplementaryWebsite/PerformancePredictions/Summary/${CASE_STUDY}/"

for i in `seq ${BEGIN_AT} ${REPETITIONS}`; do
        echo "Run $i out of ${REPETITIONS}.";
        currentTmp="${LOCATION}${CASE_STUDY}_${i}/";
        mkdir -p $currentTmp;
        # SPL Conqueror call
        createAFiles ${caseStudyPath} ${currentTmp} ${i} ${twisePath}
        cd ${currentTmp}

	      if [ "${DRY_RUN}" = false ]; then
	        chmod +x ${currentTmp}${SUPER_SCRIPT_NAME};
          echo "/usr/bin/numactl --cpubind=0 --membind=0 bash ${currentTmp}${SUPER_SCRIPT_NAME};";
          /usr/bin/numactl --cpubind=0 --membind=0 bash ${currentTmp}${SUPER_SCRIPT_NAME};
        fi

        error=$?

        if [ $error == 124 ]
        then
          echo "Timeout!";
          exit 0;
        elif [ $error -ne 0 ]
        then 
          echo "An error occurred when performing SPL Conqueror.";
          exit 255;
        fi
done
