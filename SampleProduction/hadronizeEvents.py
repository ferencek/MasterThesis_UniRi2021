import os
import re
import time

mX_min = 400
#mX_min = 1400
#mX_min = 3800
#mX_max = 400
#mX_max = 3600
mX_max = 4000
mX_step = 200
mY_step = 200


failedMassPoints = []
#failedMassPoints = [[1600, 500], [3000, 260], [3000, 300], [3000, 500], [3000, 700], [3000, 900], [3000, 1100], [3000, 1300]]

sleep_minutes = 18


def processMassPoint(mX, mY,counter):
    print ('---------------------------------------')
    print ('(mX, mY) = (%i, %i)' % (mX, mY))
    print ('---------------------------------------')

    # create jdl file
    jdl_path = os.path.join(condor_folder, ('TRSM_XToHY_6b_M3_%i_M2_%i.jdl' % (mX, mY)))
    jdl_file = open(jdl_path,'w')
    jdl_content = jdl_template
    jdl_content = re.sub('DUMMY_OUTPUTDIR',condor_folder,jdl_content)
    jdl_content = re.sub('M3MASS',str(mX),jdl_content)
    jdl_content = re.sub('M2MASS',str(mY),jdl_content)
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
Output = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_M3_M3MASS_M2_M2MASS.stdout
Error = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_M3_M3MASS_M2_M2MASS.stderr
Log = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_M3_M3MASS_M2_M2MASS.log
Arguments = M3MASS M2MASS
Queue
"""


bash_template = """#!/bin/bash

M3MASS=$1
M2MASS=$2

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

cmsDriver.py Configuration/GenProduction/python/Hadronizer_TuneCP5_13TeV_generic_LHE_pythia8_noPSweights_cff.py --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --geometry DB:Extended --era Run2_2017 --customise Configuration/DataProcessing/Utils.addMonitoring --filein file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_${M3MASS}_M2_${M2MASS}.lhe --fileout file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/GEN/TRSM_XToHY_6b_M3_${M3MASS}_M2_${M2MASS}_GEN.root --python_filename config.py -n -1 --no_exec

sed -i '34,37d' config.py
sed -i '32d' config.py

cmsRun -p config.py
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_hadronize_events'
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
        processMassPoint(mp[0],mp[1],counter)
else:
    # loop over mass points
    for mX in range(mX_min, mX_max + mX_step, mX_step):
        for mY in ([260] + range(300, mX-125, mY_step)):
            counter += 1
            processMassPoint(mX,mY,counter)

print ('---------------------------------------')