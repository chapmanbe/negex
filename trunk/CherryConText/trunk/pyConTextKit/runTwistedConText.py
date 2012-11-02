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
import sqlite3 as sqlite
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
import pyConTextNLP.helpers as helpers
import time
import os
import gzip
import cPickle
class TwistedConText(object):
    """This is the class definition that will contain the majority of processing
    algorithms for TwistedConText.

    The constructor takes as an argument the name of an SQLite database containing
    the relevant information.
    """
    def __init__(self, db, reports_label, domain_label, lexical_label):
        """create an instance of a TwistedConText object associated with the SQLite
        """


        # Define queries to select data from the SQLite database
        # this gets the reports we will processReports
        self.results = {}
        #replaced reports_table w/ reports_label, reason why included reports_id & reports
        self.query1 = '''SELECT reportid, report FROM pyConTextKit_report WHERE dataset=(?)'''
        print "the database to run from is",db
        self.conn = sqlite.connect(db)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query1, (reports_label,))
        self.reports = self.cursor.fetchall()

		#produces error, and is only used once
        #self.document = pyConText.ConTextDocument()

        self.modifiers = itemData.instantiateFromSQLite(db,lexical_label,
                                                       "pyConTextKit_items")
        self.targets = itemData.instantiateFromSQLite(db, domain_label,
                                                       "pyConTextKit_items")

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
            context.addMarkup(markup)

        context.computeDocumentGraph(verbose=True)
        return context


    def processReports(self):
        """For the selected reports (training or testing) in the database,
        process each report with peFinder
        """
        count = 0
        for r in self.reports:
                self.currentCase = r[0]
                self.currentText = r[1].lower()
                rslt = self.analyzeReport(self.currentText)
                self.results[self.currentCase] = rslt.getDocumentGraph()


def runConText(twistedhome, reports_label="my reports",
        items_label_domain="my domain items",
        items_label_lexical="my lexical items" ):

    pec = TwistedConText(os.path.join(twistedhome,"pyConTextWeb.sqlite"), reports_label,
            items_label_domain,
            items_label_lexical)
    pec.processReports()

    outputDir = os.path.join(twistedhome,"output")
    if( not os.path.exists(outputDir) ):
        os.mkdir(outputDir)
    outfile = os.path.join(outputDir,str(time.time())+".gpickle")
    fo = gzip.open(outfile,"wb")
    cPickle.dump(pec.results,fo)

    return outfile



if __name__=='__main__':

    run()

