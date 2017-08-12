"""
Project: slatt
Package: closminer
Programmers: JLB, DGP

Purpuse: obtain list of closures for building a clattice

Several ways:
1/ find them precomputed in a Borgelt apriori output file (deprecated)
2/ find them precomputed in an XML file
3/ mine them by calling external binary for Borgelt's apriori v5.4
4/ mine them by local internal algorithm

If xmlinput is set to True, and the xml file is found, will try 2,
otherwise the next consideration applies

If use_external_miner is set to True, will try 1, then 3 (eg if no
closures file found), then 4 (eg if external apriori not found)

Otherwise 4 is attempted directly

Default is xmlinput False, use_external_miner True

Borgelt's apriori call uses '/' to separate itemset from support,
 will break down if that char appears in any of the items;
 this can be changed below but must change slanode accordingly

Method xmlize() available to write the closures to the XML file

keeps dataset info (scale, nrtr and such) and
 materialized list of closures

nonmaterialized iterator and badly needed
 refactoring left to a brother project for the time being

ToDo:
 set up a local database of filenames and supports

Changes:
 Now, ElementTree is used instead of minidom.

 Classes have attributes _fields and _proccessing. _fields are the attributes
 while proccessing is the set of functions that must be instanciated in __init__.

 There is no method topercent. It is really unnecessary.

 mustsort was always false, now it is a keyword. It sorts by supp.


 When checking conditions, integers and list different from zero are treated as true.

"""

import xml.etree.ElementTree as etree

from collections import defaultdict
from verbosity import verbosity
from subprocess import call
from platform import system
from heapq import heapify, heappush, heappop
from slanode import slanode
from glob import glob
from math import floor
from decorator import Structure


# This is a dictionary which, for each platform, returns the name
# of the binary file plus the correct command
COMMANDS = {
    'Darwin' : ('aprioriD',
                './aprioriD -tc -l1 -u0 -v" /%%a" -s%2.3f %s %s'),
    'Linux'  : ('apriori',
                './apriori -tc -l1 -u0 -v" /%%a" -s%2.3f %s %s'),
    'Windows': ('apriori.exe',
                './apriori.exe -tc -l1 -u0 -v" /%%a" -s%2.3f %s %s'),
    'Microsoft': ('apriori.exe',
                './apriori.exe -tc -l1 -u0 -v" /%%a" -s%2.3f %s %s'),
    'CYGWIN_NT-5.1': ('apriori.exe',
                './apriori.exe -tc -l1 -u0 -v" /%%a" -s%2.3f %s %s'),
    'CYGWIN_NT-6.1-WOW64': ('apriori.exe',
                './apriori.exe -tc -l1 -u0 -v" /%%a" -s%2.3f %s %s'),


}



