#Copyright 2010 Brian E. Chapman
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
#
#Modified by Annie T. Chen, June-Aug., 2011.
"""
CriticalFinderGraph is a program that processes the impression section of dictated
radiology reports. pyContext is used to look for descriptions of acute critical
fidnings.

At this state, the program assumes that the reports are stored in a SQLite3 database.
The database should have a table named 'reports' with a field named 'impression'
although these values can be specified through the command line options.
"""
from django.db.models import Count
from pyConTextKit.models import Report, Result, Alert
import sys
import os
from optparse import OptionParser
import sqlite3 as sqlite
import networkx as nx
import datetime, time
import pyConTextNLP.helpers as helpers
import pyConTextGraphV2.pyConTextGraphV2 as pyConText
from pyConTextGraphV2.pyConTextSqlV2 import pyConTextSql
from pyConTextGraphV2 import itemData
import cPickle
import unicodecsv

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

        t = time.localtime()

        self.doGraphs = options.doGraphs
        self.allow_uncertainty = options.allow_uncertainty
        self.proc_category = options.category

        self.reports = Report.objects.filter(dataset=options.dataset)[:options.number]

        #print "number of reports to process",len(self.reports)
        #raw_input('continue')

        # create context objects for each of the questions we want to be answering
        self.context = {"disease":pyConText.pyConText()}

        rsltsDB = options.odbname

        alerts=Alert.objects.all()
        alerts.delete()
        rslts=Result.objects.all()
        rslts.delete()

        # Create the itemData object to store the modifiers for the  analysis
        # starts with definitions defined in pyConText and then adds
        # definitions specific for peFinder

        #label specifies whether the user wants a domain or linguistic set.

        #items returns an array of contextItems (e.g. getCategory(), getLiteral() )
        items_modifiers = itemData.instantiateFromSQLite("../pyConTextWeb.db",options.label_modifiers,"pyConTextKit_lexical")
        items_targets = itemData.instantiateFromSQLite("../pyConTextWeb.db",options.label_targets,"pyConTextKit_lexical")
		#itemData = itemData.itemData(items)
        """
        probableNegations = itemData('PROBABLE_NEGATED_EXISTENCE')
        definiteNegations = itemData('DEFINITE_NEGATED_EXISTENCE')
        pseudoNegations = itemData('PSEUDONEG')
        indications = itemData('INDICATION')
        historicals = itemData('HISTORICAL')
        conjugates = itemData('CONJ')
        probables = itemData('PROBABLE_EXISTENCE')
        definites = itemData('DEFINITE_EXISTENCE')
        future = itemData('FUTURE')
        critItems = itemData('CRIT_ITEMS')

        self.modifiers = {"disease":itemData('')}
        self.modifiers["disease"].prepend(pseudoNegations)
        self.modifiers["disease"].prepend(definiteNegations)
        self.modifiers["disease"].prepend(probableNegations)
        self.modifiers["disease"].prepend(probables)
        self.modifiers["disease"].prepend(definites)
        self.modifiers["disease"].prepend(indications)
        self.modifiers["disease"].prepend(conjugates)
        self.modifiers["disease"].prepend(future)
        self.modifiers["disease"].prepend(historicals)
    	"""

        # Quality targets (generated from category parameter set by parser)
        if( options.category.lower() == 'all'):
            targetItems = critItems
        else:
            targetItems = itemData(options.category)
        self.targets = {"disease":targetItems}
        self.models = {}

    def analyzeReport(self, report, mode, modFilters = None ):
        """given an individual radiology report, creates a pyConTextSql
        object that contains the context markup

        report: a text string containing the radiology reports
        mode: which of the pyConText objects are we using: disease
        modFilters: """
        context = self.context.get(mode)
        targets = self.targets.get(mode)
        modifiers = self.modifiers.get(mode)

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
        rslts = {}
        alerts = {}
        cntxt = self.context["disease"]

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
            """
            generates the alerts; we should be able to remove this because we are
            now using the results table to classify documents
            """
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
            #need to change the next two lines so that the fields are not hard-coded
            self.currentCase = r.id
            self.currentText = r.impression.lower()
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
            query = """INSERT INTO pyConTextKit_result (reportid,category, disease, uncertainty, historical, literal, matchedphrase) VALUES (?,?,?,?,?,?,?)"""
            for t in targets:
                rslt=Result(reportid=self.currentCase, category=t.getCategory(),
                                            disease=rslts[t]["disease"],
                                            uncertainty=rslts[t]["uncertainty"],
                                            historical=rslts[t]["temporality"],
                                            literal=t.getLiteral(),
                                            matchedphrase=t.getPhrase())
                rslt.save()

        keys = alerts.keys()
        if( keys ):
            for c in keys:
                alert=Alert(reportid=self.currentCase,category=c,alert=alerts[c],report=self.currentText)
                alert.save()

    def cleanUp(self):
        self.resultsConn.commit()


def modifies(g,n,modifiers):
    pred = g.predecessors(n)
    if( not pred ):
        return False
    pcats = [n.getCategory().lower() for n in pred]
    return bool(set(pcats).intersection([m.lower() for m in modifiers]))

# Add parser options for the label of the lexicon to use in the parsing
def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = OptionParser()
    parser.add_option("-d","--db",dest='dbname',default="pyConTextWeb.db",
                      help='name of db containing reports to parse')
    parser.add_option("-o","--odb",dest='odbname',
                      help='name of db containing results', default="pyConTextWeb.db")
                      #help='name of db containing results', default="testOutput.db")
    #parser.add_option("-s","--save_dir",dest='save_dir',default='critFinderResults',
    parser.add_option("-s","--save_dir",dest='save_dir',default='critFinderResults',
                      help='directory in which to store graphs of markups')
    parser.add_option("-t","--table",dest='table',default='pyConTextKit_report',
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
    parser.add_option("-a","--dataset",dest="dataset",default='ALL',
                      help='report dataset to analyze')
    parser.add_option("-b","--rcat",dest="rcat",default='',
                      help='report category to analyze')
    parser.add_option("-n","--number",dest="number",default=20,
                      help='number of reports to analyze')
    return parser
