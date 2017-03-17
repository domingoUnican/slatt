"""
Subproject: Slatt
Package: rerulattice
Programmers: JLB, CT
Revised by: CT

Inherits from clattice, which brings dictionary of predecessors and immediate predecessors

Offers:
.mineClosureRR to compute a closure-aware set of representative rules


Notes/ToDo:
.want to be able to use it on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
  due to an inappropriate closures file, or due to the fact that indeed there
  are no closed sets in the dataset in between both supports (careful with
  their different scales)
.revise and enlarge the local testing
.revise ticking rates
"""

from clattice import clattice
from corr import corr
from hypergraph import hypergraph


class clrerulattice(clattice):

    def __init__(self,supp,datasetfile="",v=None,xmlinput=False,externalminer=True):
        "call clattice to get the closures"
        clattice.__init__(self,supp,datasetfile,v,xmlinput=xmlinput,externalminer=externalminer)
                
    def _faces(self,itst,listpred):
        "listpred assumed immediate preds of itst - make hypergraph of differences"
        itst = set(itst)
        return hypergraph(itst,[ itst - e for e in listpred ])
    
    def mineClosureRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        """
        if confthr == 1:
            self.v.inimessg("This algorithm works only for confidence thresholds strictly smaller than 1")
            return corr()
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        self.v.zero(100)
        self.v.inimessg("Computing representative rules at confidence "+str(confthr)+" using our closure-aware approach...")
        ants = corr()
        self.v.messg("computing antecedents...")       
        for nod in self.closeds:
            self.v.tick()
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
        self.v.zero(500)
        self.v.messg("...done.\n")
        return ants
    

if __name__ == "__main__":
    import sys
    import time
    from slarule import printrules
    out_file = "output.txt"
    if len(sys.argv)>1:
        out_file=sys.argv[1]
    output=open(out_file,"w")
    current_dir="./datasets/"
    tests={"test":[0.20]}
##    tests={"retail":[0.001,0.0005],"adult":[0.01,0.005],"accidents":[0.5,0.4]}
    for filename in tests.keys():
        output.write(filename+"\n")
        for supp in tests[filename]:
            output.write(str(supp)+"\n")
            time1=time.time()
            rl = clrerulattice(supp,current_dir+filename,v=False)
            time2=time.time()-time1
            output.write("rerulattice: %3.3f"%time2+"\n")
            for ccc in [0.9,0.8,0.7]:
                output.write(str(ccc)+"\n")
                time1=time.time()
                ClosureRR =rl.mineClosureRR(supp,ccc)
                time2=time.time()-time1
                outrulesfile = file(current_dir+filename+"ClosureRR"+("_c%2.3f"%ccc)+("_s%2.4f"%supp)+".txt","w")
                output.write("ClosureRR time: %.3f"%time2+"\n")
                output.write("%d repr rules found with ClosureRR at conf %.2f"%(printrules(ClosureRR,rl.nrtr,outrulesfile,doprint=True),ccc)+"\n")

    output.close()