def post_init(self):
    '''
    This function is an auxiliary function to configure an instance
    of closminer.

    '''
    self.read_from_XML_file = self.xmlinput
    self.xmlfilename = "%s_cl%2.3fs.xml" % (self.datasetfilename,
                                            self.supp_percent)
    self.U = set()
    self.closeds = list()
    if self.v==None:
        self.v = verbosity()
    self.v.inimessg("Initializing lattice")
    if not self.datasetfilename:
        '''
        if not a filename is given.
        '''
        self.v.messg(" with just a bottom empty closure.")
        self.nrocc = 0
        self.nrits = 0
        self.supp_percent = 0.0
        self.card = 0
        self.maxsupp = 0
        self.minsupp = 0
        self.addempty(0)
    else:
        try:
            datasetfile = open(self.datasetfilename+".txt")
        except IOError:
            self.v.errmessg("Could not open file %s.txt"%(self.datasetfilename))
            exit(0)
        self.v.zero(2500)
        self.v.messg("from file %s... computing parameters..."%(self.datasetfilename))
        self.nrocc = 0
        self.U = set([])
        self.transcns = defaultdict(set)
        self.occurncs = defaultdict(set)
        for line in datasetfile:
            self.v.tick()
            for el in line.strip().split():
                if el:
                    isempty = False
                    self.nrocc += 1
                    self.U.add(el)
                    self.transcns[self.nrtr].add(el)
                    self.occurncs[el].add(self.nrtr)
            if not isempty:
                self.nrtr += 1
        self.nrits = len(self.U)  # number of items
        self.intsupp = floor(self.supp * self.nrtr) # support bound into absolute int value
        if not self.supp:
            "Borgelt's apriori might not work with support zero"
            self.supp_percent = 0.001
        else:
            "there remains a scale issue to look at in the clfile name"
            self.supp_percent = 100.0*floor(self.scale*self.supp)/self.scale
        if self.read_from_XML_file:
            self.v.messg("...reading closures from XML file...")
            try:
                self.dexmlize(self.xmlfilename)
                self.v.messg(str(self.card)+" closures found.")
                return
            except IOError:
                self.v.messg(self.xmlfilename+" not found, falling back to mining process...")
        nbord = 0
        if self.use_external_miner:
            "try using results of external apriori, or calling it"
            clfilename = "%s_cl%2.3fs.txt" % (self.datasetfilename,
                                              self.supp_percent)
            suchfiles = glob(self.datasetfilename+"_cl*s.txt")
            if clfilename in suchfiles:
                "avoid calling apriori if closures file already available"
                self.v.messg("...reading closures from file "+clfilename+"...")

            elif system() in COMMANDS:
                exe, cmmnd = COMMANDS[system()]
                self.v.messg("platform appears to be "+system()+";")
                self.v.messg("computing closures by: \n\t%s\n"%(cmmnd))
                if not glob(exe):
                    self.use_external_miner = False
                    self.v.errmessg("%s not found, falling back on internal closure miner" %(exe))
                else:
                    cmmnd = cmmnd %(self.supp_percent,
                                    self.datasetfilename+".txt",
                                    clfilename)
                    call(cmmnd,shell=True)
            else:
                "unhandled platform"
                self.v.errmessg("Platform "+system()+" not handled yet, sorry")
                self.use_external_miner = False
            if self.use_external_miner:
                "closures file in place, either was there or just computed"
                self.card = 0
                self.maxsupp = 0
                self.minsupp = self.nrtr+1
                self.v.zero(250)
                self.v.messg("...loading closures in...")
                for line in open(clfilename,'r').readlines():
                    """
                    ToDo: maybe the file has lower support
                    than desired and we do not want all closures there
                    """
                    self.v.tick()
                    node = slanode(line)
                    self.closeds.append(node)
                    self.card += 1
                    if node.supp > self.maxsupp:
                        self.maxsupp = node.supp
                    if 0 < node.supp < self.minsupp:
                        self.minsupp = node.supp
        if not self.use_external_miner:
            """
            use internal miner either as asked or
            because could not use external apriori
            """
            self.maxsupp = 0
            clos_singl = set([])
            self.v.inimessg("Computing closures at support %3.2f%%;" %
                            (100.0*floor(self.scale*self.supp)/self.scale))
            self.v.messg("singletons first...")
            for item in self.U:
                "initialize (min-)heap with closures of singletons"
                self.v.tick()
                supset = self.occurncs[item]
                supp = len(supset)
                if supp > self.maxsupp:
                    self.maxsupp = supp
                if supp > self.intsupp:
                    clos_singl.add((self.nrtr-supp,
                                    frozenset(self.inters(supset)),
                                    frozenset(supset)))
                else:
                    nbord += 1
            cnt_clos_singl = len(clos_singl)
            self.v.messg(str(cnt_clos_singl) + " such closures; " +
                         "computing larger closures...")
            pend_clos = list(clos_singl.copy())
            heapify(pend_clos)
            self.minsupp = self.nrtr
            while pend_clos:
                "extract largest-support closure and find subsequent ones"
                cl = heappop(pend_clos)
                spp = self.nrtr - cl[0]
                if spp < self.minsupp:
                    self.minsupp = spp
                node = slanode(cl[1],spp)
                self.closeds.append(node)
                self.U.update(node)
                self.card += 1
                for ext in clos_singl:
                    "try extending with freq closures of singletons"
                    if not ext[1] <= cl[1]:
                        self.v.tick()
                        supportset = cl[2] & ext[2]
                        spp = len(supportset)
                        if spp <= self.intsupp:
                            nbord += 1
                        else:
                            next_clos = frozenset(self.inters(supportset))
                            if next_clos not in [ cc[1] for cc in pend_clos ]:
                                heappush(pend_clos, (self.nrtr-len(supportset),
                                                     next_clos, frozenset(supportset)))
    if self.maxsupp < self.nrtr:
        "no bottom itemset, common to all transactions - hence add emtpy"
        self.addempty(self.nrtr)
    else:
        self.v.messg("bottom closure is nonempty;")
    self.v.messg("...done.")

    if self.mustsort:
        self.v.messg("sorting...")
        self.closeds.sort(key=lambda x:x.supp, reverse=True)
        self.mustsort = False

    self.v.messg(str(self.card)+" closures found.")
    if nbord:
        "This info only available if the local miner was used"
        self.v.messg("Additionally checked " + str(nbord) +
                     " infrequent sets as negative border.")
    self.v.inimessg("The max support is "+str(self.maxsupp)+";")
    self.v.messg("the effective absolute support threshold is "+str(self.minsupp)+
              (", equivalent to %2.3f" % (float(self.minsupp*100)/self.nrtr)) +
                 "% of " + str(self.nrtr) + " transactions.")


