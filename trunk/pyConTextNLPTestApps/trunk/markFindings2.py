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
"""markFindings.py is a program that illustrates the basic use of pyConTextNLP.

At this state, the program assumes that the reports are stored in a SQLite3 database.
By default the database has a table named 'reports' with a field named 'impression'.
These values can be be specified through the command line options."""
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
import networkx as nx

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
        self.document = pyConText.ConTextDocument()

        self.modifiers = itemData.instantiateFromCSVtoitemData(options.lexical_kb,
                literalColumn=0,
                categoryColumn=1,
                regexColumn=2,
                ruleColumn=3)
        self.targets = itemData.instantiateFromCSVtoitemData(options.domain_kb,
                literalColumn=0,
                categoryColumn=1,
                regexColumn=2,
                ruleColumn=3)

    def initializeOutput(self,rfile,lfile,dfile):
        """Provides run specific information for XML output file"""
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
    def analyzeReport(self, report ):
        """
        given an individual radiology report, creates a pyConTextGraph
        object that contains the context markup
        report: a text string containing the radiology reports
        """
        context = pyConText.ConTextDocument()
        targets = self.targets
        modifiers = self.modifiers
        splitter = helpers.sentenceSplitter()
# alternatively you can skip the default exceptions and add your own
#       splitter = helpers.sentenceSpliter(useDefaults = False)
        #splitter.addExceptionTerms("Dr.","Mr.","Mrs.",M.D.","R.N.","L.P.N.",addCaseVariants=True)
        splitter.addExceptionTerms("Ms.","D.O.",addCaseVariants=True)
        splitter.deleteExceptionTerms("A.B.","B.S.",deleteCaseVariants=True)
        sentences = splitter.splitSentences(report)
        count = 0
        for s in sentences:
            #print s
            markup = pyConText.ConTextMarkup()
            markup.setRawText(s)
            markup.cleanText()
            markup.markItems(modifiers, mode="modifier")
            markup.markItems(targets, mode="target")
            markup.pruneMarks()
            markup.dropMarks('Exclusion')
            markup.applyModifiers()
            print markup
            context.addMarkup(markup)

        self.outString += context.getXML()
        print context.getSectionText()
        #raw_input('continue')
        context.computeDocumentGraph(verbose=True)
        ag = nx.to_pydot(context.getDocumentGraph(), strict=True)
        ag.write("case%03d.pdf"%self.currentCase,format="pdf")
        #print "*"*42
        #print context.getXML(currentGraph=False)
        #print "*"*42
        raw_input('continue')

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
                self.analyzeReport(self.currentText)
                self.outString +=u"</case>\n"
        print "_"*48

def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-b","--db",dest='dbname',
                      help='name of SQLite database containing reports to parse')
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
        f0 = codecs.open(options.ofile+"_pretty.xml",encoding='utf-8',mode="w")
        f0.write(xml.toprettyxml(encoding='utf-8'))
        f0.close()
    except Exception, error:
        print "could not prettify xml"
        print error


if __name__=='__main__':

    main()

