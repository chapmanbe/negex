import unicodecsv as csv
import array
import hashlib
import sqlite3
import os

class csvParser:
    """
        Initializes the csvParser object with a csv file
        @param file String containing the path to the file
    """
    def __init__(self,file, label, type, lex_type=None):
        #For debugging: When set to false, does not modify Database
        self.execute = True 					#Default = True
        #Include id into INSERT statement? For linking items on id
        self.idINCL = False 					#Default = False
        self.label = label
        self.issues = []
        self.lex_type = lex_type
        if type == "report":
            self.type = "pyConTextKit_report"
        elif type == "lexicon":
            self.type = "pyConTextKit_items"
        try:
            fileBIN = open(file,'rb')
        except IOError:
            print "File does not exist!"
        else:
            self.csvReader = sorted(csv.DictReader(open(file,'rbU'), dialect='excel'))
        self.rowsmodified = 0

    """
        Reads a csv file row by row and calls createSQLStmt method executing SQL to modify database.
        @pre csvParser must be instantiated before iterateRows can be called
    """
    def iterateRows(self):
        user_home = os.path.expanduser('~')
        CherryConTextHome = os.path.join(user_home,'CherryConText','pyConTextKit')
        dbname = os.path.join(CherryConTextHome,'CherryConText.sqlite')
        print "\n\n\ndatabase name is %s\n\n\n"%dbname
        connection = sqlite3.connect(dbname)
        c = connection.cursor()
        continueLoop = True
        if self.type == "pyConTextKit_items":
            table = "pyConTextKit_items"

        elif self.type == "pyConTextKit_report":
            table = 'pyConTextKit_report'

        c.execute("""select id from %s order by rowid desc limit 1"""%table)
        try:
            id = c.fetchone()[0]+1
        except:
            id = 0
        for pos, row in enumerate(self.csvReader):
            if( self.type == "pyConTextKit_items" ):
                c.execute("""INSERT into pyConTextKit_items('label','category','literal','re','rule','creator_id','lex_type','show') VALUES (?,?,?,?,?,?,?,?)""",
                    (self.label,row['Lex'],row['Type'],row['Regex'],row['Direction'],1,self.lex_type,'true'))
            elif( self.type == "pyConTextKit_report" ):
                c.execute("""INSERT into pyConTextKit_report('dataset','reportid','report') VALUES (?,?,?)""",(self.label,row['reportid'],row['report']))
            id += 1
        connection.commit()
        c.close()

    def addIssue(self, issue):
        self.issues.append(issue)

    def returnIssues(self):
        return self.issues;


