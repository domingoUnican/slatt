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
.add initialization for output from other closure miners such as Zaki's RULES
.some day the contents should be able to accommodate trees and sequences and...
"""

import copy


class slanode(frozenset):

    def __new__(cls, contents=[], supp=0, mxs=-1, mns=-1, gmxs=-1):
        cont = contents
        if isinstance(contents, str):
            sepsupp = contents.split('/')
            cont = sepsupp[0].strip('( ').split()
            if len(sepsupp) > 1:
                "comes with support info"
                supp = int(sepsupp[1].strip(')%\n\r'))
        s = frozenset.__new__(cls, cont)
        s.supp = supp
        s.mxs = mxs
        s.mns = -1
        s.gmxs = -1
        s.card = len(contents)
        return s

    def __str__(self, trad={}):
        """
        prettyprint of itemset: support omitted if zero
        optional element translator trad
        """
        s = ""
        for el in sorted(self):
            el = trad.get(el, el)  # get the value of el if exists
            s = s + "," + str(el) if s else str(el)  # concatenate str(el) if s
        s = "{ " + s + " }"
        if self.supp > 0:
            s = s + " (" + str(self.supp) + ")"
        return s

    def __repr__(self, trad={}):
        return self.__str__(trad=trad)

    def revise(self, c):
        '''
        Return a copy, changing the contents of the node
        '''
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
