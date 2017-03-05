"""
Project: Slatt
Package: corr
Creation: november 25th, 2008, and thoroughly revised afterwards. There
are a few changes from a previous version. First of all, there is a new attribute
of type verbosity, set to false, so it does not print anything. The
algorithm has also changed, now the idea is to sage all the values
g in the dictionary together with the minimal elements ee such that
g in self[ee].
Programmers: JLB, DGP

Purpose:
.implement correspondence tightening
..(auxiliary process for rule mining)

Inherits from dict:
.it is a dict of lists
.the dict keys must admit a comparison operation (partial order)
.adds the operation of tightening: each element in a list remains only
 in those lists corresponding to keys that are maximal among those
 keys of lists where the element appears

ToDo:
.try to find better algorithmics
"""

from decorator import Structure
class corr(dict, Structure):

    __fields = [('v', 'l')]

    def tighten(self,progcnt=None):
        "may use a verbosity object progcnt to report progress"
        ticking = (progcnt!=None)
        # max_elements contains the maximal ee, such that g in self[ee]
        max_elements = dict()
        for ee in self:
            for g in self[ee]:
                # We check the previous elements, and add a new one if maximal
                temp = max_elements.get(g, set())
                if not any(ee < e for e in temp):
                    # If we add a new maximal, it is possible to remove some.
                    temp = {e for e in temp if not e < ee}
                    temp.add(ee)
                    max_elements[g] = temp
        # Now, to check the conditions, we check the values in max_elements
        for e in self:
            if ticking:
                progcnt.tick()
            valids = []
            for g in self[e]:
                if not any(e <ee for ee in max_elements[g]):
                    valids.append(g)
            self[e] = valids

if __name__=="__main__":

    print ("slatt module corr called as main and running as test...")

    c = corr()

    for i in range(10):
        c[i] = []
        for k in range(6):
            c[i].append(str(i+3*k))

    print ("===")

    print (c)

    for e in c.keys():
        print (e, ":", c[e])

    print ("===")

    c.tighten()

    print ("===")

    print (c)

    for e in c.keys():
        print (e, ":", c[e])
    print ("===")
