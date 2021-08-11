import ROOT as r
import copy

#--------------------------------------------------------------------------------------------------------------------------------
def function (graph,graphs_BP, name):

    #############################
    # The "surface" drawing options ("surf", "col", "cont") impose their own internal coordinate system
    # which complicates overlay of additional objects on the plot and requires extra steps. The code
    # below is based on discussion and instructions provided in
    # https://root-forum.cern.ch/t/drawing-a-single-contour-over-a-tgraph2d-using-cont4/12061
    #############################

    c = r.TCanvas("c", "",1200,800)
    c.cd()

    gr_dummy = r.TGraph()
    gr_dummy.SetPoint(0,1000,3000)

    pad1 = r.TPad("pad1","",0,0,1,1)
    pad2 = r.TPad("pad2","",0.1,0.1,0.85,0.9)
    pad2.SetFillStyle(4000) # will be transparent

    pad1.Draw()
    pad1.cd()

    graph.SetMinimum(0) # has to be placed before calling TAxis methods (?!)
    graph.SetMaximum(1) # has to be placed before calling TAxis methods (?!)
   
    graph.GetXaxis().SetTickLength(0)
    graph.GetYaxis().SetTickLength(0)

    graph.Draw("cont4z")

    xmin = graph.GetXaxis().GetXmin()
    xmax = graph.GetXaxis().GetXmax()
    ymin = graph.GetYaxis().GetXmin()
    ymax = graph.GetYaxis().GetXmax()

    #print xmin, xmax, ymin, ymax

    pad2.Range(xmin,ymin,xmax,ymax)
    pad2.Draw()
    pad2.cd()

    gr_dummy.Draw("SAME *") # necessary to get the tick marks

    pline = r.TPolyLine()
    pline.SetPoint(0,xmin,xmin-125.)
    pline.SetPoint(1,xmax,xmax-125.)
    pline.SetPoint(2,xmin,xmax-125.)
    pline.SetPoint(3,xmin,xmin-125.)
    pline.SetFillColor(10)
    pline.SetFillStyle(1001)
    pline.SetLineColor(2)
    pline.SetLineWidth(2)
    pline.Draw("f")
    pline_hatched = copy.deepcopy(pline)
    pline_hatched.SetFillColor(r.kGray)
    pline_hatched.SetFillStyle(3344)
    pline_hatched.Draw("f")

    pad2.RedrawAxis()

    c.SaveAs(name)


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

boosted_higgs_graphsGen = [r.TGraph2D(), r.TGraph2D(), r.TGraph2D(), r.TGraph2D()]
boosted_higgs_graphsGenJet = [r.TGraph2D(), r.TGraph2D(), r.TGraph2D(), r.TGraph2D()]
for i in range(4):
    boosted_higgs_graphsGen[i].SetTitle(";m_{X} [GeV];m_{Y} [GeV];Event selection eff. (%i H cand.)"%i)
    boosted_higgs_graphsGenJet[i].SetTitle(";m_{X} [GeV];m_{Y} [GeV];Event selection eff. (%i H cand.)"%i)



mX_min = 400
mX_max = 4000
mX_step = 200
mY_step = 200


n = 0
for mX in range(mX_min, mX_max + mX_step, mX_step):
    for mY in ([260] + range(300, mX-125, mY_step)):
        f = r.TFile("/users/lcalic/nobackup/cmsdas_2020_gen/condor_analysis_jobs_20210802145153/HISTOGRAMS_TRSM_XToHY_6b_M3_%i_M2_%i.root" % (mX, mY))
        f.cd()
        h1_b = f.Get("h_multiplicityN_higgs_candidates")
        h2_b = f.Get('h_DeltaR_bb_vs_higgspt')
        h2_n = f.Get('h_higgs_pt_all')
        h1_n = f.Get('h_multiplicityN_higgs_candidates_boosted')
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
        for count in range(4):
            frac_gen = h1_n.GetBinContent(count+1) / h1_n.Integral()
            frac_genjet = h1_b.GetBinContent(count+1) / h1_b.Integral()
            boosted_higgs_graphsGen[count].SetPoint(n, mX, mY, frac_gen)
            boosted_higgs_graphsGenJet[count].SetPoint(n, mX, mY, frac_genjet)
        n += 1
        
        
