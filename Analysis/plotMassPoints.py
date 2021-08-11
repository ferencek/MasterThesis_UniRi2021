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


gr_BP = r.TGraph()

n = 0
for (mX, mY) in [(1600, 500), (2000, 300), (2000, 800),  (2500, 300)]:
        gr_BP.SetPoint(n,mX,mY)
        n += 1

gr_BP.SetMarkerStyle(4)
gr_BP.SetMarkerColor(r.kBlue)

gr_BP.Draw("SAME P")


mX_min = 400
mX_max = 4000
mX_step = 200
mY_step = 200

gr = r.TGraph()

n = 0
for mX in range(mX_min, mX_max + mX_step, mX_step):
    for mY in sorted(list(set([260,mX-140])) + range(300, mX-125, mY_step)):
        print ("(mX, mY) = (%i, %i)" % (mX, mY))
        gr.SetPoint(n,mX,mY)
        n += 1

gr.SetMarkerStyle(20)
gr.SetMarkerColor(r.kRed)
gr.SetMarkerSize(0.6)

gr.Draw("SAME P")

pline = r.TPolyLine()
pline.SetPoint(0,0,0)
pline.SetPoint(1,4200,0)
pline.SetPoint(2,4200,2*125)
pline.SetPoint(3,3*125,2*125)
pline.SetPoint(4,4200,4200-125)
pline.SetPoint(5,4200,4200)
pline.SetPoint(6,0,4200)
pline.SetPoint(7,0,0)
pline.SetFillColor(r.kGray)
pline.SetFillStyle(3344)
pline.Draw("f")

r.gPad.RedrawAxis()

c.SaveAs("mass_points.pdf")
