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
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
import pyConTextNLP.helpers as helpers
import re
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

    def testModifiers(self):
        for m in self.modifiers:
            reg = m.getRE()
            if( reg ):
                reg = m.getLiteral()
                r = re.compile(reg,re.IGNORECASE|re.UNICODE); 
                print "l: %s; r: %s"%(m.getLiteral(),m.getRE())
                print bool(r.findall(m.getLiteral())),r.findall(m.getLiteral())
                print "Now clean text"
                self.context.setRawText(reg)
                self.context.cleanText()
                print bool(r.findall(self.context.getText())),r.findall(self.context.getText())
                print "_"*42

    def testTargets(self):
        for m in self.targets:
            reg = m.getRE()
            if( reg ):
                reg = m.getLiteral()
                r = re.compile(reg,re.IGNORECASE|re.UNICODE); 
                print "l: %s; r: %s"%(m.getLiteral(),m.getRE())
                print bool(r.findall(m.getLiteral())),r.findall(m.getLiteral())
                print "_"*42

        
    
def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-b","--db",dest='dbname',
                      help='name of db containing reports to parse')
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
    pec.testModifiers()
    raw_input('continue')
    pec.testTargets()
    
    
if __name__=='__main__':
    
    main()
    
