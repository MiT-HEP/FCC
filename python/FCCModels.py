import re
from HiggsAnalysis.CombinedLimit.PhysicsModel import *

FCC_HIGGS_DECAYS   = [ "hww", "hzz", "hgg", "hbb", 'hmm' , 'hall' ]
FCC_HIGGS_PROD     = [ "ZH","VBFZ","VBFW"]
FCC_ENERGIES       = [ '7TeV', '8TeV', '13TeV', '14TeV', '240GeV', '350GeV']

def getFCCHiggsProdDecMode(bin,process,options):
    """Return a triple of (production, decay, energy)"""
    processSource = process
    decaySource   = options.fileName+":"+bin # by default, decay comes from the datacard name or bin label
    if "_" in process: 
        (processSource, decaySource) = "_".join(process.split("_")[0]),process.split("_")[-1] # ignore anything in the middle for SM-like higgs
        if decaySource not in FCC_HIGGS_DECAYS:
            print "ERROR", "Validation Error: signal process %s has a postfix %s which is not one recognized higgs decay modes (%s)" % (process,decaySource,FCC_HIGGS_DECAYS)
            #raise RuntimeError, "Validation Error: signal process %s has a postfix %s which is not one recognized higgs decay modes (%s)" % (process,decaySource,FCC_HIGGS_DECAYS)
    if processSource not in FCC_HIGGS_PROD :
        raise RuntimeError, "Validation Error: signal process %s not among the allowed ones." % processSource
    #
    foundDecay = None
    for D in FCC_HIGGS_DECAYS:
        if D in decaySource:
            if foundDecay: raise RuntimeError, "Validation Error: decay string %s contains multiple known decay names" % decaySource
            foundDecay = D
    if not foundDecay: raise RuntimeError, "Validation Error: decay string %s does not contain any known decay name" % decaySource
    #
    foundEnergy = None
    for D in FCC_ENERGIES:
        if D in decaySource:
            if foundEnergy: raise RuntimeError, "Validation Error: decay string %s contains multiple known energies" % decaySource
            foundEnergy = D
    if not foundEnergy:
        for D in FCC_ENERGIES:
            if D in options.fileName+":"+bin:
                if foundEnergy: raise RuntimeError, "Validation Error: decay string %s contains multiple known energies" % decaySource
                foundEnergy = D
    if not foundEnergy:
        foundEnergy = '350GeV' ## To ensure backward compatibility
        print "Warning: decay string %s does not contain any known energy, assuming %s" % (decaySource, foundEnergy)
    #
    return (processSource, foundDecay, foundEnergy)


##########################################
### FCC MODEL
##########################################

class FccHiggs(PhysicsModel):
    "Float ggH and ttH together and VH and qqH together"
    def __init__(self):
        PhysicsModel.__init__(self) # not using 'super(x,self).__init__' since I don't understand it

    def doParametersOfInterest(self):
        """Create POI out of signal strength and MH"""
        # --- Signal Strength as only POI --- 
        self.modelBuilder.doVar("width[1,.5,1.5]")
        self.modelBuilder.doVar("kappaZ[1,0.5,1.5]")
        self.modelBuilder.doVar("kappaW[1,0.5,1.5]")
        self.modelBuilder.doVar("kappaB[1,0.5,1.5]")
        self.modelBuilder.doVar("kappaG[1,0.5,1.5]")
        #self.modelBuilder.doVar("kappaT[1,0.5,1.5]")
        self.modelBuilder.doVar("kappaM[1,0.5,1.5]")


        self.kappaMap = { ## maps decays -> kappa
                "hzz" : "kappaZ",
                "hww" : "kappaW",
                "hbb" : "kappaB",
                "hgg" : "kappaG",
                "hmm" : "kappaM",
                }

        self.modelBuilder.doSet("POI","width,kappaZ,kappaW,kappaB,kappaG,kappaM")
        self.setup()

    def setup(self):
        ''' these scalings maps in a variable scaling_prod_decay with the kappas and the width'''
        for prod in FCC_HIGGS_PROD:
            for decay in FCC_HIGGS_DECAYS:
                formula = ""
                if prod == "ZH" and decay == "hall": 
                    formula = '"@0*@0",kappaZ'
                elif prod == "ZH" : 
                    formula = '"@0*@0*@1*@1/(@2*@2)",kappaZ,'+self.kappaMap[decay]+',width'
                elif prod == "VBFZ" and decay == "hall": 
                    formula = '"@0*@0",kappaZ'
                elif prod == "VBFZ" : 
                    formula = '"@0*@0*@1*@1/(@2*@2)",kappaZ,'+self.kappaMap[decay]+',width'
                elif prod == "VBFW" and decay == "hall": 
                    formula = '"@0*@0",kappaW'
                elif prod == "VBFW" : 
                    formula = '"@0*@0*@1*@1/(@2*@2)",kappaW,'+self.kappaMap[decay]+',width'

                print "DEBUG: creating ","expr::scaling_"+prod + "_" + decay + "(" + formula +")"
                self.modelBuilder.factory_("expr::scaling_"+prod + "_" + decay + "(" + formula +")")

    def getYieldScale(self,bin,process):
        "Split in production and decay, and call getHiggsSignalYieldScale; return 1 for backgrounds "
        if not self.DC.isSignal[process]: return 1
        (processSource, foundDecay, foundEnergy) = getFCCHiggsProdDecMode(bin,process,self.options)
        return self.getHiggsSignalYieldScale(processSource, foundDecay, foundEnergy)

    def getHiggsSignalYieldScale(self,production,decay, energy):
        name = "scaling_"
        name += production  +"_"
        name += decay
        if self.modelBuilder.out.function(name) == None:
            print "looking for production", production, "decay",decay,"energy",energy
            raise ValueError("unable to find in model: '" + name +"'")
        return name

fccHiggs=FccHiggs()
