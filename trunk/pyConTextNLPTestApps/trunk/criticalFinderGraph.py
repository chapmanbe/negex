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
"""criticalFinderGraph is a program that processes the impression section of dictated
radiology reports. pyContext is used to look for descriptions of acute critical
fidnings.

At this state, the program assumes that the reports are stored in a SQLite3 database.
The database should have a table named 'reports' with a field named 'impression'
although these values can be specified through the command line options."""
import sys

import os
from optparse import OptionParser
import sqlite3 as sqlite
import networkx as nx
import time
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.helpers as helpers
from critfindingItemData import *
"""helper functions to compute final classification"""

class criticalFinder(object):
    """This is the class definition that will contain the majority of processing
    algorithms for criticalFinder.
    
    The constructor takes as an argument the name of an SQLite database containing
    the relevant information.
    """
    def __init__(self, options):#dbname, outfile, save_dir, table, idcolumn, txtcolumn, doGraphs):
        """create an instance of a criticalFinder object associated with the SQLite
        database.
        dbname: name of SQLite database
        """

        # Define queries to select data from the SQLite database
        # this gets the reports we will process
        self.query1 = '''SELECT %s,%s FROM %s'''%(options.id,options.report_text,options.table)
        
        self.save_dir = options.save_dir
        if( not os.path.exists(self.save_dir) ):
            os.mkdir(self.save_dir)
        
        self.allow_uncertainty = options.allow_uncertainty
        self.proc_category = options.category
        self.conn = sqlite.connect(options.dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query1)
        self.reports = self.cursor.fetchall()
        
        print "number of reports to process",len(self.reports)
        self.context = pyConText.pyConText()
        
        self.modifiers = "disease":itemData()
        self.modifiers.prepend(pseudoNegations)
        self.modifiers.prepend(definiteNegations)
        self.modifiers.prepend(probableNegations)
        self.modifiers.prepend(probables)
        self.modifiers.prepend(definites)
        self.modifiers.prepend(indications)
        
        self.modifiers.prepend(conjugates)
        self.modifiers.prepend(future)
        self.modifiers.prepend(historicals)

        # Quality targets
        if( options.category.lower() == 'all'):
            targetItems = critItems
        else:
            targetItems = [i for i in critItems if i.getCategory() == options.category]
        self.targets = targetItems
        self.models = {}

    def analyzeReport(self, report, modFilters = None ):
        """given an individual radiology report, creates a pyConTextSql
        object that contains the context markup

        report: a text string containing the radiology reports
        modFilters: """
        context = self.context
        targets = self.targets
        modifiers = self.modifiers
        if modFilters == None :
            modFilters = ['indication','pseudoneg','probable_negated_existence',
                          'definite_negated_existence', 'probable_existence',
                          'definite_existence', 'historical']
        context.reset()
        sentences = helpers.sentenceSplitter(report)
        count = 0
        for s in sentences:
            context.setTxt(s) 
            context.markItems(modifiers, mode="modifier")
            context.markItems(targets, mode="target")
            context.pruneMarks()
            context.dropMarks('Exclusion')
            context.applyModifiers()
            #context.pruneModifierRelationships()
            context.dropInactiveModifiers()
            context.commit()
            count += 1
        #context.computeDocumentGraph()    

    def classifyDocumentTargets(self):
        cntxt = self.context
        cntxt.computeDocumentGraph()
        g = cntxt.getDocumentGraph()
        targets = [n[0] for n in g.nodes(data = True) if n[1].get("category","") == 'target']
        
        if( not targets ):
            return alerts,rslts
        if(self.allow_uncertainty):
            pos_filters = ["definite_existence","probable_existence"]
        else:
            pos_filters = ["definite_existence"]
        for t in targets:
            mods = g.predecessors(t)
            rslts[t] = {}
            if( not mods ): # an unmodified target is disease positive,certain, and acute
                
                rslts[t]['disease'] = 'Pos'
                rslts[t]['uncertainty'] = 'No'
                rslts[t]['temporality'] = 'New'
            else:
                if (modifies(g,t,pos_filters) and
                    not modifies(g,t,[#"definite_negated_existence",
                                      #"probable_negated_existence",
                                      "future","indication","pseudoneg"])):
                    rslts[t]['disease'] = 'Pos'
                else:
                    rslts[t]['disease'] = 'Neg'
                if( modifies(g,t,["probable_existence",
                                  "probable_negated_existence"]) ):
                    rslts[t]['uncertainty'] = 'Yes'
                else:
                    rslts[t]['uncertainty'] = 'No'
                if( modifies(g,t,["historical"]) ):
                    rslts[t]['temporality'] = 'Old'
                else:
                    if( rslts[t]['disease'] == 'Neg'):
                        rslts[t]['temporality'] = 'NA'
                    else:
                        rslts[t]['temporality'] = 'New'
            rsum = alerts.get(t.getCategory(),0)
            if( rslts[t]["disease"] == 'Pos' and rslts[t]["temporality"] == 'New'):
                alert = 1
            else:
                alert = 0
            rsum = max(rsum,alert)
            alerts[t.getCategory()] = rsum

        return alerts, rslts   

    def plotGraph(self):
        cntxt = self.context["disease"]
        g = cntxt.getDocumentGraph()
        ag = nx.to_pydot(g, strict=True)
        gfile = os.path.join(self.save_dir,
                             "report_%s_unc%s_%s_critical.pdf"%(self.proc_category,
                                                                self.allow_uncertainty,
                                                          self.currentCase))
        ag.write(gfile,format="pdf")
    def processReports(self):
        """For the selected reports (training or testing) in the database,
        process each report with peFinder
        """
        count = 0
        for r in self.reports:
                self.currentCase = r[0]
                self.currentText = r[1].lower()
                self.analyzeReport(self.currentText,
                                    "disease",
                                    modFilters=['indication','probable_existence',
                                                'definite_existence',
                                              'historical','future','pseudoneg',
                                              'definite_negated_existence',
                                              'probable_negated_existence'])

                self.recordResults()  
    
    def recordResults(self):

        alerts, rslts = self.classifyDocumentTargets()
        if( self.doGraphs and rslts):
            self.plotGraph()
        targets = rslts.keys()
        if(  targets ):
            print self.currentCase
            query = """INSERT INTO results (reportid,category, disease, uncertainty, historical, literal, matchedphrase) VALUES (?,?,?,?,?,?,?)"""
            for t in targets:
                self.resultsCursor.execute(query,
                                           (self.currentCase,
                                            t.getCategory(),
                                            rslts[t]["disease"],
                                            rslts[t]["uncertainty"],
                                            rslts[t]["temporality"],
                                            t.getLiteral(),
                                            t.getPhrase(),))
        keys = alerts.keys()
        if( keys ):
            query = """INSERT INTO alerts (reportid,category, alert, report) VALUES (?,?,?,?)"""
            for c in keys:
                self.resultsCursor.execute(query,(self.currentCase,c,alerts[c],self.currentText,))
        
        
    def cleanUp(self):     
        self.resultsConn.commit()

        
