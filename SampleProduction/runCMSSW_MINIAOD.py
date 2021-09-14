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
    jdl_content = re.sub('DUMMY_JOB',(job if singleJobs else '$(process)'),jdl_content)
    jdl_content = re.sub('DUMMY_QUEUE',('' if singleJobs else '100'),jdl_content)
    jdl_file.write(jdl_content)
    jdl_file.close()

    # submit Condor job
    os.system('condor_submit ' + jdl_path)


jdl_template = """universe = vanilla
Notification = never
Executable = DUMMY_OUTPUTDIR/CMSSW_MINIAOD.sh
Output = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT_DUMMY_JOB.stdout
Error = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT_DUMMY_JOB.stderr
Log = DUMMY_OUTPUTDIR/TRSM_XToHY_6b_DUMMY_MASSPOINT_DUMMY_JOB.log
Arguments = DUMMY_JOB DUMMY_MASSPOINT 100
Queue DUMMY_QUEUE
"""

# CMSSW cfg files below based on the matrix workflow 10224.0
# runTheMatrix.py -n | grep 2017 | grep -i ttbar
# runTheMatrix.py -nel 10224.0

# Pileup sample
# /RelValMinBias_13/CMSSW_10_5_0_pre1-103X_mc2017_realistic_v2-v1/GEN-SIM
# Dataset size: 18489831073 (18.5GB) Number of blocks: 1 Number of events: 90000 Number of files: 7 Creation time: 2019-01-30 11:30:37 Site name: T1_US_FNAL_Disk, T2_US_Nebraska, T2_US_Purdue Release name: CMSSW_10_5_0_pre1

# Below adding lines to the CMSSW cfg file which set the random seeds to different values every time a job is run
# (from https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePythonTips?redirectedfrom=CMS.SWGuidePythonTips#Reset_the_random_seeds_every_tim)
bash_template = """#!/bin/bash

CONDOR_PROCESS=$1
MASSPOINT=$2
MAXEVENTS=$3

START_TIME=`/bin/date`
echo "Started at $START_TIME"
echo ""

cd ${_CONDOR_SCRATCH_DIR}

export HOME=/users/ferencek

source /cvmfs/cms.cern.ch/cmsset_default.sh
scram project CMSSW CMSSW_10_6_25
cd CMSSW_10_6_25/src/
eval `scram runtime -sh`

let "SKIP = $CONDOR_PROCESS * MAXEVENTS"

cmsDriver.py rawsim --mc --conditions auto:phase1_2017_realistic -n ${MAXEVENTS} --era Run2_2017 --eventcontent RAWSIM -s SIM,DIGI,L1,DIGI2RAW,HLT:@relval2017 --datatier GEN-SIM-DIGI-RAW --pileup AVE_35_BX_25ns --geometry DB:Extended --python_filename produceRAWSIM.py --filein file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/GEN/TRSM_XToHY_6b_${MASSPOINT}_GEN.root --no_exec

sed -i '121ifrom IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper\\nrandSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)\\nrandSvc.populate()' produceRAWSIM.py
sed -i "92iprocess.mix.input.fileNames = cms.untracked.vstring(['file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/224DA2A6-BA5A-FE44-8888-9608E3C3491F.root', 'file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/22947840-2543-6A4A-B2BD-B9155495D0B3.root', 'file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/2C3F1D6A-E892-1D44-9A70-E4E0E609694B.root', 'file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/3342EB73-02EB-6346-B81B-3A7635DE89C2.root', 'file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/53101FB7-F71D-2D46-BF45-FE15E6D0E5E2.root', 'file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/ABFA3921-52E7-134C-87B6-D58052402997.root', 'file:/STORE/ferencek/Pixel/mc/relval/CMSSW_10_5_0_pre1/RelValMinBias_13/GEN-SIM/103X_mc2017_realistic_v2-v1/20000/ACB3CEC8-09F0-174B-AD93-84BA32EED0C5.root'])" produceRAWSIM.py
sed -i '56i\ \ \ \ skipEvents = cms.untracked.uint32('"${SKIP}"'),' produceRAWSIM.py

cmsRun -p produceRAWSIM.py

cmsDriver.py miniaodsim  --conditions auto:phase1_2017_realistic -n ${MAXEVENTS} --era Run2_2017 --eventcontent MINIAODSIM --runUnscheduled -s RAW2DIGI,L1Reco,RECO,RECOSIM,EI,PAT --datatier MINIAODSIM --geometry DB:Extended --python_filename produceMINIAODSIM.py --filein file:rawsim_SIM_DIGI_L1_DIGI2RAW_HLT_PU.root --fileout file:/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/MINIAOD/TRSM_XToHY_6b_${MASSPOINT}_MINIAOD_${CONDOR_PROCESS}.root --no_exec

cmsRun -p produceMINIAODSIM.py
exitcode=$?

echo ""
END_TIME=`/bin/date`
echo "Finished at $END_TIME"
exit $exitcode
"""


condor_folder = 'condor_CMSSW_MINIAOD'
if options.bp:
    condor_folder += '_BP'
condor_folder = condor_folder + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
os.system('mkdir -p ' + condor_folder)

# create Bash script
bash_path = os.path.join(condor_folder,'CMSSW_MINIAOD.sh')
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
