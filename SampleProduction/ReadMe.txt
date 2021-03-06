-------------------------------------------
TRSM gridpacks
-------------------------------------------

# Initial code setup

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /home/ferencek/TRSM_production/
git clone -b cmsdas2020 --depth=1 https://github.com/agrohsje/genproductions.git genprod_mg261_slc7


# Manual gridpack production

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /home/ferencek/TRSM_production/genprod_mg261_slc7/bin/MadGraph5_aMCatNLO
time ./gridpack_generation.sh TRSM_XToHY_6b_M3_3000_M2_300 ../../../../../../STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/TRSM_XToHY_6b_M3_3000_M2_300 local


# Automated gridpack production

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /home/ferencek/TRSM_production/
python -u produceGridpacks.py |& tee gridpack_production_`date "+%Y%m%d_%H%M%S"`.log

# Move/copy gridpacks to STORE
mv -v /home/ferencek/TRSM_production/genprod_mg261_slc7/bin/MadGraph5_aMCatNLO/TRSM_XToHY_6b_*_tarball.tar.xz /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/gridpacks/madgraph/V5_2.6.1/

or better

rsync -avPSh --no-r --include="TRSM_XToHY_6b_*_tarball.tar.xz" --exclude="*" /home/ferencek/TRSM_production/genprod_mg261_slc7/bin/MadGraph5_aMCatNLO/* /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/gridpacks/madgraph/V5_2.6.1/

# Clean gridpacks production area
rm -rf /home/ferencek/TRSM_production/genprod_mg261_slc7/bin/MadGraph5_aMCatNLO/TRSM_XToHY_6b_*


# Submit Condor jobs to generate events
cd /users/ferencek/TRSM_production/
python generateEvents.py


# Submit Condor jobs to hadronize events
cd /users/ferencek/TRSM_production/
python hadronizeEvents.py


# Submit Condor jobs to run Delphes (--pu adds pileup)
cd /users/ferencek/TRSM_production/
python runDelphes.py
python runDelphes.py --pu

###################
Delphes samples turned out to be buggy as far as the pileup simulation was concerned.
The effect of pileup on the jet mass seemed greatly underestimated. The samples
were finally not used.
###################

# Submit Condor jobs to run CMSSW and produce MINIAOD files with pileup overlaid
cd /users/ferencek/TRSM_production/
python runCMSSW_MINIAOD.py

# Submit Condor jobs to run CMSSW and produce NANOAOD files
cd /users/ferencek/TRSM_production/
python runCMSSW_NANOAOD.py


# To check for missing files and get a list of failed mass points
python checkOutput.py path/to/output/files/

-------------------------------------------
TRSM benchmark points - New model
-------------------------------------------
# Generate events

There are 4 benchmark points considered

TRSM_XToHY_6b_M3_1600_M2_500_BPb
TRSM_XToHY_6b_M3_2000_M2_300_BPd
TRSM_XToHY_6b_M3_2000_M2_800_BPe
TRSM_XToHY_6b_M3_2500_M2_300_BPf

whose parameter values are defined in TRSM_benchmark_points.dat. Below TRSM_XToHY_6b_M3_2000_M2_300_BPd is used as an example

cd /users/ferencek/CMSDAS_2020/MCGen/
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
scram project CMSSW CMSSW_10_6_5
cd CMSSW_10_6_5
cmsenv
cd ..
git clone https://gitlab.com/apapaefs/twosinglet.git
cd twosinglet/twosinglet_scalarcouplings/

Modify parameter values at the bottom of twosinglet_generatecard.py to those for TRSM_XToHY_6b_M3_2000_M2_300_BPd and then run

python twosinglet_generatecard.py

Set decay width for eta and iota to auto

sed -i "/DECAY 99925/c\DECAY 99925 auto # Weta" param_card.dat
sed -i "/DECAY 99926/c\DECAY 99926 auto # Wiota" param_card.dat

and copy the final param_card.dat to the desired location

cp -p param_card.dat /STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/TRSM_XToHY_6b_M3_2000_M2_300_BPd/TRSM_XToHY_6b_M3_2000_M2_300_BPd_param_card.dat

Card files for TRSM_XToHY_6b_M3_2000_M2_300_BPd:

/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/TRSM_XToHY_6b_M3_2000_M2_300_BPd/TRSM_XToHY_6b_M3_2000_M2_300_BPd_proc_card.dat
/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/TRSM_XToHY_6b_M3_2000_M2_300_BPd/TRSM_XToHY_6b_M3_2000_M2_300_BPd_param_card.dat
/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/TRSM_XToHY_6b_M3_2000_M2_300_BPd/TRSM_XToHY_6b_M3_2000_M2_300_BPd_run_card.dat
/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/TRSM_XToHY_6b_M3_2000_M2_300_BPd/TRSM_XToHY_6b_M3_2000_M2_300_BPd_madspin_card.dat

cd /users/ferencek/CMSDAS_2020/MCGen
wget https://cms-project-generators.web.cern.ch/cms-project-generators/MG5_aMC_v2.6.1.tar.gz
tar xf MG5_aMC_v2.6.1.tar.gz
cd MG5_aMC_v2_6_1

./bin/mg5_aMC

set group_subprocesses Auto
import model loop_sm_twoscalar
generate p p > h h h [QCD]
output TRSM_XToHY_6b_M3_2000_M2_300_BPd -nojpeg

launch

Turn off analysis and turn on MadSpin

Load the above param_card.dat, run_card.dat and madspin_card.dat and let it run.

Exit when done

quit


References:

https://answers.launchpad.net/mg5amcnlo/+question/270858
https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/MadSpin#Fulllistofoptions
-------------------
# Copy LHE files and fix particle ID codes

gunzip -c /users/ferencek/CMSDAS_2020/MCGen/MG5_aMC_v2_6_1/TRSM_XToHY_6b_M3_1600_M2_500_BPb/Events/run_01_decayed_1/unweighted_events.lhe.gz > /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_1600_M2_500_BPb.lhe
gunzip -c /users/ferencek/CMSDAS_2020/MCGen/MG5_aMC_v2_6_1/TRSM_XToHY_6b_M3_2000_M2_300_BPd/Events/run_01_decayed_1/unweighted_events.lhe.gz > /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_2000_M2_300_BPd.lhe
gunzip -c /users/ferencek/CMSDAS_2020/MCGen/MG5_aMC_v2_6_1/TRSM_XToHY_6b_M3_2000_M2_800_BPe/Events/run_01_decayed_1/unweighted_events.lhe.gz > /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_2000_M2_800_BPe.lhe
gunzip -c /users/ferencek/CMSDAS_2020/MCGen/MG5_aMC_v2_6_1/TRSM_XToHY_6b_M3_2500_M2_300_BPf/Events/run_01_decayed_1/unweighted_events.lhe.gz > /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_2500_M2_300_BPf.lhe

sed -i 's/ 99925 / 35 /g;s/ 99926 / 36 /g' /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_1600_M2_500_BPb.lhe
sed -i 's/ 99925 / 35 /g;s/ 99926 / 36 /g' /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_2000_M2_300_BPd.lhe
sed -i 's/ 99925 / 35 /g;s/ 99926 / 36 /g' /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_2000_M2_800_BPe.lhe
sed -i 's/ 99925 / 35 /g;s/ 99926 / 36 /g' /users/ferencek/store/TRSM_XToHY_6b/2017/13TeV/LHE/TRSM_XToHY_6b_M3_2500_M2_300_BPf.lhe


# Submit Condor jobs to hadronize events
cd /users/ferencek/TRSM_production/
python hadronizeEvents.py --bp


# Submit Condor jobs to run Delphes (--pu adds pileup)
cd /users/ferencek/TRSM_production/
python runDelphes.py --bp
python runDelphes.py --bp --pu

###################
Delphes samples turned out to be buggy as far as the pileup simulation was concerned.
The effect of pileup on the jet mass seemed greatly underestimated. The samples
were finally not used.
###################
-------------------------------------------
Warnings encountered:


generate p p > h h h [QCD]

WARNING: Some loop diagrams contributing to this process are discarded because they are not pure (QCD)-perturbation.
Make sure you did not want to include them.

launch

Please note that the automatic computation of the width is
    only valid in narrow-width approximation and at tree-level.

--> Tania said these are safe to ignore


This is how MadSpin was crashing before loading the heft model to perform h > b b~ decays

INFO: generating the production square matrix element
INFO: generate p p > h h h   --no_warning=duplicate;define pert_QCD = -4 -3 -2 -1 1 2 3 4 21;add process p p > h h h  pert_QCD  --no_warning=duplicate; 
Command "generate_events run_01" interrupted with error:
NoDiagramException : No amplitudes generated from process Process: g/u/c/d/s/u~/c~/d~/s~ g/u/c/d/s/u~/c~/d~/s~ > h h h WEIGHTED=18 @1. Please enter a valid process

-------------------
Possible other ways to define the process (NOT TESTED):


p p p > iota0 > h h h [QCD]

p p > iota, iota > h h h [QCD]

p p > b b~ b b~ b b~ [QCD]

-------------------------------------------
