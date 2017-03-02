"""
Programmers: JLB, DGP

Purpose: implementing lattice nodes and other itemset usages such as generators

Inherits from frozenset and Structure so that they can index dictionaries and
the attributes are set in a special attribute called _fields.
__init__ method takes any possible iterable.

Offers:
.supp, card
..mxs (max supp of a subset)
..mns (min supp of a superset)
..gmxs (max supp of a minimal generator that reaches some conf thr to the node)
.revise() to change the contents of the slanode while preserving the mxs/mns values - returns a new slanode
.package contributes ops outside class:
..str2node to make a slanode by parsing a line like the Borgelt output
.auxitset(string-or-another-iterable), auxiliary class to parse into set and support
..then coerce into slanode the auxitset and call setsupp(supp)

Notes:
.supp is an integer, absolute support; dataset size needed to compute relative support
.may want to use customized separator character to read the support from the apriori output ('/' or ';' or...)
.copy method is not necessary, because there exists a method deepcopy from the module
 copy.

ToDo:
.eliminate str2node
.try Python 3.0 to inform the support upon __init__() and simplify (could then remove auxitset, set2node, str2node)
.add initialization for output from other closure miners such as Zaki's RULES
.some day the contents should be able to accommodate trees and sequences and...
"""

from decorator import Structure
import copy

def str2node(string=""):
    sepsupp = string.split('/')
    cont = sepsupp[0].strip('( ').split()
    supp = 0
    if len(sepsupp)>1:
        "comes with support info"
        supp = int(sepsupp[1].strip(')%\n\r'))
    return slanode(cont, supp = supp)


class slanode(Structure, frozenset):

    _fields = [('contents', []), # The actual iterable
               ('supp', 0), # support, initializate to 0
               ('card', len, ['contents']), # card =  len(contents)
               ('mxs', -1), ('mns', -1), ('gmxs',-1)]


    def __str__(self,trad={}):
        """
        prettyprint of itemset: support omitted if zero
        optional element translator trad
        """
        s = ""
        for el in sorted(self):
            if  el in trad.keys():
                el = trad[el]
            if s=="":
                s = str(el)
            else:
                s += "," + str(el)
        s = "{ " + s + " }"
        if self.supp > 0:
            s = s + " (" + str(self.supp) + ")"
        return s

    def __repr__(self, trad={}):
        return self.__str__(trad=trad)

    def revise(self,c):
        return copy.deepcopy(slanode(contents=c,
                                     supp=self.supp,
                                     mxs=self.mxs,
                                     mns=self.mns,
                                     gmxs=self.gmxs))
    def copy(self):
        return copy.deepcopy(self)

if __name__=="__main__":
    "some little testing needed here"
    pass

##    print "slatt module itset called as main and running as test..."