def modifies(g,n,modifiers):
    pred = g.predecessors(n)
    if( not pred ):
        return False
    pcats = [n.getCategory().lower() for n in pred]
    return bool(set(pcats).intersection([m.lower() for m in modifiers]))
    
def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-d","--db",dest='dbname',
                      help='name of db containing reports to parse')
    parser.add_option("-o","--odb",dest='odbname',
                      help='name of db containing results', default="testOutput.db")
    parser.add_option("-s","--save_dir",dest='save_dir',default='critFinderResults',
                      help='directory in which to store graphs of markups')
    parser.add_option("-t","--table",dest='table',default='reports',
                      help='table in database to select data from')
    parser.add_option("-i","--id",dest='id',default='rowid',
                      help='column in table to select identifier from')
    parser.add_option("-g", "--graph",action='store_true', dest='doGraphs',default=False)
    parser.add_option("-r","--report",dest='report_text',default='impression',
                      help='column in table to select report text from')
    parser.add_option("-c","--category",dest='category',default='ALL',
                      help='category of critical finding to search for. If ALL, all categories are processed')
    parser.add_option("-u","--uncertainty_allowed",dest="allow_uncertainty",
                      action="store_true",default=False)
    return parser

def main():

    parser = getParser()
    (options, args) = parser.parse_args()
    if( options.dbname == options.odbname ):
        raise ValueError("output database must be distinct from input database")        
    pec = criticalFinder(options)
    pec.processReports()
    pec.cleanUp()
    
    
if __name__=='__main__':
    
    main()
    
