#/bin/bash
set -e
timeout 3h /usr/bin/mono /scratch/kaltenec/Distance-Based_Scalability/Scripts/../../SPLConqueror/SPLConqueror/CommandLine/bin/Release/CommandLine.exe /scratch/kaltenec/Distance-Based_Scalability/Results/Linux-6.2.1_1/learn_divDistBased_10.a
timeout 3h /usr/bin/mono /scratch/kaltenec/Distance-Based_Scalability/Scripts/../../SPLConqueror/SPLConqueror/CommandLine/bin/Release/CommandLine.exe /scratch/kaltenec/Distance-Based_Scalability/Results/Linux-6.2.1_1/learn_divDistBased_100.a
timeout 3h /usr/bin/mono /scratch/kaltenec/Distance-Based_Scalability/Scripts/../../SPLConqueror/SPLConqueror/CommandLine/bin/Release/CommandLine.exe /scratch/kaltenec/Distance-Based_Scalability/Results/Linux-6.2.1_1/learn_divDistBased_1000.a
