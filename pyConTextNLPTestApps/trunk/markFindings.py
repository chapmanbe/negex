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

from optparse import OptionParser
import sqlite3 as sqlite
import pyConTextNLP
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
import pyConTextNLP.helpers as helpers
import getpass
import time
import xml.dom.minidom as minidom
import codecs

"""helper functions to compute final classification"""

class criticalFinder(object):
    """This is the class definition that will contain the majority of processing
    algorithms for criticalFinder.
    
    The constructor takes as an argument the name of an SQLite database containing
    the relevant information.
    """
    def __init__(self, options):
        """create an instance of a criticalFinder object associated with the SQLite
        database.
        dbname: name of SQLite database
        """
        

        # Define queries to select data from the SQLite database
        # this gets the reports we will process
        self.query1 = '''SELECT %s,%s FROM %s'''%(options.id,options.report_text,options.table)
        
        self.conn = sqlite.connect(options.dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query1)
        self.reports = self.cursor.fetchall()
        
        print "number of reports to process",len(self.reports)
        self.context = pyConText.pyConText()
       
        mods = itemData.instantiateFromCSV(options.lexical_kb)
        trgs = itemData.instantiateFromCSV(options.domain_kb)

        self.modifiers = itemData.itemData()
        for key in mods.keys():
            self.modifiers.prepend(mods[key])

        self.targets = itemData.itemData()
        for key in trgs.keys():
            self.targets.prepend(trgs[key])

    def initializeOutput(self,rfile,lfile,dfile):
        self.outString  =u"""<?xml version="1.0"?>\n"""
        self.outString +=u"""<markup>\n"""
        self.outString +=u"""<pyConTextNLPVersion> %s </pyConTextNLPVersion>\n"""%pyConTextNLP.__version__
        self.outString +=u"""<operator> %s </operator>\n"""%getpass.getuser()
        self.outString +=u"""<date> %s </date>\n"""%time.ctime()
        self.outString +=u"""<dataFile> %s </dataFile>\n"""%rfile
        self.outString +=u"""<lexicalFile> %s </lexicalFile>\n"""%lfile
        self.outString +=u"""<domainFile> %s </domainFile>\n"""%dfile

    def closeOutput(self):
        self.outString +=u"""</markup>\n"""
    def getOutput(self):
        return self.outString
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
            #print s
            context.setRawText(s) 
            context.cleanText()
            context.markItems(modifiers, mode="modifier")
            context.markItems(targets, mode="target")
            g= context.getCurrentGraph()
            ic=0
            context.pruneMarks()
            context.dropMarks('Exclusion')
            context.applyModifiers()
            #context.pruneModifierRelationships()
            context.dropInactiveModifiers()
            print context
            self.outString += context.getXML()+u"\n"
            context.commit()
            count += 1
        context.computeDocumentGraph()    
        #print "*"*42
        #print context.getXML(currentGraph=False)
        #print "*"*42

    def processReports(self):
        """For the selected reports (training or testing) in the database,
        process each report with peFinder
        """
        count = 0
        for r in self.reports[0:20]:
                self.currentCase = r[0]
                self.currentText = r[1].lower()
                print "CurrentCase:",self.currentCase
                self.outString +=u"""<case>\n<caseNumber> %s </caseNumber>\n"""%self.currentCase
                self.analyzeReport(self.currentText,
                                    modFilters=['indication','probable_existence',
                                                'definite_existence',
                                                'historical','future','pseudoneg',
                                                'definite_negated_existence',
                                                'probable_negated_existence'])
                self.outString +=u"</case>\n"
print "_"*48
        
        
def modifies(g,n,modifiers):
    pred = g.predecessors(n)
    if( not pred ):
        return False
    pcats = [n.getCategory().lower() for n in pred]
    return bool(set(pcats).intersection([m.lower() for m in modifiers]))
    
def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-b","--db",dest='dbname',
                      help='name of db containing reports to parse')
    parser.add_option("-o","--output",dest="ofile",
                      help="name of file for xml output",default="output")
    parser.add_option("-l","--lexical_kb",dest='lexical_kb',
                      help='name of csv file containing lexical knowledge', default="lexical_kb.csv")
    parser.add_option("-d","--domain_kb",dest='domain_kb',
                      help='name of csv file containing domain knowledge', default="domain_kb.csv")
    parser.add_option("-t","--table",dest='table',default='reports',
                      help='table in database to select data from')
    parser.add_option("-i","--id",dest='id',default='rowid',
                      help='column in table to select identifier from')
    parser.add_option("-r","--report",dest='report_text',default='impression',
                      help='column in table to select report text from')
    return parser

def main():

    parser = getParser()
    (options, args) = parser.parse_args()
    pec = criticalFinder(options)
    pec.initializeOutput(options.dbname, 
                options.lexical_kb, options.domain_kb)
    pec.processReports()
    pec.closeOutput()
    txt = pec.getOutput()
    f0 = codecs.open(options.ofile+".xml",encoding='utf-8',mode="w")
    f0.write(txt)
    f0.close()
    try:
        xml = minidom.parseString(txt)
        print xml.toprettyxml(encoding="utf-8")
        f0 = codecs.open(options.ofile+"_pretty.xml",encoding='utf-8',mode="w")
        f0.write(xml.toprettyxml(encoding="utf-8"))
        f0.close()
    except Exception, error:
        print "could not prettify xml"
        print error
    
    
if __name__=='__main__':
    
    main()
    
