import ROOT as r

#---------------------------------------------------------------------
# to run in the batch mode (to prevent canvases from popping up)
r.gROOT.SetBatch()

# set plot style
r.gROOT.SetStyle("Plain")
r.gStyle.SetPalette(57)

# suppress the statistics box
r.gStyle.SetOptStat(0)

# more detailed statistics box
#r.gStyle.SetOptStat("nemruoi")
#r.gStyle.SetOptStat(1111111)

# suppress the histogram title
r.gStyle.SetOptTitle(0)

r.gStyle.SetPadTickX(1)  # to get the tick marks on the opposite side of the frame
r.gStyle.SetPadTickY(1)  # to get the tick marks on the opposite side of the frame

# tweak margins
#r.gStyle.SetPadTopMargin(0.05);
#r.gStyle.SetPadBottomMargin(0.13);
r.gStyle.SetPadLeftMargin(0.10);
r.gStyle.SetPadRightMargin(0.15);

# tweak axis title offsets
r.gStyle.SetTitleOffset(1.2, "Y");

# set nicer fonts
r.gStyle.SetTitleFont(42, "")
r.gStyle.SetTitleFont(42, "XYZ")
r.gStyle.SetLabelFont(42, "XYZ")
r.gStyle.SetTextFont(42)
r.gStyle.SetStatFont(42)
r.gROOT.ForceStyle()
#---------------------------------------------------------------------

gr_gen = r.TGraph2D()
gr_genjet = r.TGraph2D()
gr_gen.SetTitle(";m_{X} [GeV];m_{Y} [GeV];Fraction of boosted Higgs boson candidates")
gr_genjet.SetTitle(";m_{X} [GeV];m_{Y} [GeV];Fraction of boosted Higgs boson candidates")

mX_min = 400
mX_max = 4000
mX_step = 200
mY_step = 200


n = 0
for mX in range(mX_min, mX_max + mX_step, mX_step):
    for mY in ([260] + range(300, mX-125, mY_step)):
        #f = r.TFile("/users/lcalic/nobackup/cmsdas_2020_gen/condor_analysis_jobs_GenJetNoNu_20210610132757/HISTOGRAMS_TRSM_XToHY_6b_M3_%i_M2_%i.root" % (mX, mY))
        f = r.TFile("/users/ferencek/TRSM_analysis/condor_analysis_jobs_GenJetNoNu_20210610132757/HISTOGRAMS_TRSM_XToHY_6b_M3_%i_M2_%i.root" % (mX, mY))
        f.cd()
        h1_b = f.Get("h_multiplicityN_higgs_candidates")
        h2_b = f.Get('h_DeltaR_bb_vs_higgspt')
        h2_n = f.Get('h_higgs_pt_all')
        frac_gen = h2_b.Integral(0,h2_b.GetNbinsX()+1,0,h2_b.GetYaxis().FindBin(0.8)-1)/ h2_n.Integral(0,h2_n.GetNbinsX()+1)
        nHiggsCands=0
        for i in range(1,5):
            nHiggsCands += h1_b.GetBinContent(i+1)*i
        frac_genjet=float(nHiggsCands)/h2_n.Integral(0,h2_n.GetNbinsX()+1)
        print ("(mX, mY) = (%i, %i)" % (mX, mY))
        print (frac_gen)
        print (frac_genjet)
        gr_gen.SetPoint(n,mX,mY,frac_gen)
        gr_genjet.SetPoint(n,mX,mY,frac_genjet)
        n += 1

## create canvas
c = r.TCanvas("c", "",1200,800)
c.cd()

gr_gen.SetMinimum(0) # has to be called before SetLimits for SetLimits to have an effect (?!)
gr_gen.SetMaximum(1) # has to be called before SetLimits for SetLimits to have an effect (?!)
# however, SetLimits does not have the desired effect because with the "surface" drawing options the graph always stretches/squeezes to fill the full range
#gr_gen.GetXaxis().SetLimits(0,4000)
#gr_gen.GetYaxis().SetLimits(0,4000-125)
#gr_gen.GetXaxis().SetLimits(3*125,4000)
#gr_gen.GetYaxis().SetLimits(2*125,4000-125)
gr_gen.Draw("cont4z")
c.SaveAs("BoostedHiggsFraction_gen.pdf")

gr_genjet.SetMinimum(0) # has to be placed before calling SetLimits (?!)
gr_genjet.SetMaximum(1) # has to be placed before calling SetLimits (?!)
# however, SetLimits does not have the desired effect because with the "surface" drawing options the graph always stretches/squeezes to fill the full range
#gr_genjet.GetXaxis().SetLimits(0,4000)
#gr_genjet.GetYaxis().SetLimits(0,4000-125)
#gr_genjet.GetXaxis().SetLimits(3*125,4000)
#gr_genjet.GetYaxis().SetLimits(2*125,4000-125)
gr_genjet.Draw("cont4z")
c.SaveAs("BoostedHiggsFraction_genjet.pdf")
