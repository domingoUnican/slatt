"""
Project: slatt
Package: clattice for 0.2.4 on top of our own closure miner
Programmers: JLB

Purpose: implement a lattice by lists of antecedents among closed itsets

Offers:
.computing bms, mxs, list of predecesors, list of immediate predecessors
.scale in closminer serves to use ints instead of floats for
  support/confidence bounds, and allows us to index
  already-computed bases or cuts - params moved there:
  scale, univ, nrtr, nrits, nrocc, U (univ set), card (number of closures),
  maximum and minimum supports seen (absolute integers),
  supp_percent (float in [0,100] actually used for the mining)


ToDo:
.is it possible to save time somehow using immpreds to compute mxn/mns?
.rethink the scale, now 100000 means three decimal places for percentages
.be able to load only a part of the closures in the available file if desired support
is higher than in the file
.review the ticking rates
.should become a set of closures? 
"""

from closminer import closminer
from infinity import inft as infinity
from verbosity import verbosity
from collections import defaultdict

class clattice(closminer):
    """
    Lattice implemented as explicit list of closures (from closminer)
    with a dict of closed predecessors for each closure
    and a dict of immediate closed predecessors (added here)
    (all the predecessors - transitive closure)
    Verbosity v own or received at init
    Closures expected ordered in the list
    - option -l1 in Borgelts
    - by decreasing supports o/w
    """

    def __init__(self,supp,datasetfilename,v=None,xmlinput=False,externalminer=True):
        "float supp in [0,1] - read from clos file or create it from dataset"
        closminer.__init__(self,supp,datasetfilename,v,xmlinput=xmlinput,externalminer=externalminer)
        self.preds = defaultdict(list)
        self.impreds = defaultdict(set)
        for node in self.closeds:
            """
            set up preds and everything -
            closures come in either nonincreasing support or nondecreasing size
            hence all subsets of each closure come before it
            """
            node.mxs = 0
            node.bmns = infinity()
            for e in self.closeds:
                "list existing nodes potentially below, break at itself"
                self.v.tick()
                if e < node:
                    "a subset found"
                    self.preds[node].append(e)
                    "add e to this list"
                    self.impreds[node].add(e)
                    """
                    removes from the list of predecesors all those that are
                    also predecesors of e
                    """
                    self.impreds[node]=self.impreds[node]-set(self.preds[e])            
                    if e.supp < node.bmns: 
                        node.bmns = e.supp
                    if node.supp > e.mxs:
                        e.mxs = node.supp
                elif e == node:
                    "reached node"
                    break



if __name__ == "__main__":
    forget = False    
    filename = "./datasets/test"
    supp = 0.15
    ccc = 0.4
    c1=clattice(supp,filename)
    for nod in c1.closeds:
        print "------------------"
        print nod
        print "bmns ",nod.bmns
        print "mxs ",nod.mxs
            

