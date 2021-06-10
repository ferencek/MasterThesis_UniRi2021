import os
import re
import time


massPoints = ['M3_1600_M2_500_BPb', 'M3_2000_M2_300_BPd', 'M3_2000_M2_800_BPe', 'M3_2500_M2_300_BPf']
failedMassPoints = []

sleep_minutes = 18


def processMassPoint(massPoint,counter):
    print ('---------------------------------------')
    print ('mass point = %s' % massPoint)
    print ('---------------------------------------')

    # create jdl file
    jdl_path = os.path.join(condor_folder, ('TRSM_XToHY_6b_%s.jdl' % massPoint))
    jdl_file = open(jdl_path,'w')
    jdl_content = jdl_template
    jdl_content = re.sub('DUMMY_OUTPUTDIR',condor_folder,jdl_content)
    jdl_content = re.sub('DUMMY_MASSPOINT',massPoint,jdl_content)
    jdl_file.write(jdl_content)
    jdl_file.close()

    # submit Condor job
    os.system('condor_submit ' + jdl_path)

    if counter%40 == 0:
        print ('Sleeping... zZZzz  zZZzz zZZzz')
        time.sleep(sleep_minutes * 60)
        print ('Just woke up. Continuing...')


jdl_template = """universe = vanilla
Notification = never
Executable = DUMMY_OUTPUTDIR/hadronizeEvents.sh
Output = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT.stdout
Error = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT.stderr
Log = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT.log
Arguments = DUMMY_MASSPOINT
Queue
"""


bash_template = """#!/bin/bash

MASSPOINT=$1

START_TIME=`/bin/date`
echo "Started at $START_TIME"
echo ""

cd ${_CONDOR_SCRATCH_DIR}

source /cvmfs/cms.cern.ch/cmsset_default.sh
scram project CMSSW CMSSW_10_6_0
cd CMSSW_10_6_0/src/
eval `scram runtime -sh`
mkdir -p Configuration/GenProduction/python/
wget https://raw.githubusercontent.com/cms-sw/genproductions/3aacccd15d69b1ba71a61e855db283a63f3ed02d/genfragments/ThirteenTeV/Hadronizer/Hadronizer_TuneCP5_13TeV_generic_LHE_pythia8_noPSweights_cff.py -P Configuration/GenProduction/python/
scram b
cd ../..

cmsDriver.py Configuration/GenProduction/python/Hadronizer_TuneCP5_13TeV_generic_LHE_pythia8_noPSweights_cff.py --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --geometry DB:Extended --era Run2_2017 --customise Configuration/DataProcessing/Utils.addMonitoring --filein file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_${MASSPOINT}.lhe --fileout file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/GEN/TRSM_XToHY_6b_${MASSPOINT}_GEN.root --python_filename config.py -n -1 --no_exec

sed -i '34,37d' config.py
sed -i '32d' config.py

cmsRun -p config.py
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_hadronize_events_BP'
os.system('mkdir -p ' + condor_folder)

# create Bash script
bash_path = os.path.join(condor_folder,'hadronizeEvents.sh')
bash_script = open(bash_path,'w')
bash_script.write(bash_template)
bash_script.close()
os.system('chmod +x ' + bash_path)

counter = 0

if len(failedMassPoints):
    for mp in failedMassPoints:
        counter += 1
        processMassPoint(mp,counter)
else:
    # loop over mass points
    for mp in massPoints:
        counter += 1
        processMassPoint(mp,counter)

print ('---------------------------------------')
