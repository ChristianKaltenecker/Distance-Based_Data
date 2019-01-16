#!/bin/bash

REPETITIONS=100;
BEGIN_AT=1;
RELATIVE=false;
DRY_RUN=false;
INSERT_CONFIGS=true;
RF_SEED_REPETITIONS=10;

TW_COUNTER="1 2 3"
#FILES="pres_0 pres_1 pres_2 uni_0 uni_1 uni_2"

SAMPLED_CONFIGURATION_FILE_PREFIX="sampledConfigurations_"
OUT_PREFIX="out_"
CSV_SUFIX=".csv"
TXT_SUFIX=".txt"
LOG_SUFIX=".log"

SUPER_SCRIPT_NAME="learnAll.a"

createAFiles () {
        path=$1
        tmp=$2
        seed=$3

        scriptFile="${tmp}${SUPER_SCRIPT_NAME}"

        if [ "${RELATIVE}" = true ];
        then 
          scriptPath="./";
        else
          scriptPath=${tmp};
        fi

        > $scriptFile;
        for twCounter in $TW_COUNTER
        do
          file="${tmp}learn_${FILE_NAME}_$((${twCounter}-1)).a";
          csvFile="${path}measurements.xml";
          allConfigFile="${path}allConfigurations.csv";
          sampleFile="${scriptPath}${SAMPLED_CONFIGURATION_FILE_PREFIX}${FILE_NAME}_$((${twCounter}-1)).csv";
                
          # Write in the super-script
          if [ "${RELATIVE}" = true ];
          then
            echo "script ./learn_${FILE_NAME}_$((${twCounter}-1)).a" >> $scriptFile;
          else
            echo "script ${file}" >> $scriptFile;
          fi

          echo "clean-global" >> $scriptFile;

          fromFile="";

          if [ ${FILE_NAME} = "rand" ]; then
            fromFile="fromFile:${allConfigFile}";
          fi

          numConfigs="asTW${twCounter}";

          if [ "${INSERT_CONFIGS}" = true ]; then
            if [ "${RELATIVE}" = true ]; then
              configs=$(cat ${4}twise_${twCounter}.txt | wc -l);
            else
              configs=$(cat ${path}twise_${twCounter}.txt | wc -l);
            fi
            numConfigs="${configs}";
          fi

          # Write in a-file
          > ${file};
          echo "log ${scriptPath}${OUT_PREFIX}${FILE_NAME}_$((${twCounter}-1))${LOG_SUFIX}" >> ${file};
          echo "mlsettings bagging:False stopOnLongRound:False parallelization:True lossFunction:RELATIVE useBackward:False abortError:10 limitFeatureSize:False featureSizeTreshold:7 quadraticFunctionSupport:True crossValidation:False learn_logFunction:True numberOfRounds:70 backwardErrorDelta:1 minImprovementPerRound:0.25 withHierarchy:False" >> ${file};
          echo "solver z3" >> ${file}
          echo "vm ${path}FeatureModel.xml" >> ${file};
          echo "all ${csvFile}" >> ${file};
          echo "nfp Performance" >> ${file};
          if [ "${SAMPLING_STRATEGY}" = "select-all-measurements true" ]; then
            echo "${SAMPLING_STRATEGY}" >> ${file};
          else
            echo "${SAMPLING_STRATEGY} numConfigs:${numConfigs} seed:${seed} ${fromFile}" >> ${file};
          fi
          #echo "learn-splconqueror" >> ${file};
          echo "define-python-path /scratch/kaltenec/venv/bin" >> ${file};
          for rf_seed in `seq 1 $RF_SEED_REPETITIONS`; do
            echo "learn-python RandomForestRegressor random_state=${rf_seed}" >> ${file}
            #echo "analyze-learning" >> ${file};
          done;
          echo "printconfigs ${sampleFile}" >> ${file};
          echo "clean-sampling" >> ${file};

        done
}

