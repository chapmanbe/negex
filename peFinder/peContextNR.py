#!/usr/bin/env python
"""This is a file that processes the radiology impression section of CTA
reports. pyContext is used to look for descriptions of pulmonary embolisms.
The analysis looks for historical state, historicity, and uncertainty"""
import sys

import os
from optparse import OptionParser
import sqlite3 as sqlite

import datetime, time
import pyContext.pycontext as pycontext
import pyContext.helpers as helpers
from pyContext.pycontextSql import pycontextSql
import pyContext.pycontextNX as pnx
from pyContext.itemData import *
from peItemData import *
import cPickle

import readDeID

"""helper functions to compute final classifications"""
def qualityState(value):
    if(value):
        return "Not Diagnostic"
    else:
        return "Diagnostic"
def diseaseState(value):
    if( value ):
        return "Pos"
    else:
        return "Neg"
def uncertaintyState(value):
    if( value ):
        return "Yes"
    else:
        return "No"
def notModifiedByOR(terms,modifier):
    for term in terms:
        if(not term.isModifiedBy(modifier)):
            return True
    return False
def historicalState(value):
    if( value ):
        return "Old"
    else:
        return "New"
def getParser():

    parser = OptionParser()
    parser.add_option("-f","--filename",dest='fname',
                      help='name of file containing reports to parse')
   
    return parser



