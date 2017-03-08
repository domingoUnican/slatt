"""
Project: slatt
Package: clattice for 0.2.4 on top of our own closure miner
Programmers: JLB

Purpose: implement a lattice by lists of antecedents among closed itsets

Offers:
.hist_cuts: all cuts computed so far, so that they are not recomputed
.dump_hist_cuts
.computing closure op
.to string method
.scale in closminer serves to use ints instead of floats for
  support/confidence/boost bounds, and allows us to index
  already-computed bases or cuts - params moved there:
  scale, univ, nrtr, nrits, nrocc, U (univ set), card (number of closures),
  maximum and minimum supports seen (absolute integers),
  supp_percent (float in [0,100] actually used for the mining)

Auxiliary local methods:

ToDo:
.check whether the skipping of closures in computing cuts works at all
.refactor the handling of omitted nodes in setcuts:
  the conf boost (upper width) bound and the variants of Kr Property 9
  should be treated in the same manner
.raise a more appropriate exception if platform not handled
.recover the handling of mns/mxs and check their use in extreme cases
.if mxs zero, option is conservative estimate minsupp-1
.is it possible to save time somehow using immpreds to compute mxn/mns?
.rethink the scale, now 100000 means three decimal places for percentages
.be able to load only a part of the closures in the available file if desired support is higher than in the file
.review the ticking rates
.should become a set of closures? 
"""

from closminer import closminer
from infinity import inft as infinity
from verbosity import verbosity
from corr import corr
from collections import defaultdict

class clattice(closminer):
    """
    Lattice implemented as explicit list of closures (from closminer)
    with a dict of closed predecessors for each closure (added here)
    (all the predecessors - transitive closure)
    Verbosity v own or received at init
    Closures expected ordered in the list
    - option -l1 in Borgelts
    - by decreasing supports o/w
    """

    def __init__(self,supp,datasetfilename,v=None,xmlinput=False,externalminer=True):
        "float supp in [0,1] - read from clos file or create it from dataset"
        closminer.__init__(self,supp,datasetfilename,v,xmlinput=xmlinput,externalminer=externalminer)
        self.hist_cuts = {}
        self.preds = defaultdict(list)
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
                    if e.supp < node.bmns: 
                        node.bmns = e.supp
                    if node.supp > e.mxs:
                        e.mxs = node.supp
                elif e == node:
                    "reached node"
                    break
        


    def __str__(self):
        s = ""
        for e in sorted(self.closeds):
            s += str(e) + "\n"
        return s

    def close(self,st):
        "closure of set st according to current closures list - slow for now"
        over = [ e for e in self.closeds if st <= e ]
        if len(over)>0:
            e = over[0]
        else:
            "CAREFUL: what if st is not included in self.U?"
            e = set2node(self.U)
        for e1 in over:
            if e1 < e:
                e = e1
        return e

    def isclosed(self,st):
        "test closedness of set st according to current closures list"
        return st in self.closeds

    def dump_hist_cuts(self):
        "prints out all the cuts so far - useful mostly for testing"
        for e in self.hist_cuts.keys():
            print "\nMinimal closed antecedents at conf thr", e
            pos = self.hist_cuts[e][0]
            for ee in pos.keys():
                print ee, ":",
                for eee in pos[ee]: print eee,
                print
            print "Maximal closed nonantecedents at conf thr", e
            neg = self.hist_cuts[e][1]
            for ee in neg.keys():
                print ee, ":",
                for eee in neg[ee]: print eee,
                print

    def setcuts(self,scsthr,sccthr,forget=False,skip=None,skippar=0):
        """
        supp/conf already scaled thrs in [0,self.scale]
        computes all cuts for that supp/conf thresholds, if not computed yet;
        keeps them in hist_cuts to avoid duplicate computation (unless forget);
        the cut for each node consists of two corrs, pos and neg border:
        hist_cuts : supp/conf thr -> (pos,neg)
        pos : node -> min ants,  neg : node -> max nonants
        wish to be able to use it for a support different from self.minsupp
        (unclear whether it works now in that case)
        Things that probably do not work now:
        Bstar may require a support improvement wrt larger closures
        signaled by skip not None AND skippar (improv) not zero
        Kr/BC heuristics may require a conf-based check on nodes,
        signaled by skip not None and skippar (conf) not zero
        NOTE: cpos does not appear to be used anywhere. Consider removing it
        """
        if (scsthr,sccthr) in self.hist_cuts.keys():
            "use cached version if it is there"
            return self.hist_cuts[scsthr,sccthr]
        if skip is not None and skippar != 0:
            "risk of not all closures traversed, don't cache the result"
            forget = True
        else:
            "skip is None or skippar is zero, then no skipping"
            skip = never
        cpos = corr()
        cneg = corr()
        self.v.zero(500)
        self.v.messg("...computing (non-)antecedents...")
        for nod in self.closeds:
            "review carefully and document this loop"
            if skip(nod,skippar,self.scale):
                "we will not compute rules from this closure"
                continue
            self.v.tick()
            if self.scale*nod.supp >= self.nrtr*scsthr:
                pos, neg = self._cut(nod,sccthr) 
                cpos[nod] = pos
                cneg[nod] = neg
        if not forget: self.hist_cuts[scsthr,sccthr] = cpos, cneg
        self.v.messg("...done;")
        return cpos, cneg

    def _cut(self,node,thr):
        """
        splits preds of node at cut given by
        min thr-antecedents and max non-thr-antecedents
        think about alternative algorithmics
        thr expected scaled according to self.scale
        NOTE: yesants does not appear to be used anywhere
        """
        yesants = []
        notants = []
        for m in self.preds[node]:
            "there must be a better way of doing all this!"
            if self.scale*node.supp >= thr*m.supp:
                yesants.append(m)
            else:
                notants.append(m)
        minants = []
        for m in yesants:
            "keep only minimal antecedents - candidate to separate program?"
            for mm in yesants:
                if mm < m:
                    break
            else:
                minants.append(m)
        maxnonants = []
        for m in notants:
            "keep only maximal nonantecedents"
            for mm in notants:
                if m < mm:
                    break
            else:
                maxnonants.append(m)
        return (minants,maxnonants)

def never(n,s,t):
    return False

if __name__ == "__main__":
    forget = False    
    filename = "prueba"
    supp = 0.15
    ccc = 0.4
    c1=clattice(supp,filename)
    for nod in c1.closeds:
        print "------------------"
        print nod
        print "bmns ",nod.bmns
            

