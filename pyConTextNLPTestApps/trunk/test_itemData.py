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

class test_itemData(object):
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
        
       
        self.items = itemData.instantiateFromCSVtoitemData(options.items,
                literalColumn=options.lc,
                categoryColumn=options.cc,
                regexColumn=options.rec,
                ruleColumn=options.ruc)


    def test_itemData(self):
        for m in self.items:
            reg = m.getRE()
            if( reg ):
                context = pyConText.ConTextMarkup()
                reg = m.getLiteral()
                r = re.compile(reg,re.IGNORECASE|re.UNICODE); 
                print "l: %s; r: %s"%(m.getLiteral(),m.getRE())
                print bool(r.findall(m.getLiteral())),r.findall(m.getLiteral())
                print "Now clean text"
                context.setRawText(reg)
                context.cleanText()
                print bool(r.findall(context.getText())),r.findall(context.getText())
                print "_"*42

    
def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-i","--items",dest='items',
                      help='name of csv file containing itemData', default="")
    parser.add_option("-l","--literal",dest='lc',type='int', default=0,
                      help='column in file to select literal from')
    parser.add_option("-c","--category",dest='cc',type='int', default=1,
                      help='column in file to select category from')
    parser.add_option("-r","--regex",dest='rec',type='int', default=2,
                      help='column in file to select regular expression from')
    parser.add_option("-u","--rule",dest='ruc',type='int', default=3,
                      help='column in file to select rule from')
    return parser

def main():

    parser = getParser()
    (options, args) = parser.parse_args()
    pec = test_itemData(options)
    pec.test_itemData()
    
    
if __name__=='__main__':
    
    main()
    
