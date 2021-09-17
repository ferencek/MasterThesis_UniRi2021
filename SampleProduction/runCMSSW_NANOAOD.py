import os
import re
import time
import datetime

# regular mass points
mX_min = 400
mX_max = 4000
mX_step = 400
mY_step = 400


failedMassPoints = []
#failedMassPoints = [[1600, 500], [3000, 260], [3000, 300], [3000, 500], [3000, 700], [3000, 900], [3000, 1100], [3000, 1300]]

failedJobsList = ''
# grep 'return value' path/to/Condor/folder/*.log | grep -v 'return value 0' > failed_jobs.txt
#failedJobsList = 'failed_jobs.txt'

# benchmark points
massPoints_BP = ['M3_1600_M2_500_BPb', 'M3_2000_M2_300_BPd', 'M3_2000_M2_800_BPe', 'M3_2500_M2_300_BPf']
failedMassPoints_BP = []


from optparse import OptionParser
parser = OptionParser()

parser.add_option('--bp', dest="bp", action='store_true',
                  help="Process TRSM benchmark points",
                  default=False)

(options, args) = parser.parse_args()


if not options.bp:
    if not failedJobsList:
        failedMassPoints_str = []
        for mp in failedMassPoints:
            failedMassPoints_str.append('M3_%i_M2_%i' % (mp[0],mp[1]))
        failedMassPoints = failedMassPoints_str
    else:
        job_list = open(failedJobsList, 'rb').read().splitlines()
        for job in job_list:
            failedMassPoints.append(job.split()[0].replace('TRSM_XToHY_6b_','').replace('.log:',''))
else:
    failedMassPoints = failedMassPoints_BP

massPoints = []
if not options.bp:
    # loop over mass points
    for mX in range(mX_min, mX_max + mX_step, mX_step):
        for mY in sorted(list(set([260,mX-140])) + range(300, mX-125, mY_step)):
            massPoints.append('M3_%i_M2_%i' % (mX,mY))
else:
    massPoints = massPoints_BP


def processMassPoint(massPoint):
    print ('---------------------------------------')
    print ('mass point = %s' % massPoint)
    print ('---------------------------------------')

    # create jdl file
    jdl_path = os.path.join(condor_folder, ('TRSM_XToHY_6b_%s.jdl' % massPoint))
    jdl_file = open(jdl_path,'w')

    # figure out if individual failed jobs are being resubmitted
    singleJobs = False
    job = ''
    if re.search('_\w+_\d+_\d+$', massPoint) or re.search('_BP\w+_\d+$', massPoint):
        singleJobs = True
        job = massPoint.split('_')[-1]
        massPoint = re.split('_\d+$', massPoint)[0]

    jdl_content = jdl_template
    jdl_content = re.sub('DUMMY_OUTPUTDIR',condor_folder,jdl_content)
    jdl_content = re.sub('DUMMY_MASSPOINT',massPoint,jdl_content)
    jdl_file.write(jdl_content)
    jdl_file.close()

    # submit Condor job
    os.system('condor_submit ' + jdl_path)


jdl_template = """universe = vanilla
Notification = never
Executable = DUMMY_OUTPUTDIR/CMSSW_NANOAOD.sh
Output = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT.stdout
Error = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT.stderr
Log = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT.log
Arguments = DUMMY_MASSPOINT
Queue
"""

# CMSSW cfg files below based on the matrix workflow 1325.61
# runTheMatrix.py -n | grep 2017 | grep -i ttbar
# runTheMatrix.py -nel 1325.61

bash_template = """#!/bin/bash

MASSPOINT=$1

START_TIME=`/bin/date`
echo "Started at $START_TIME"
echo ""

cd ${_CONDOR_SCRATCH_DIR}

export HOME=/users/ferencek

source /cvmfs/cms.cern.ch/cmsset_default.sh
scram project CMSSW CMSSW_10_6_25
cd CMSSW_10_6_25/src/
eval `scram runtime -sh`

cmsDriver.py nanoaodsim --conditions auto:phase1_2017_realistic -s NANO --datatier NANOAODSIM -n -1 --era Run2_2017,run2_nanoAOD_106Xv1 --mc --eventcontent NANOAODSIM --python_filename produceNANOAODSIM.py --filein file:input.root --fileout file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/NANOAOD/TRSM_XToHY_6b_${MASSPOINT}_NANOAOD.root --no_exec

sed -i '7iimport glob' produceNANOAODSIM.py
sed -i "s|'file:input.root'|'file:'\ +\ f\ for\ f\ in\ glob.glob('/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/MINIAOD/TRSM_XToHY_6b_${MASSPOINT}_MINIAOD_*.root')|g" produceNANOAODSIM.py

cmsRun -p produceNANOAODSIM.py
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_CMSSW_NANOAOD'
if options.bp:
    condor_folder += '_BP'
condor_folder = condor_folder + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
os.system('mkdir -p ' + condor_folder)

# create Bash script
bash_path = os.path.join(condor_folder,'CMSSW_NANOAOD.sh')
bash_script = open(bash_path,'w')
bash_script.write(bash_template)
bash_script.close()
os.system('chmod +x ' + bash_path)


if len(failedMassPoints):
    for mp in failedMassPoints:
        processMassPoint(mp)
else:
    for mp in massPoints:
        processMassPoint(mp)

print ('---------------------------------------')