class closminer(Structure):

    _fields = ['supp',  # support (required)
               'datasetfilename',  # file name of the dataset (required)
               ('v', None),  # verbosity
               ('xmlinput', False),  # read from xml
               ('externalminer', True),  # Use an external miner
               ('use_external_miner', lambda x: x, ['externalminer']), # for using Borgelt apriori
               ('scale', 100000),  # float that is used to convert to a percentage.
               ('supp_percent', lambda x,y: max(100.0*floor(x*y)/x, 0.001), ['scale', 'supp']),
               ('U', set()),  # Universe of items
               ('closeds', list()),
               ('card', 0),
               ('mustsort', False),
               ('nrtr',0), # Number of lines in the file

    ]
    _proccessing = [post_init]


    def addempty(self,nrtr):
        """
        add emptyset as closure, with nrtr as support
        (pushed into the front, not appended)
        """
        node = slanode("", nrtr)
        self.card += 1
        self.closeds.insert(0,node)

    def xmlize(self,outfnm=""):
        '''
        Generate the corresponding xml code
        '''
        topelem = etree.Element("xmlclosurespace")
        contextelem = etree.SubElement(topelem, "context")
        closelem = etree.SubElement(topelem, "closures")
        paramelem = etree.SubElement(contextelem, "parameters",
                                     filename = self.datasetfilename,
                                     support = "{0}%".format(self.supp_percent)
        )
        cd = defaultdict(list)
        for c in self.closeds:
            cd[c.supp].append(c)

        for s in reversed(sorted(cd)):
            cls = sorted([(len(c),hash(c),c) for c in cd[s]])
            for c in cls:
                clelem = etree.SubElement(closelem, "closure",
                                          support = str(c[2].supp),
                                          card = str(c[0]),
                                          hashcode =  str(c[1]))
                for it in sorted(c[2]):
                    etree.SubElement(clelem, "item", value= str(it))

        etree.ElementTree(topelem).write(outfnm if outfnm else self.xmlfilename,
                                         encoding='unicode',
                                         xml_declaration=True)

    def dexmlize(self,clfilename=""):
        """
        closeds already is []
        ToDo: check support in xml file,
        read/write further params there
        (e.g. dataset params)...
        """
        if not clfilename:
            clfilename = self.xmlfilename
        xmldoc = xml.etree.ElementTree.parse(clfilename)
        elemclos = xmldoc.find("closures")
        self.minsupp = self.nrtr
        for clo in elemclos.getchildren():
            "handle a closed set"
            s = set()
            for itelem in clo.getchildren():
                "to do: check they are items"
                it = itelem.get("value")
                s.add(it)
            spp = int(clo.get("support"))
            clos = set2node(s,spp)
            if spp < self.minsupp:
                self.minsupp = spp
            self.closeds.append(clos)
            self.card += 1

    def inters(self,lstr):
        "for an iterable of transactions lstr, return their intersection"
        items = self.U.copy()
        for t in lstr:
            items &= self.transcns[t]
        return items


# if __name__=="__main__":

#     dsfnm = "e13"
#     supp = 0.001
# ##    dsfnm = "pumsb_star"
# ##    supp = 0.7
# ##    dsfnm = "lenses_recoded"
# ##    supp = 0.1


#     c = closminer(supp,dsfnm,xmlinput=True)

#     print c.closeds

#     c.xmlize()
