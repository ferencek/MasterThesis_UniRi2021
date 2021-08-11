import os

mX_min = 400
mX_max = 4000
mX_step = 200
mY_step = 200


# loop over mass points
for mX in range(mX_min, mX_max + mX_step, mX_step):
    for mY in sorted(list(set([260,mX-140])) + range(300, mX-125, mY_step)):
        print ('---------------------------------------')
        print ('(mX, mY) = (%i, %i)' % (mX, mY))
        print ('---------------------------------------')

        cards_path = '/STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards'
        template_folder = 'TRSM_XToHY_6b_template'
        template_path = os.path.join(cards_path, template_folder)

        sample_name = 'TRSM_XToHY_6b_M3_%i_M2_%i' % (mX, mY)
        sample_path = os.path.join(cards_path, sample_name)

        # prepare sample data cards in case they do not already exist
        if not os.path.exists(sample_path):
            # create sample data cards folder
            cmd = 'mkdir -p %s' % sample_path
            os.system(cmd)

            # copy template data cards
            for f in os.listdir(template_path):
                #print f
                cmd = 'cp -v %s %s' % (os.path.join(template_path, f), os.path.join(sample_path, sample_name + '_' + f))
                os.system(cmd)

            # set mass values
            for c in ['customizecards.dat', 'proc_card.dat']:
                cmd = "sed -i 's/M3MASS/%i/g' %s" % (mX, os.path.join(sample_path, sample_name + '_' + c))
                os.system(cmd)
                cmd = "sed -i 's/M2MASS/%i/g' %s" % (mY, os.path.join(sample_path, sample_name + '_' + c))
                os.system(cmd)

        # run MadGraph
        mg_path = '/home/ferencek/TRSM_production/genprod_mg261_slc7/bin/MadGraph5_aMCatNLO/'
        os.chdir(mg_path)

        cmd = 'time ./gridpack_generation.sh %s ../../../../../../STORE/ferencek/TRSM_XToHY_6b/2017/13TeV/datacards/%s local' % (sample_name, sample_name)
        os.system(cmd)

print ('---------------------------------------')
