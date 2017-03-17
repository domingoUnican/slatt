from rerulattice import rerulattice
from closurererulattice import clrerulattice
from slarule import printrules

class job:

    def __init__(self,datasetfilename,supp,verbose=True):
        """
        duplicate lattice to be simplified (but first attempt failed)
        job consists of 
          dataset file name, extension ".txt" explicitly added
          support threshold in [0,1],
        """
        self.verb = verbose
        self.datasetfilename = datasetfilename
        self.supp = supp
        self.rerulatt = None
        self.clrerulatt = None

    def run(self,basis,conf=1.0,show=False,outrules=False,verbose=True):
        """
        the run method consists of
          target basis ("GenRR", "RRGenerator", or "RRClosureGenerator")
          confidence threshold in [0,1),
          show: whether rules will be shown interactively
          outrules: whether rules will be stored in a file
        """
        basis2 = basis
        if basis == "GenRR":
            if self.rerulatt is None:
                self.rerulatt = rerulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.rerulatt.xmlize()
            self.rerulatt.v.verb = verbose and self.verb
            latt = self.rerulatt
            rules = self.rerulatt.mineKrRR(self.supp,conf)
            secondminer = self.rerulatt.mineKrRR
        elif basis == "RRGenerator":
            if self.rerulatt is None:
                self.rerulatt = rerulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.rerulatt.xmlize()
            self.rerulatt.v.verb = verbose and self.verb 
            latt = self.rerulatt
            rules = self.rerulatt.mineRR(self.supp,conf)
            secondminer = self.rerulatt.mineRR
        elif basis == "RRClosureGenerator":
            if self.clrerulatt is None:
                self.clrerulatt = clrerulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.clrerulatt.xmlize()
            self.clrerulatt.v.verb = verbose and self.verb 
            latt = self.clrerulatt
            rules = self.clrerulatt.mineClosureRR(self.supp,conf)
            secondminer = self.clrerulatt.mineClosureRR
        else:
            "a print because there may be no lattice and no verbosity - to correct soon"
            print "Basis unavailable; options: GenRR, RRGenerator, RRClosureGenerator"
            return 0
        count = None
        if outrules:
            outrulesfile = file(self.datasetfilename+basis2+("_c%2.3f"%conf)+("_s%2.3f"%self.supp)+".txt","w")
            count = printrules(rules,latt.nrtr,outrulesfile,doprint=True)
        if show:
            print "\n\n"
            count = printrules(rules,latt.nrtr,outfile=None,doprint=True)
        if not count:
            count = printrules(rules,latt.nrtr,outfile=None,doprint=False)
        print basis+" basis on "+self.datasetfilename+".txt has ", count, "rules of confidence at least", conf
        return count

if __name__=="__main__":

    testjob = job("./datasets/test",0.4)
    testjob.run("RRClosureGenerator",conf=0.7,show=True)
    testjob.run("RRGenerator",conf=0.7,show=False)
    testjob.run("GenRR",conf=0.7,outrules=True,show=False)
    cnt = testjob.run("GenRR",conf=0.7,show=True)
    print cnt
