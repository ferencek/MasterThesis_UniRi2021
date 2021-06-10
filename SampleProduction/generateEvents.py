import os
import re

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

def processMassPoint(mX, mY):
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


jdl_template = """universe = vanilla
Notification = never
Executable = DUMMY_OUTPUTDIR/generateEvents.sh
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
mkdir work
cd work
tar xf /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/gridpacks/madgraph/V5_2.6.1/TRSM_XToHY_6b_M3_${M3MASS}_M2_${M2MASS}_slc7_amd64_gcc700_CMSSW_10_6_0_tarball.tar.xz

NEVENTS=10000
RANDOMSEED=12345
NCPU=1
./runcmsgrid.sh $NEVENTS $RANDOMSEED $NCPU

mv -v cmsgrid_final.lhe /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_${M3MASS}_M2_${M2MASS}.lhe
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_generate_events'
os.system('mkdir -p ' + condor_folder)

# create Bash script
bash_path = os.path.join(condor_folder,'generateEvents.sh')
bash_script = open(bash_path,'w')
bash_script.write(bash_template)
bash_script.close()
os.system('chmod +x ' + bash_path)

if len(failedMassPoints):
    for mp in failedMassPoints:
        processMassPoint(mp[0],mp[1])
else:
    # loop over mass points
    for mX in range(mX_min, mX_max + mX_step, mX_step):
        for mY in ([260] + range(300, mX-125, mY_step)):
            processMassPoint(mX,mY)

print ('---------------------------------------')
