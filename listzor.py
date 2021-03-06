#!/usr/bin/env python

#author: Oz Elentok
#email: oz.elen@gmail.com
#status: development

import pygtk
pygtk.require('2.0')
import gtk
import ast
from parser import FileParser

class MainForm:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title('Listzor')
		self.window.connect('delete_event', lambda w, e: gtk.main_quit())
		self.window.set_default_size(500, 300)

		self.currentFile = None

		self.treeview = gtk.TreeView()
		self.treeview.set_property("enable-grid-lines", True)
		self.treeview.set_property("rules-hint", True)
		self.treeSelector = self.treeview.get_selection()
		self.treeSelector.connect('changed', self.rowChange)

		self.scrollwindow = gtk.ScrolledWindow(
			self.treeview.get_vadjustment(),
			self.treeview.get_hadjustment())
		self.scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrollwindow.add(self.treeview)

		# uses self.notesBuffers
		self.emptyBuffer = gtk.TextBuffer()
		self.notesView = gtk.TextView()
		self.notesView.set_editable(True)
		self.notesView.set_wrap_mode(gtk.WRAP_WORD)

		self.topVBox = gtk.VBox(False, 0)

		self.tableVBox = gtk.VBox(True, 0)
		self.tableVBox.pack_start(self.scrollwindow, True, True, 0)

		self.noteVBox = gtk.VBox(False, 0)
		self.noteVBox.pack_start(gtk.HSeparator(), False, False, 0)

		notesLabel = gtk.Label("Notes")
		notesLabel.set_alignment(0, 0)
		self.noteVBox.pack_start(notesLabel, False, False, 0)
		self.noteVBox.pack_start(self.notesView, True, True, 0)
		
		self.tableVBox.pack_start(self.noteVBox, True, True, 0)

		self.topVBox.pack_start(self.createMenu(), False, False, 0)
		self.topVBox.pack_start(self.tableVBox, True, True, 0)

		self.window.add(self.topVBox)
		self.window.show_all()
		self.newFile()

	def createMenu(self): 
		menubar = gtk.MenuBar()
 	   
		menu_file = gtk.Menu()
		menu_edit = gtk.Menu()
		menu_help = gtk.Menu()
		
		item_new = gtk.MenuItem('New')
		item_new.connect('button-press-event', self.newFile)
		item_open = gtk.MenuItem('Open')
		item_open.connect('button-press-event', self.openFile)
		item_save = gtk.MenuItem('Save')
		item_save.connect('button-press-event', self.saveFile)
		item_quit = gtk.MenuItem('Quit')
		item_quit.connect('button-press-event', lambda w, e: gtk.main_quit())
		menu_file.append(item_new)
		menu_file.append(item_open)
		menu_file.append(item_save)
		menu_file.append(item_quit)

		item_addItem = gtk.MenuItem('Add Item')
		item_addItem.connect('button-press-event', self.addRow, menu_edit)
		item_addColumn = gtk.MenuItem('Add Column')
		item_delItem = gtk.MenuItem('Delete Selected Item')
		item_delItem.connect('button-press-event', self.delRow, menu_edit)
		item_delColumn = gtk.MenuItem('Delete Column')
		menu_edit.append(item_addItem)
		menu_edit.append(item_addColumn)
		menu_edit.append(item_delItem)
		menu_edit.append(item_delColumn)
		
		item_about = gtk.MenuItem('About')
		menu_help.append(item_about)

		item_file = gtk.MenuItem('File')
		item_edit = gtk.MenuItem('Edit')
		item_help = gtk.MenuItem('Help')
		
		item_file.set_submenu(menu_file)
		item_edit.set_submenu(menu_edit)
		item_help.set_submenu(menu_help)
		
		menubar.append(item_file)
		menubar.append(item_edit)
		menubar.append(item_help)

		return menubar

	def newFile(self, widget=None, e=None):
		liststore = gtk.ListStore(str)
		self.loadData(liststore, [str], ['Name'], [])


	def openFile(self, widget, e):
		fileChooser = gtk.FileChooserDialog('Open a File', self.window,
				gtk.FILE_CHOOSER_ACTION_OPEN,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				gtk.STOCK_OPEN, gtk.RESPONSE_OK), None)
		fileFilter = gtk.FileFilter()
		fileFilter.set_name('Text Files')
		fileFilter.add_pattern('*.txt')
		fileFilter.add_pattern('*.csv')
		fileChooser.add_filter(fileFilter)
		response = fileChooser.run()
		if response != gtk.RESPONSE_OK:
			fileChooser.destroy()
			return
		fileName = fileChooser.get_filename()
		fileChooser.destroy()
		fileParser = FileParser()
		newListStore, headersType, tableHeaders, rowsNotes = fileParser.parseToTable(fileName)
		if newListStore == None:
			self.displayErrorPrompt('ERROR! Corrupted File', 'The file: \'' + fileName +
				'could not be loaded\nFile\'s data is malformed')
			return
		self.currentFile = fileName
		self.loadData(newListStore, headersType,
					tableHeaders, rowsNotes)

	def saveFile(self, widget, e):
		fileChooser = gtk.FileChooserDialog('Save File', self.window,
				gtk.FILE_CHOOSER_ACTION_SAVE,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				gtk.STOCK_SAVE, gtk.RESPONSE_OK), None)
		fileFilter = gtk.FileFilter()
		fileFilter.set_name('Text Files')
		fileFilter.add_pattern('*.txt')
		fileFilter.add_pattern('*.csv')
		fileChooser.add_filter(fileFilter)
		response = fileChooser.run()
		if response != gtk.RESPONSE_OK:
			fileChooser.destroy()
			return
		fileName = fileChooser.get_filename()
		fileChooser.destroy()
		fileParser = FileParser()
		rowNotes = []
		for nbuffer in self.notesBuffers:
			startIter = nbuffer.get_start_iter()
			endIter = nbuffer.get_end_iter()
			rowNotes.append(nbuffer.get_text(startIter, endIter))
		fileParser.parseToFile(fileName, self.liststore, self.tableHeaders, rowNotes)


	def loadData(self, liststore, headersType, headers, rowsNotes):
		# remove old treeview columns
		for col in self.treeview.get_columns():
			self.treeview.remove_column(col)
		# add new treeview columns
		for i, header in enumerate(headers):
			# cell
			if headersType[i] == int:
				cell = gtk.CellRendererText()
				cell.connect('edited', self.intCellEdited,
						liststore, i)
			elif headersType[i] == float:
				cell = gtk.CellRendererText()
				cell.connect('edited', self.floatCellEdited,
						liststore, i)
			elif headersType[i] == bool:
				cell = gtk.CellRendererToggle()
				cell.connect('toggled', self.boolCellEdited,
						liststore, i)
			else:
				cell = gtk.CellRendererText()
				cell.connect('edited', self.textCellEdited,
						liststore, i)

			if headersType[i] == bool:
				col = gtk.TreeViewColumn(header, cell, active = i)
				cell.set_property('activatable', True)

			else:
				col = gtk.TreeViewColumn(header, cell, text = i)
				cell.set_property('editable', True)
				col.set_resizable(True)
			
			# column
			self.treeview.append_column(col)
		# notes buffers
		self.tableHeaders = headers;
		self.notesBuffers = []
		for notes in rowsNotes:
			nbuffer = gtk.TextBuffer()
			nbuffer.set_text(notes)
			self.notesBuffers.append(nbuffer)
		self.liststore = liststore;
		self.treeview.set_model(self.liststore)

	def displayErrorPrompt(self, title, message):
		errorPrompt = gtk.MessageDialog(self.window,
				gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
				message)
		errorPrompt.set_title(title)
		errorPrompt.run();
		errorPrompt.destroy();

	def addRow(self, widget, e, menu):
		menu.popdown()
		self.liststore.append(None)
		self.notesBuffers.append(gtk.TextBuffer())

	def delRow(self, widget,e, menu):
		menu.popdown()
		itemToDel = self.treeSelector.get_selected()[1]
		if itemToDel != None:
			index = self.liststore.get_path(itemToDel)[0]
			self.liststore.remove(itemToDel)
			del self.notesBuffers[index]
	def intCellEdited(self, widget, path, text, model, column):
		model[path][column] = int(text)

	def floatCellEdited(self, widget, path, text, model, column):
		model[path][column] = float(text)

	def boolCellEdited(self, widget, path, model, column):
		model[path][column] = not model[path][column]

	def textCellEdited(self, widget, path, text, model, column):
		model[path][column] = text

	def rowChange(self, widget):
		itemIter = widget.get_selected()[1]
		if itemIter != None:
			index = self.liststore.get_path(itemIter)[0]
			self.notesView.set_buffer(self.notesBuffers[index])		
			self.notesView.set_property('editable', True)
		else:
			self.notesView.set_buffer(self.emptyBuffer)
			self.notesView.set_property('editable', False)

	def main(self):
		gtk.main()

if __name__ == '__main__':
	mainForm = MainForm()
	mainForm.main()