class PEContextNR(object):
    def __init__(self):

        # Create the itemData object to store the modifiers for the  analysis
        self.modifiers = {"disease":itemData.itemData()}
        self.modifiers["disease"].extend(pseudoNegations)
        self.modifiers["disease"].extend(definiteNegations)
        self.modifiers["disease"].extend(probableNegations)
        self.modifiers["disease"].extend(probables)
        self.modifiers["disease"].extend(definites)
        self.modifiers["disease"].extend(indications)
        self.modifiers["disease"].extend(historicals)
        self.modifiers["disease"].extend(conjugates)

        # Create a seperate itemData for the quality modifiers
        self.modifiers["quality"] = itemData.itemData()
        self.modifiers["quality"].extend(pseudoNegations)
        self.modifiers["quality"].extend(definiteNegations)
        self.modifiers["quality"].extend(probableNegations)
        self.modifiers["quality"].extend(probables)
        self.modifiers["quality"].extend(historicals)
        self.modifiers["quality"].extend(conjugates)
        self.modifiers["quality"].extend(qualities)
        self.modifiers["quality"].extend([['limited dataset compliant','EXCLUSION','','']])
        # Quality targets
        self.targets = {"disease":peItems}
        self.targets["quality"] = itemData.itemData()
        #self.targets["quality"].extend(qualities)
        self.targets["quality"].extend(examFeatures)
        self.targets["quality"].extend([['limited dataset compliant','EXCLUSION','','']])

        

        self.targets["quality2"] = itemData.itemData()
        self.targets["quality2"].extend(artifacts)
        self.temporalCount = 0
        self.models = {}

    def splitTypos(self):
        pass
    def analyzePEReport(self, report, mode, modFilters = None ):
        """given a pyContext object and a radiology report creates a pycontextSql
        object that contains the context markup
        context: a pyContext object
        report: a text string containing the radiology reports
        targets: a list of phrases to search for
        modifiers: a list of modifiers to search for
        modFilters: """
        try:
            fo = open("pedoc%d_%s.txt"%(self.currentCase, mode),"w")
            context = self.context.get(mode)
            targets = self.targets.get(mode)
            modifiers = self.modifiers.get(mode)
            if modFilters == None :
                modFilters = ['indication','pseudoneg','probable_negated_existence','definite_negated_existence', 'probable_existence', 'definite_existence', 'historical']
            context.reset()
            terms = itemData.itemData(targets)
            sentences = helpers.sentenceSplitter(report)
            count = 0
            for s in sentences:
                context.setTxt(s) 
                context.markModifiers(modifiers)
                context.markTargets(terms)
                fo.write("Original markup\n%s\n"%context.__str__())
                context.pruneMarks()
                fo.write("Pruned markup\n%s\n"%context.__str__())
                context.dropMarks('Exclusion')
                fo.write("Post Exclusion\n%s\n"%context.__str__())
                context.applyModifiers()
                fo.write("Post modifiers\n%s\n"%context.__str__())
                fo.write("*"*42+"\n")
                pnxobj = pnx.pyConTextGraph(context)
                pnxobj.drawGraph("pedoc%d_%s_%s"%(self.currentCase,context.getCurrentSentenceNumber(),mode), format="png")
                #print context
                context.commit()
                count += 1
            model = pycontextSql(db=self.dbn)
            model.populate(context,modFilters)
            fo.close()
            return model
        except Exception, error:
            print "failed in analyzePEReport", error
    def createModel(self, sentence, mode, filters  ):
        self.setOutput(mode)
        self.models[mode] = self.analyzePEReport( sentence, mode,
                                modFilters=filters)
    def determineDiseaseState(self):
        # determine disease state
        # Disease will be positive if unmodifiedDisease is true
        # or if modifiedDisease['quality'] is true
        ds = diseaseState(bool(self.models["disease"].query(
            "where (unmodified == 'YES' or ((definite_existence == 'YES' or probable_existence == 'YES' ) and\
            pseudoneg == 'NO' and probable_negated_existence == 'NO' and\
            definite_negated_existence ==  'NO' and\
            indication == 'NO'))") or self.models["disease"].query(
            "where historical == 'YES' and probable_negated_existence == 'NO' and definite_negated_existence == 'NO'"
        ) ))
        
        self.disease_state = ds
    def determineQualityState(self):
        # now determine quality
        # quality is true (not-diagnostic) if modifiedQuality['quality'] is
        # true or if unmodifiedquality2 is true
        # make sure quality is uncertainty if no mention of PE is made
        # if finding is negated, don't mark as uncertain #265
        quality = bool(
            #self.models["quality"].query("where unmodified == 'YES'") or
            self.models["quality"].query("where quality_feature == 'YES'") or
            self.models["quality2"].query("where unmodified == 'YES'") ) 
        qs = qualityState(quality)
        self.quality_state = qs
        
    def determineUncertaintyState(self):
        # now determine disease uncertainty
        # uncertainty is true if modifiedDisease['uncertainty'] is true or
        # modifiedDisease[('negation','uncertainty')] or if the quality
        # is not diagnostic
        # uncertain if no mention of PE is made other than as indication fixes pedoc #155
        usd = bool(not self.models["disease"].query("") or \
                   (self.models["disease"].query("where indication == 'YES'") and \
                    not self.models["disease"].query("where probable_negated_existence == 'YES'") and\
                    not self.models["disease"].query("where definite_negated_existence == 'YES'") and\
                    not self.models["disease"].query("where probable_existence == 'YES'") ) )
        us = uncertaintyState(bool( self.models["disease"].query("where probable_negated_existence == 'YES' or probable_existence == 'YES' " ) or\
                                   self.models["disease"].query("where probable_existence == 'YES' and definite_negated_existence == 'YES'") or\
                                    (self.quality_state == "Not Diagnostic" and self.disease_state == 'Neg') or usd) )
        

        self.uncertainty_state = us
    def determineHistoricalState(self):
        self.historical_state = "NULL"
        hs = historicalState(bool(self.models["disease"].query("where historical =='YES'")))
        self.historical_state = hs
    def printContext(self):
        print "%6d\t%s\t%s\t%s\t%s\t%s\t%s"%(
                        self.currentCase,
                        self.b[2].ljust(10).upper(),
                        self.disease_state.ljust(10).lower(),
                        self.b[4].ljust(20).upper(),
                        self.quality_state.ljust(20).lower(),
                        self.b[3].ljust(5).upper(),
                        self.uncertainty_state.ljust(5).lower())
                self.c))

    def processReports(self):
        count = 0
        for r in self.reports:
            self.currentCase = r[0]
            self.currentText = r[1].lower()
            self.setReportDB(self.currentCase, mode = True )
            
            
            if( self.currentCase in self.breakCases ):
                pass #raw_input('continue')
            self.getReaderStates(self.currentCase)
            self.setReportDB(self.currentCase)
            if( self.b ):
                print self.currentCase
                # change program to only return one object
                # Essentialy move unmodifiedDisease into modifiedDiseae with a key of ''
                
                # I think we need to add a reference to the sentence to each tagged obect
                self.createModel(self.currentText, "disease", ['indication','probable_existence','definite_existence',
                                           'historical','pseudoneg','definite_negated_existence','probable_negated_existence'])
                self.createModel(self.currentText, "quality",['quality_feature'])
                self.createModel(self.currentText, "quality2", [])
                try:
                    if( 'NULL' not in self.b ):
                        self.determineDiseaseState()
                        self.determineQualityState()
                        self.determineUncertaintyState()
                        self.determineHistoricalState()
                        count += 1
                except Exception, error:
                    print "failed to process report",error
                    self.problemCases.append(self.currentCase)
                    raw_input('continue')
                self.recordResults()  
        print "processed %d cases"%count
        print "%d problem cases"%len(self.problemCases)
    
            

def main():
    parser = getParser()
    (options, args) = parser.parse_args()
    reports = readDeID.readDeIDTxt(options.fname)   
    pec = PEContext()
    pec.processReports()
    
    
if __name__=='__main__':
    main()
    