if [ $# -ne 3 ] && [ $# -ne 5 ]; then
        echo "Usage: <CaseStudy> <MultiplicationFactor> <semi/geom/norm/rand/solv/all> [FirstIteration] [LastIteration]";
        exit;
fi

CASE_STUDY=$1;
MULTIPLICATION_FACTOR=$2;
TYPE=$3;

if [ "${TYPE}" = "solv" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:uniform onlyBinary:true selection:SolverSelection";
  # number-weight-optimization:1-1";
  FILE_NAME="solv";
elif [ "${TYPE}" = "binom" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:binomial onlyBinary:true selection:SolverSelection optimization:local";
  FILE_NAME="binom";
elif [ "${TYPE}" = "geom" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:geometric onlyBinary:true selection:SolverSelection optimization:local";
  FILE_NAME="geom";
elif [ "${TYPE}" = "local" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:uniform onlyBinary:true selection:SolverSelection optimization:local";
  FILE_NAME="local";
elif [ "${TYPE}" = "invgeom" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:geometric onlyBinary:true selection:DiverseSelection";
  FILE_NAME="invgeom";
elif [ "${TYPE}" = "twogeom" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:twosidedgeometric onlyBinary:true selection:SolverSelection optimization:local";
  FILE_NAME="twogeom";
elif [ "${TYPE}" = "semi" ]; then
  SAMPLING_STRATEGY="binary satoutput";
  FILE_NAME="semi";
elif [ "${TYPE}" = "rand" ]; then
  SAMPLING_STRATEGY="binary random";
  FILE_NAME="rand";
elif [ "${TYPE}" = "norm" ]; then
  SAMPLING_STRATEGY="hybrid distribution-aware distance-metric:manhattan distribution:normal use-whole-population:true onlyBinary:true optimization:local selection:SolverSelection";
  FILE_NAME="norm";
elif [ "${TYPE}" = "all" ]; then
  SAMPLING_STRATEGY="select-all-measurements true";
  FILE_NAME="all"
  BEGIN_AT=1;
  REPETITIONS=1;
else
  echo "Only solv, binom, geom, norm, semi, or rand as type."
  exit;
fi

if [ $# -eq 5 ]; then
      BEGIN_AT=$4;
      REPETITIONS=$5;
fi

PREFIX="/scratch/kaltenec/Distribution-Aware-Sampling/"

# Mono variables
MONO_PATH="/usr/bin/mono"

# Python variables
PYTHON_PATH="/usr/bin/python3"
PYTHON_SCRIPT="${PREFIX}Scripts/SampleConverter.py"

# SPL Conqueror variables
SPL_CONQUEROR_PATH="/scratch/kaltenec/SPLConqueror/SPLConqueror/CommandLine/bin/Release/CommandLine.exe"

if [ "${RELATIVE}" = true ]; 
then
  SOURCE_PATH="../"
  REAL_PATH="${PREFIX}DistOut/ConstraintData/"
else
  SOURCE_PATH="${PREFIX}DistOut/ConstraintData/"
fi

TMP_PATH="/scratch/kaltenec/Distribution-Aware-Sampling/Results_RF/${CASE_STUDY}/"

if [ "${RELATIVE}" = true ];
then
  caseStudyPath="${SOURCE_PATH}";
  realCaseStudyPath="${REAL_PATH}${CASE_STUDY}/"
else
  caseStudyPath="${SOURCE_PATH}${CASE_STUDY}/"
fi

for i in `seq ${BEGIN_AT} ${REPETITIONS}`; do
        echo "Run $i out of ${REPETITIONS}.";
        currentTmp="${TMP_PATH}${CASE_STUDY}_${i}/";
        mkdir -p $currentTmp;
        # SPL Conqueror call
        if [ "${DRY_RUN}" = false ] || [ "${INSERT_CONFIGS}" = false ]; then
          createAFiles ${caseStudyPath} ${currentTmp} ${i}
        else
          createAFiles ${caseStudyPath} ${currentTmp} ${i} ${realCaseStudyPath}
        fi
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
        
        if [ "${DRY_RUN}" = false ]; then
          # Python call
          for twCounter in $TW_COUNTER 
          do
            echo ${PYTHON_PATH} ${PYTHON_SCRIPT} ${currentTmp}${SAMPLED_CONFIGURATION_FILE_PREFIX}${FILE_NAME}_$((${twCounter} - 1)).csv ${MULTIPLICATION_FACTOR}
            ${PYTHON_PATH} ${PYTHON_SCRIPT} ${currentTmp}${SAMPLED_CONFIGURATION_FILE_PREFIX}${FILE_NAME}_$((${twCounter} - 1)).csv ${MULTIPLICATION_FACTOR}
          done
        fi
done
