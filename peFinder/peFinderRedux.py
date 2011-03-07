#!/usr/bin/env python
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
"""peFinder is a program that processes the impression section of dictated
reports for CTPA exams. pyContext is used to look for descriptions of pulmonary embolisms.
The analysis looks for historical state, historicity, and uncertainty.

At this state, the program assumes that the reports are stored in a SQLite3 database.
The database is also presumed to contain user annotations, that the pyConText results
are compared to."""
import sys

import os
from optparse import OptionParser
import sqlite3 as sqlite

import datetime, time
import pyConText.pycontext as pycontext
import pyConText.helpers as helpers
from pyConText.pycontextSql import pycontextSql
import pyConText.pycontextNX as pnx
from pyConText.itemData import *
from peItemData import *
import cPickle
"""helper functions to compute final classification accuracies by comparison
to human annotations"""

def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-d","--db",dest='dbname',
                      help='name of db containing reports to parse')
    parser.add_option("-t","--test",dest='test',action='store_true',default=False, help='run on testing set')
    parser.add_option("-u","--user",dest='user',default="negex1b",
                      help='name of user for parser')
    parser.add_option("-c","--comment",dest="comment",default="",help="description of this algorithm")
   
    return parser



class PEContext(object):
    """This is the class definition that will contain the majority of processing
    algorithms for peFinder.
    
    The constructor takes as an argument the name fo an SQLite database containing
    the relevant information.
    """
    def __init__(self, dbname):
        """create an instance of a PEContext object associated with the SQLite
        database.
        dbname: name of SQLite database
        """

        # Define queries to select data from the SQLite database
        # this gets the reports we will process
        self.query1 = '''SELECT id,impression FROM pesubject''' 
        # get the consensus labels for the disease and quality states
        self.query2 = '''SELECT diseaseState,qualityState,CDS,diseaseUncertainty,CQS FROM consensus_states WHERE psid==?'''
        # get the userannotations from the three raters we are using for this
        # study
        self.query3 = """SELECT usrname,diseaseState,qualityState,qualitylimit,usrname FROM userannotations where psid_id == ? AND (usrname=='aaron' OR usrname=='hyun' OR usrname=='sean')"""
        # create query to get temporal annotations
        self.query4 = """SELECT usrname FROM AND (usrname == 'jd' OR usrname =='sean' OR usrname=='peter')"""


        self.conn = sqlite.connect(dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query1)
        # get the training set reports. The first 20 reports were used to train
        # Aaron and Hyun and so can be skipped
        reports = self.cursor.fetchall()
        if( not test ):
            self.reports = (reports[20:])[:250]
        else:
            self.reports = reports[270:]
        print "number of reports to process",len(self.reports)
        raw_input('continue')
        t = time.localtime()
        d = datetime.datetime(t[0],t[1],t[2])
        
        # create context objects for each of the questions we want to be answering
        self.context = {"disease":pycontext.pycontext(),
                        "quality":pycontext.pycontext(),
                        "quality2":pycontext.pycontext()}


        rsltsDB = dbname+"Results.db"
        if( os.path.exists(rsltsDB) ):
            os.remove(rsltsDB)
        
        self.resultsConn = sqlite.connect(rsltsDB)
        self.resultsCursor = self.resultsConn.cursor()
        self.resultsCursor.execute("""CREATE TABLE results (
            id INT PRIMARY KEY,
            disease TEXT,
            uncertainty TEXT,
            historical TEXT,
            quality TEXT)""")


        # Create the itemData object to store the modifiers for the  analysis
        # starts with definitions defined in pyConText and then adds
        # definitions specific for peFinder
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
    def setOutput(self, mode = "disease"):
        if( self.dbName != None ):
            self.dbn = mode+self.dbName                        
            if( os.path.exists(self.dbn)):
                os.remove(self.dbn)
        else:
            self.dbn = None

    def analyzePEReport(self, report, mode, modFilters = None ):
        """given an individual radiology report, creates a pyConTextSql
        object that contains the context markup

        report: a text string containing the radiology reports
        mode: ???
        modFilters: """
        try:
            fo = open("pedoc%d_%s.txt"%(self.currentCase, mode),"w")
            context = self.context.get(mode)
            targets = self.targets.get(mode)
            modifiers = self.modifiers.get(mode)
            if modFilters == None :
                modFilters = ['indication','pseudoneg','probable_negated_existence',
                              'definite_negated_existence', 'probable_existence',
                              'definite_existence', 'historical']
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
                pnxobj.drawGraph("pedoc%d_%s_%s"%\
                                 (self.currentCase,
                                  context.getCurrentSentenceNumber(),
                                  mode), format="png")
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
        """determine disease state for current object.
        Disease state will be positive if
            unmodifiedDisease is true OR modifiedDisease['quality'] is true
        """
        ds = diseaseState(bool(self.models["disease"].query(
            "where (unmodified == 'YES' or ((definite_existence == 'YES' or probable_existence == 'YES' ) and\
            pseudoneg == 'NO' and probable_negated_existence == 'NO' and\
            definite_negated_existence ==  'NO' and\
            indication == 'NO'))") or self.models["disease"].query(
            "where historical == 'YES' and probable_negated_existence == 'NO' and definite_negated_existence == 'NO'"
        ) ))
        
        if( ds != self.b[2] ):
            self.disagreements["ds"].append(self.currentCase)
            self.f1.write("%d\nusers(%s):algorithm(%s)\ndisease model\n%s\n%s\n"%\
                     (self.currentCase, self.b[2], ds, self.models["disease"],"*"*42))
        self.dsMatrix[(self.b[2],ds)] += 1
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
        if( qs != self.b[4] ):
            self.disagreements["qs"].append(self.currentCase)
            self.f2.write("%d\nusers(%s):algorithm(%s)\n\n%s\n%s\n%s\n"%\
                     (self.currentCase,self.b[4],qs,self.models["quality"],self.models["quality2"],"*"*42))
        self.qsMatrix[(self.b[4],qs)] += 1
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
        us = uncertaintyState(bool(
            self.models["disease"].query("where probable_negated_existence == 'YES' or probable_existence == 'YES' " ) or\
            self.models["disease"].query("where probable_existence == 'YES' and definite_negated_existence == 'YES'") or\
            (self.quality_state == "Not Diagnostic" and self.disease_state == 'Neg') or usd) )
        
        self.uncertainty_state = us
    def determineHistoricalState(self):
        self.historical_state = "NULL"
        hs = historicalState(bool(self.models["disease"].query("where historical =='YES'")))
        
    def printContext(self):
        print "%6d\t%s\t%s\t%s"%(
                        self.currentCase,
                        self.disease_state.ljust(10).lower(),
                        self.quality_state.ljust(20).lower(),
                        self.uncertainty_state.ljust(5).lower())

    def processReports(self):
        """For the selected reports (training or testing) in the database,
        process each report with peFinder
        """
        count = 0
        for r in self.reports:
            self.currentCase = r[0]
            self.currentText = r[1].lower()
            self.setReportDB(self.currentCase, mode = True )
            
            
            if( self.currentCase in self.breakCases ):
                pass #raw_input('continue')
            self.getReaderStates(self.currentCase)
            self.setReportDB(self.currentCase)

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
    
    def recordResults(self):
        query = """INSERT INTO results (id,disease, uncertainty, historical, quality) VALUES (?,?,?,?,?)"""
        self.resultsCursor.execute(query,(self.currentCase,self.disease_state,self.uncertainty_state,self.historical_state,self.quality_state,))
        
        
    def cleanUp(self):     
        self.f1.close()
        self.f2.close()
        self.f3.close()
        self.conn.close()
        self.resultsConn.commit()

        
