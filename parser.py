#!/usr/bin/env python

#author: Oz Elentok
#email: oz.elen@gmail.com
#status: development

import pygtk
pygtk.require('2.0')
import gtk
import csv
import gobject
import sys

class FileParser(object):

	def __init__(self):
		self.letterTypes = {'f':  float, 'i': int,
				's': str, 'b': bool}
		self.gobjectTypes = {gobject.TYPE_FLOAT: 'f', gobject.TYPE_INT: 'i'
		 		,gobject.TYPE_STRING: 's', gobject.TYPE_BOOLEAN: 'b'}

	def convertValToTableFormat(self, cellType, val):
		if cellType == 'd':
			return float(val)
		elif cellType == 'i':
			return int(val)
		elif cellType == 'b':
			if val == 'True':
				return True
			else:
				return False
		else:
			return val
	def convertTypeToFileFormat(self, colType):
		return self.gobjectTypes[colType]

	# parses file into table
	# returns gtk.listStore containing the table, and returns the table headers
	def parseToTable(self, filePath):
		with open(filePath, 'r') as dataFile:
			try:
				dataRows = csv.reader(dataFile)
				dataLetters = dataRows.next()
				dataTypes = [self.letterTypes[t] for t in dataLetters]
				liststore = gtk.ListStore(*dataTypes)
				tableHeaders = dataRows.next()
				rowsNotes = []
				for row in dataRows:
					# row is empty
					if not row:
						continue
					data = []
					for i, cellType in enumerate(dataLetters):
						val = self.convertValToTableFormat(cellType, row[i])
						data.append(val)
					liststore.append(data)
					rowsNotes.append(row[-1])
				return liststore, dataTypes, tableHeaders, rowsNotes

			except:
				print >> sys.stderr, 'File Data is malformed'
		return None, None, None

	# parses data into csv file
	def parseToFile(self, filePath, liststore, tableHeaders, rowsNotes):
		with open(filePath, 'w',) as dataFile:
			csvWriter = csv.writer(dataFile)
			dataTypes = []
			for i in range(liststore.get_n_columns()):
				col = liststore.get_column_type(i)
				colLetter = self.convertTypeToFileFormat(col)
				dataTypes.append(colLetter)
			csvWriter.writerow(dataTypes)
			csvWriter.writerow(tableHeaders)

			for i, row in enumerate(liststore):
				ouputRow = [item for item in row]
				ouputRow.append(rowsNotes[i])
				csvWriter.writerow(ouputRow)