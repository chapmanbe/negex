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
	def __init__(self,file, label, type):
		#For debugging: When set to false, does not modify Database
		self.execute = True 					#Default = True
		#Include id into INSERT statement? For linking items on id
		self.idINCL = False 					#Default = False
		self.label = label
		self.issues = []
		if type == "report":
			self.type = "pyConTextKit_report"
		elif type == "lexicon":
			self.type = "pyConTextKit_lexical"
		try:
			fileBIN = open(file,'rU')
		except IOError:
			print "File does not exist!"
		else:
			self.csvReader = sorted(csv.DictReader(open(file,'rU'), dialect='excel'))
		self.rowsmodified = 0

	"""
		Create SQL statements for inserting the information
		@param row type:list Row that contains the data that needs to be inserted
		Possible issues:
			I took out id from the SQL statments becuase it's PRIMARY AI and might interfere
	"""
	def createSQLStmt(self,row):
		sqlconfigs = { #removed ids
			'pyConTextKit_lexical': ['category','literal','re','rule','creator_id'],
			'pyConTextKit_report' : ['reportid','report'],
			'pyConTextKit_alert'  : ['reportid','category','alert','report'],
			'pyConTextKit_result' : ['reportid','category','disease','uncertainty','historical','literal','matchedphrase']
		}

		if self.idINCL: #add id to each array
			sqlconfigs = { #removed ids
			'pyConTextKit_lexical': ['id','category','literal','re','rule','creator_id'],
			'pyConTextKit_report' : ['id','reportid','report'],
			'pyConTextKit_alert'  : ['id','reportid','category','alert','report'],
			'pyConTextKit_result' : ['id','reportid','category','disease','uncertainty','historical','literal','matchedphrase']
		}
		if self.type is None:
			raise Exception("Type is not defined")
		tablename = self.type

		sqlStmt = "INSERT INTO "+tablename+" ("

		sortedList = sorted(sqlconfigs[tablename])
		sqlconfig_mini = sortedList.pop()
		for i in sortedList:
			sqlStmt += i+", "
		sqlStmt += sqlconfig_mini

		if self.type == "pyConTextKit_lexical":
			sqlStmt += ", label) VALUES ("
		elif self.type == "pyConTextKit_report":
			sqlStmt += ", dataset) VALUES ("
		else:
			sqlStmt += ") VALUES ("

		row_mini = row.pop()
		for i in row:
			sqlStmt += "'"+i+"', "
		sqlStmt += "'"+row_mini+"'"

		sqlStmt += ", '"+self.label+"');"
		return sqlStmt

	"""
		Reads a csv file row by row and calls createSQLStmt method executing SQL to modify database.
		@pre csvParser must be instantiated before iterateRows can be called
	"""
	def iterateRows(self):
		if self.execute:
			user_home = os.path.expanduser('~')
			pyConTextWebHome = os.path.join(user_home,'pyConTextWeb')
			connection = sqlite3.connect(os.path.join(pyConTextWebHome,'pyConTextWeb.sqlite'))
			c = connection.cursor()
		continueLoop = True
		for pos, row in enumerate(self.csvReader):
			self.rowsmodified += 1
			if continueLoop:
				keysSorted = sorted(row.keys())
				if 0 == pos: # just need the values of the rows
					if len(self.checkKeys(keysSorted)) > 0:
						continueLoop = False
				if continueLoop:
					valuesSorted = []
					for i in keysSorted:
						valuesSorted.append(row[i])

					""" Instead of printing execute it across the sql database """
					if self.execute:
						c.execute(self.createSQLStmt(valuesSorted))
					else:
						print self.createSQLStmt(valuesSorted)
		if self.execute:
			connection.commit()
			c.close()

	def addIssue(self, issue):
		self.issues.append(issue)

	def returnIssues(self):
		return self.issues;

	def checkKeys(self, keys):
		sqlconfigs = { #removed ids
			'pyConTextKit_lexical': ['category','literal','re','rule','creator_id'],
			'pyConTextKit_report' : ['reportid','report'],
			'pyConTextKit_alert'  : ['reportid','category','alert','report'],
			'pyConTextKit_result' : ['reportid','category','disease','uncertainty','historical','literal','matchedphrase']
		}
		checkArray = sqlconfigs[self.type]
		for i in keys:
			if i in checkArray:
				checkArray.remove(i)

		if len(checkArray) > 0:
			issue = ""
			for i in checkArray:
				issue += "<b>"+i+"</b>, "
			if len(checkArray) > 1:
				issue += " are missing from the CSV file"
			else:
				issue += " is missing from the CSV file"

			self.addIssue(issue)

		return checkArray