#BP lists         
points = [(1600, 500),(2000, 300),(2000, 800),(2500, 300)]
suffix = ["BPb","BPd", "BPe","BPf"]
gr_gen_BP = [r.TGraph2D() for point in points]
gr_genjet_BP = [r.TGraph2D() for point in points]
boosted_higgs_graphsGen_BP = [[r.TGraph2D() for point in points] for i in range (4)]
boosted_higgs_graphsGenJet_BP = [[r.TGraph2D() for point in points] for i in range (4)]


for p in range(len(points)):
 
    gr_gen_BP[p].SetTitle(";m_{X} [GeV];m_{Y} [GeV];Fraction of boosted Higgs boson candidates")
    gr_genjet_BP[p].SetTitle(";m_{X} [GeV];m_{Y} [GeV];Fraction of boosted Higgs boson candidates")
    for i in range(4):
        boosted_higgs_graphsGen_BP[i][p].SetTitle(";m_{X} [GeV];m_{Y} [GeV];Event selection eff. (%i H cand.)"%i)
        boosted_higgs_graphsGenJet_BP[i][p].SetTitle(";m_{X} [GeV];m_{Y} [GeV];Event selection eff. (%i H cand.)"%i)
        

for p, (mX,mY) in enumerate(points):
        n=0
        f = r.TFile("/users/lcalic/nobackup/cmsdas_2020_gen/HISTOGRAMS_TRSM_XToHY_6b_M3_%i_M2_%i_%s.root" % (mX, mY, suffix[p]))
        f.cd()
        h1_b = f.Get("h_multiplicityN_higgs_candidates")
        h2_b = f.Get('h_DeltaR_bb_vs_higgspt')
        h2_n = f.Get('h_higgs_pt_all')
        h1_n = f.Get('h_multiplicityN_higgs_candidates_boosted')
        frac_gen = h2_b.Integral(0,h2_b.GetNbinsX()+1,0,h2_b.GetYaxis().FindBin(0.8)-1)/ h2_n.Integral(0,h2_n.GetNbinsX()+1)
        nHiggsCands=0
        for i in range(1,5):
            nHiggsCands += h1_b.GetBinContent(i+1)*i
        frac_genjet=float(nHiggsCands)/h2_n.Integral(0,h2_n.GetNbinsX()+1)
        print ("(mX, mY) = (%i, %i)" % (mX, mY))
        print (frac_gen)
        print (frac_genjet)
        gr_gen_BP[p].SetPoint(n,mX,mY,frac_gen)
        gr_genjet_BP[p].SetPoint(n,mX,mY,frac_genjet)
        for count in range(4):
            frac_gen = h1_n.GetBinContent(count+1) / h1_n.Integral()
            frac_genjet = h1_b.GetBinContent(count+1) / h1_b.Integral()
            boosted_higgs_graphsGen_BP[count][p].SetPoint(n, mX, mY, frac_gen)
            boosted_higgs_graphsGenJet_BP[count][p].SetPoint(n, mX, mY, frac_genjet)
        



function (gr_gen,gr_gen_BP,  "BoostedHiggsFraction_gen.pdf")
function (gr_genjet, gr_genjet_BP, "BoostedHiggsFraction_genjet.pdf")
for i in range (4):  
   function(boosted_higgs_graphsGen[i], boosted_higgs_graphsGen_BP[i],"Event_Selection_eff_%i_gen.pdf"%i)
   function(boosted_higgs_graphsGenJet[i],boosted_higgs_graphsGenJet_BP[i],"Event_Selection_eff_%i_genJet.pdf"%i) 
    





