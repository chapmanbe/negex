import unicodecsv as csv
import array
import hashlib
import sqlite3
import os
class reportParser(object):
    """
        Initializes the csvParser object with a csv file
        @param file String containing the path to the file
    """
    def __init__(self,fname, label):
        self.label = label
        self.issues = []
        if type == "report":
            self.type = "pyConTextKit_report"
            self.type = "pyConTextKit_items"
        self.reader = open(fname,'rbU')
        self.rowsmodified = 0

    """
        Reads a csv file row by row and calls createSQLStmt method executing SQL to modify database.
    """
    def uploadReports(self, beginMark, endMark):
        user_home = os.path.expanduser('~')
        CherryConTextHome = os.path.join(user_home,'CherryConText','pyConTextKit')
        dbname = os.path.join(CherryConTextHome,'CherryConText.sqlite')
        connection = sqlite3.connect(dbname)
        c = connection.cursor()
        beginMark = "@begin_report"
        endMark = "@end_report"
        
        lines = self.reader.readlines()
        report = []
        while( lines ):
            l = lines.pop(0)
            if beginMark in l:
                report = []
                l = lines.pop(0)
                reportid  = l.strip()
            elif endMark in l:
                reportTxt = " ".join(report)
                c.execute("""INSERT into pyConTextKit_report('dataset','reportid','report') VALUES (?,?,?)""",
                        (self.label,reportid,reportTxt,))
            else:
                report.append(l)

        connection.commit()
        c.close()


    def addIssue(self, issue):
        self.issues.append(issue)

    def returnIssues(self):
        return self.issues;

class lexicalParser(object):
    """
        Initializes the csvParser object with a csv file
        @param file String containing the path to the file
    """
    def __init__(self,lfile, label, lex_type=None):
        self.label = label
        self.issues = []
        self.lex_type = lex_type
        self.csvReader = sorted(csv.DictReader(open(lfile,'rbU'), dialect='excel', delimiter="\t"))
        self.rowsmodified = 0

    """
        Reads a csv file row by row and calls createSQLStmt method executing SQL to modify database.
    """
    def uploadData(self):
        user_home = os.path.expanduser('~')
        CherryConTextHome = os.path.join(user_home,'CherryConText','pyConTextKit')
        dbname = os.path.join(CherryConTextHome,'CherryConText.sqlite')
        connection = sqlite3.connect(dbname)
        c = connection.cursor()
        lt = self.lex_type

        for pos, row in enumerate(self.csvReader):
            print self.label,row
            c.execute("""INSERT into pyConTextKit_items('label','category','literal','re','rule','creator_id','lex_type','show') VALUES (?,?,?,?,?,?,?,?)""",
                    (self.label,row['Lex'],row['Type'],row['Regex'],row['Direction'],1,self.lex_type,'true'))
        connection.commit()
        c.close()

    def addIssue(self, issue):
        self.issues.append(issue)

    def returnIssues(self):
        return self.issues;