def getStats(m,pos='Pos',neg='Neg',label=''):
    ppv = m[(pos,pos)]/float(m[(pos,pos)]+m[(neg,pos)])
    sens = m[(pos,pos)]/float(m[(pos,pos)]+m[(pos,neg)])
    spec = m[(neg,neg)]/float(m[(neg,neg)]+m[(neg,pos)])
    acc = float(m[(pos,pos)]+m[(neg,neg)])/(m[(pos,pos)]+m[(neg,neg)]+m[(pos,neg)]+m[(neg,pos)])
    print label
    print "PPV=",ppv, m[(pos,pos)],m[(pos,pos)]+m[(neg,pos)]
    print "Sens=",sens, m[(pos,pos)], m[(pos,pos)]+m[(pos,neg)]
    print "Spec=",spec, m[(neg,neg)], m[(neg,neg)]+m[(neg,pos)]
    print "Accuracy=",acc, m[(pos,pos)]+m[(neg,neg)], m[(pos,pos)]+m[(neg,neg)]+m[(pos,neg)]+m[(neg,pos)]
            

def main():
    parser = getParser()
    (options, args) = parser.parse_args()
        
    pec = PEContext(options.dbname, options.test)
    pec.processReports()
    pec.getResults()
    pec.saveDisagreements()
    pec.cleanUp()
    
    
if __name__=='__main__':
    main()
    
