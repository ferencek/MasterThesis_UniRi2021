import os
import re
import time
import datetime

# regular mass points
mX_min = 400
#mX_min = 600
#mX_max = 400
mX_max = 4000
mX_step = 200
mY_step = 200

failedMassPoints = []
#failedMassPoints = [[3200, 2700], [3200, 2900], [3400, 260], [3400, 1100], [3400, 1300], [3400, 1500], [3600, 1900], [3600, 2100], [3600, 2300], [3600, 2500], [3600, 2700], [3600, 2900], [3800, 900], [3800, 1300], [3800, 1500], [4000, 1500], [4000, 1700]]

# benchmark points
massPoints_BP = ['M3_1600_M2_500_BPb', 'M3_2000_M2_300_BPd', 'M3_2000_M2_800_BPe', 'M3_2500_M2_300_BPf']
failedMassPoints_BP = []

sleep_minutes = 10


from optparse import OptionParser
parser = OptionParser()

parser.add_option('--bp', dest="bp", action='store_true',
                  help="Process TRSM benchmark points",
                  default=False)

parser.add_option('--pu', dest="pu", action='store_true',
                  help="Add pileup",
                  default=False)

(options, args) = parser.parse_args()


if not options.bp:
    failedMassPoints_str = []
    for mp in failedMassPoints:
        failedMassPoints_str.append('M3_%i_M2_%i' % (mp[0],mp[1]))
    failedMassPoints = failedMassPoints_str
else:
    failedMassPoints = failedMassPoints_BP

massPoints = []
if not options.bp:
    # loop over mass points
    for mX in range(mX_min, mX_max + mX_step, mX_step):
        for mY in ([260] + range(300, mX-125, mY_step)):
            massPoints.append('M3_%i_M2_%i' % (mX,mY))
else:
    massPoints = massPoints_BP


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
#Requirements = (OpSysAndVer == "CentOS7" && machine != "lorientree02.hep.zef.irb.hr" )
Executable = DUMMY_OUTPUTDIR/runDelphes.sh
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
cd ../..

export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

wget http://cp3.irmp.ucl.ac.be/downloads/Delphes-3.5.0.tar.gz
tar zxf Delphes-3.5.0.tar.gz

cd Delphes-3.5.0
ROOTCFLAGS=$(root-config --cflags --libs)
sed -i 's/-std=c++0x //g' Makefile
make -j 6

./DelphesCMSFWLite /users/ferencek/TRSM_production/delphes_card_CMS.tcl /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/DelphesCMS/TRSM_XToHY_6b_${MASSPOINT}_DelphesCMS.root /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/GEN/TRSM_XToHY_6b_${MASSPOINT}_GEN.root
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_delphes'
if options.bp:
    condor_folder += '_BP'
if options.pu:
    condor_folder += '_PU'
condor_folder = condor_folder + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
os.system('mkdir -p ' + condor_folder)

# create Bash script
bash_path = os.path.join(condor_folder,'runDelphes.sh')
bash_script = open(bash_path,'w')
bash_content = bash_template
if options.pu:
    bash_content = re.sub('delphes_card_CMS.tcl','delphes_card_CMS_PileUp.tcl',bash_content)
    bash_content = re.sub('_DelphesCMS.root','_DelphesCMSPileUp.root',bash_content)
bash_script.write(bash_content)
bash_script.close()
os.system('chmod +x ' + bash_path)

counter = 0

if len(failedMassPoints):
    for mp in failedMassPoints:
        counter += 1
        processMassPoint(mp,counter)
else:
    for mp in massPoints:
        counter += 1
        processMassPoint(mp,counter)

print ('---------------------------------------')
