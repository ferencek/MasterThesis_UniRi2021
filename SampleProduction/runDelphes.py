import os
import re
import time

mX_min = 400
#mX_min = 600
#mX_max = 400
mX_max = 4000
mX_step = 200
mY_step = 200


failedMassPoints = []
#failedMassPoints = [[3200, 2700], [3200, 2900], [3400, 260], [3400, 1100], [3400, 1300], [3400, 1500], [3600, 1900], [3600, 2100], [3600, 2300], [3600, 2500], [3600, 2700], [3600, 2900], [3800, 900], [3800, 1300], [3800, 1500], [4000, 1500], [4000, 1700]]

sleep_minutes = 10


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
#Requirements = (OpSysAndVer == "CentOS7" && machine != "lorientree02.hep.zef.irb.hr" )
Executable = DUMMY_OUTPUTDIR/runDelphes.sh
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
cd ../..

export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

wget http://cp3.irmp.ucl.ac.be/downloads/Delphes-3.4.2.tar.gz
tar zxf Delphes-3.4.2.tar.gz

cd Delphes-3.4.2
ROOTCFLAGS=$(root-config --cflags --libs)
sed -i 's/-std=c++0x //g' Makefile
make -j 6

./DelphesCMSFWLite cards/delphes_card_CMS.tcl /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/DelphesCMS/TRSM_XToHY_6b_M3_${M3MASS}_M2_${M2MASS}_DelphesCMS.root /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/GEN/TRSM_XToHY_6b_M3_${M3MASS}_M2_${M2MASS}_GEN.root
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_delphes'
os.system('mkdir -p ' + condor_folder)

# create Bash script
bash_path = os.path.join(condor_folder,'runDelphes.sh')
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
