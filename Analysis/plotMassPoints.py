import ROOT as r

#---------------------------------------------------------------------
# to run in the batch mode (to prevent canvases from popping up)
r.gROOT.SetBatch()

# set plot style
r.gROOT.SetStyle("Plain")

# suppress the statistics box
r.gStyle.SetOptStat(0)

# more detailed statistics box
#r.gStyle.SetOptStat(1111111)

# suppress the histogram title
r.gStyle.SetOptTitle(0)

r.gStyle.SetPadTickX(1)  # to get the tick marks on the opposite side of the frame
r.gStyle.SetPadTickY(1)  # to get the tick marks on the opposite side of the frame

# tweak margins
#r.gStyle.SetPadTopMargin(0.05);
#r.gStyle.SetPadBottomMargin(0.13);
r.gStyle.SetPadLeftMargin(0.10);
r.gStyle.SetPadRightMargin(0.04);

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


# create canvas
c = r.TCanvas("c", "",1200,800)
c.cd()

# create mass plane
bkg = r.TH2F("bkg",";m_{X} [GeV];m_{Y} [GeV]",105,0,4200,105,0,4200)
bkg.Draw()


mX_min = 400
mX_max = 4000
mX_step = 200
mY_step = 200

e = r.TEllipse()
e.SetLineColor(r.kRed)

for mX in range(mX_min, mX_max + mX_step, mX_step):
    for mY in ([260] + range(300, mX-125, mY_step)):
        print ("(mX, mY) = (%i, %i)" % (mX, mY))
        e.DrawEllipse(mX,mY,10,15,0,360,0)

c.SaveAs("mass_points.pdf")
