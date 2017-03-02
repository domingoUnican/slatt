"""
Project: Slatt
Package: verbosity
Created: Apr 16th, 2009, on the basis of a lot of previous work, then revised
Programmers: JLB, DGP

Offers:
.handling of verbosity including messages and progress reporting
.please use this class for ALL terminal output in the project

ToDo:
.add some testing in the __main__
.some day it will become a GUI
.this class should be parent class for all the classes that needs verbosity
.there is code repetition, checking if verb. This could be avoided
"""
from decorator import Structure


class verbosity(Structure):
    """
    Offers messaging of what is ongoing and ascii-based progress report
    Everything can be put off through the verbosity level
    """
    _fields = [('verb', True), ('lim', 0), ('count', 0)]

    def messg(self, s):
        if not self.verb:
            return
        print(s, end='')  # This prints in the same line

    def inimessg(self, s):
        "initiates a sequence of related messg's"
        if not self.verb:
            return
        print("\n[Slatt] "+s, end='')

    def errmessg(self,s):
        print("\n[Slatt] Something is wrong! "+s)

    def zero(self,newlim=0):
        self.count = 0
        if newlim>0: self.lim = newlim

    def tick(self):
        if not self.verb:
            return
        self.count += 1
        if self.count == self.lim:
            print('.', end='')
            self.count = 0

    def __str__(self):
        return 'Verbosity: {0}\nLimit: {1}\nCount: {2}\n'.format(self.verb,
                                                                   self.lim,
                                                                   self.count)


if __name__=="__main__":
    pass

##    print "slatt module verbosity called as main and running as test..."
