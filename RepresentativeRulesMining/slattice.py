"""
Project: Slatt
Package: slattice
Programmers: JLB
Revised by: CT

Purpose: basic implication mining: minimal generators 

Inherits from clattice; use clattice when only closures are needed,
and slattice when the minimal generators of each
closure are also needed, as in rerulattice.

Fields: 
.mingens: a corr maintaining the nontrivial minimal generators for each closure
..antecedents of the iteration-free basis of Wild, Pfaltz-Taylor, Pasquier-Bastide, Zaki...


Methods available:
.findmingens: to compute the minimal generators of all closures via
  transversals of immediate predecessors obtained as negative cuts
  (note that no tightening is necessary)
.setmns to initialize the mns's of the free sets after mingens created


Auxiliary local methods:
._faces to compute faces (differences) to apply the transversal

ToDo:
.revise and enlarge the local testing
.revise ticking rates
.some day it can be used on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
..due to an inappropriate closures file, or due to the fact that indeed there
..are no closed sets in the dataset in between both supports (careful with
..their different scales), all this is to be clarified
"""


from clattice import clattice
from slanode import set2node
from hypergraph import hypergraph
from corr import corr
from collections import defaultdict


class slattice(clattice):

    def __init__(self,supp,datasetfile="",v=None,xmlinput=False,externalminer=True):
        "get the closures, find minimal generators, set their mns"
        clattice.__init__(self,supp,datasetfile,v,xmlinput=xmlinput,externalminer=externalminer)      
        self.mingens = corr()
        self.findmingens()
        self.setmns()


    def _faces(self,itst,listpred):
        "listpred assumed immediate preds of itst - make hypergraph of differences"
        itst = set(itst)
        return hypergraph(itst,[ itst - e for e in listpred ])

    def findmingens(self,suppthr=-1):
        """
        compute the minimal generators for each closure;
        nontrivial pairs conform Wild's iteration-free basis;
        algorithm is the same as mineRR for confidence 1;
        optional suppthr in [0,1] to impose an extra level of iceberg
        but this optional value is currently ignored
        because maybe minsupp actually much higher than mined at
        use the support found in closures file
        when other supports handled, remember to memorize computed ones
        """
        if suppthr < 0:
            "ToDo: find out how to use integer division"
            sthr = int(self.scale*self.minsupp/self.nrtr)
        else:
            "ToDo: remove this assignment and do it the right way"
            sthr = int(self.scale*self.minsupp/self.nrtr)
        if len(self.mingens)>0:
            return self.mingens
        self.v.inimessg("Computing cuts for minimal generators...")
        """If cthr=self.scale in nonants we have inmediate
        closed predecessors of nod
        """
        self.v.zero(250)
        self.v.messg("computing transversal antecedents...")
        for nod in self.closeds:
            "careful, assuming nodes ordered by size here - find all free sets"
            self.v.tick()
            self.mingens[nod] = []
            for m in self._faces(nod,self.impreds[nod]).transv().hyedges: 
                if m in self.closeds:
                    i=self.closeds.index(m)
                    mm = self.closeds[i]
                else:
                    mm = set2node(m)
                    mm.setsupp(nod.supp)
                    mm.clos = nod
                
                self.mingens[nod].append(mm)
            if len(self.mingens[nod]) == 1 and nod.card == self.mingens[nod][0].card:
                "nod is a free set and its own unique mingen"
                nod.mns = nod.bmns
            else:
                "nod has some proper subsets as mingens"
                nod.mns = nod.supp 
        self.v.messg("...done;")
        return self.mingens



    def setmns(self):
        """
        set slanode.mns for free sets in mingens lists
        findmingens() assumed to have been invoked already
        maybe it is possible to accelerate this computation
        """
        self.v.zero(250)
        self.v.inimessg("Initializing min supp below free sets...")
        for c1 in self.closeds:
            for m1 in self.mingens[c1]:
                self.v.tick()
                if m1.mns <= 0:
                    m1.mns = self.nrtr
                    for c2 in self.preds[c1]:
                        if c2.supp < m1.mns:
                            for m2 in self.mingens[c2]:
                                if m2 < m1:
                                    m1.mns = c2.supp
        self.v.messg("...done.\n")

if __name__ == "__main__":
    forget = False    
    filename = "./datasets/test"
    supp = 0.15
    ccc = 0.4
    s1=slattice(supp,filename)
    for nod in s1.closeds:
        print "------------------"
        print nod.bmns
        for m in s1.mingens[nod]:
            print m
            print "mns ",m.mns

            
    
