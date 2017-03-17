"""
Subproject: Slatt
Package: rerulattice
Programmers: JLB, CT
Revised by: CT

Inherits from slattice, which brings cuts, mingens, and GDgens

Offers:
.mineKrRR to compute a subset of representative rules
  by Kryszkiewicz heuristic,
.mineRR to compute the representative rules for a given confidence
  by our complete variant of Kryszkiewicz,
.mineClosureRR to compute a closure-aware set of representative rules



Notes/ToDo:
.hist fields for the three algorithms
.want to be able to use it on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
  due to an inappropriate closures file, or due to the fact that indeed there
  are no closed sets in the dataset in between both supports (careful with
  their different scales)
.revise and enlarge the local testing
.revise ticking rates
.find a way to print GDGens
"""
import time
from slatticenew import slattice
from slarule import slarule
from corr import corr
import sys
from hypergraph import hypergraph

class rerulattice(slattice):

    def __init__(self,supp,datasetfile="",v=None,xmlinput=False,externalminer=True):
        "call slattice to get the closures and minimal generators"
        slattice.__init__(self,supp,datasetfile,v,xmlinput=xmlinput,externalminer=externalminer)

    def _faces(self,itst,listpred):
        "listpred assumed immediate preds of itst - make hypergraph of differences"
        itst = set(itst)
        return hypergraph(itst,[ itst - e for e in listpred ])

    def mineKrRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence using Kryszkiewicz IDA 2001 heuristic;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        """
##        if confthr == 1:
##            return self.findmingens(suppthr)
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
##        self.v.zero(100)
##        self.v.inimessg("Computing representative rules at confidence "+str(confthr)+" using Kryszkiewicz's incomplete heuristic...")
        ants = corr()
##        self.v.messg("computing antecedents...")
        for nod in self.closeds:
            self.v.tick()
            c1=self.scale*nod.mxs
            c2=self.scale*nod.supp
            if  c2 >= cthr*nod.mns and c1 < cthr*nod.mns:
                "this is the test of Prop 9 in Kryszkiewicz's paper"
                ants[nod] = []
                "computing valid antecedents ..."

                for node in self.preds[nod]+[nod]:
                    for m in self.mingens[node]:
                        if m<nod and c1<cthr*m.supp and cthr*m.supp <=c2 and c2<cthr*m.mns:
                            ants[nod].append(m)
##        self.v.zero(500)
##        self.v.messg("...done.\n")
        return ants

    def mineRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        """
        if confthr == 1:
            return self.findmingens(suppthr)
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        self.v.zero(100)
        self.v.inimessg("Computing representative rules at confidence "+str(confthr)+" using our heuristic...")
        ants = corr()
        self.v.messg("computing antecedents...")
        for nod in self.closeds:
            self.v.tick()
            mxgs=0
            for m in self.mingens[nod]:
                if m<nod:
                    mxgs=nod.supp
                    break
            for node in self.preds[nod]:
                if mxgs<node.supp and cthr*node.supp<=self.scale*nod.supp:
                    mxgs=node.supp
            c1=self.scale*nod.mxs
            c2=self.scale*nod.supp
            if cthr*mxgs>c1:
                "this is the test of Prop 5 in our EGC paper"
                ants[nod] = []
                "computing valid antecedents (Prop 6 in our EGC paper)"
                for node in self.preds[nod]+[nod]:
                    for m in self.mingens[node]:
                        if m<nod and c1<cthr*m.supp and cthr*m.supp <=c2 and c2<cthr*m.mns:
                            ants[nod].append(m)
        self.v.zero(500)
        self.v.messg("...done.\n")
        return ants

    def mineClosureRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        """
        if confthr == 1:
            return self.findGDgens(suppthr)
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
##        self.v.zero(100)
##        self.v.inimessg("Computing representative rules at confidence "+str(confthr)+" using our closure-aware approach...")
        ants = corr()
##        self.v.messg("computing antecedents...")
        for nod in self.closeds:
##            self.v.tick()
            mxgs=0
            foundyesants=False
            for node in self.preds[nod]:
                if mxgs<node.supp and cthr*node.supp<=self.scale*nod.supp:
                    mxgs=node.supp
                    foundyesants=True
            if not foundyesants:
                mingens = self._faces(nod,list(self.impreds[nod])).transv().hyedges
                if len(mingens)>1:
                    mxgs=nod.supp
                elif len(mingens[0])<nod.card:
                    mxgs=nod.supp
            c1=self.scale*nod.mxs
            c2=self.scale*nod.supp
            if cthr*mxgs>c1 and mxgs>nod.supp:
                "this is the test of Prop 3 in our IEEE Trans paper"
                ants[nod] = []
                "computing valid antecedents (Prop 4 in our IEEE Trans paper)"
                for node in self.preds[nod]:
                    if c1<cthr*node.supp and cthr*node.supp<=c2 and c2<cthr*node.bmns:
                        ants[nod].append(node)
##        self.v.zero(500)
##        self.v.messg("...done.\n")
        return ants


if __name__ == "__main__":
    from slarule import printrules
    print("Starting..")
    out_file = "output.txt"
    if len(sys.argv)>1:
        out_file=sys.argv[1]
    output=open(out_file,"w")
    current_dir="./datasets/"
##    tests={"prueba":[0.20]}
    tests={"retail":[0.001,0.0005],"adult":[0.01,0.005],"accidents":[0.5,0.4]}
    for filename in tests.keys():
        output.write(filename+"\n")
        for supp in tests[filename]:
            output.write(str(supp)+"\n")
            time00=time.time()
            rl = rerulattice(supp,current_dir+filename)
            time0=time.time()
            output.write("rerulattice: %3.3f"%(time0-time00)+"\n")
            for ccc in [0.9,0.8,0.7]:
                output.write(str(ccc)+"\n")
                time1=time.time()
##                KrRRants = rl.mineKrRR(supp,ccc)
##                time2=time.time()
##                RRants = rl.mineRR(supp,ccc)
##                time3=time.time()
                ClosureRR =rl.mineClosureRR(supp,ccc)
                time4=time.time()
                times=[time4-time1]
                algorithms=["ClosureRR"]
                miners=[ClosureRR]
                for i,alg in enumerate(algorithms):
                    outrulesfile = file(current_dir+filename+alg+("_c%2.3f"%ccc)+("_s%2.4f"%supp)+".txt","w")
                    output.write("%s time: %.3f"%(alg,times[i])+"\n")
                    output.write("%d repr rules found with %s at conf %.2f"%(printrules(miners[i],rl.nrtr,outrulesfile,doprint=True),alg,ccc)+"\n")

    output.close()
