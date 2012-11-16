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

		self.treeview = gtk.TreeView()
		self.treeSelector = self.treeview.get_selection()
		self.treeSelector.connect('changed', self.rowChange)

		self.scrollwindow = gtk.ScrolledWindow(
			self.treeview.get_vadjustment(),
			self.treeview.get_hadjustment())
		self.scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrollwindow.add(self.treeview)

		# uses self.notesBuffers
		self.notesView = gtk.TextView()
		self.notesView.set_editable(True)
		self.notesView.set_wrap_mode(gtk.WRAP_WORD)

		self.topVBox = gtk.VBox(False, 0)

		self.tableVBox = gtk.VBox(True, 0)
		self.tableVBox.pack_start(self.scrollwindow, True, True, 0)

		self.noteVBox = gtk.VBox(False, 0)
		self.noteVBox.pack_start(gtk.HSeparator(), False, False, 0)
		self.noteVBox.pack_start(self.notesView, True, True, 0)
		
		self.tableVBox.pack_start(self.noteVBox, True, True, 0)

		self.topVBox.pack_start(self.createMenu(), False, False, 0)
		self.topVBox.pack_start(self.tableVBox, True, True, 0)

		self.window.add(self.topVBox)
		self.window.show_all()


	def createMenu(self): 
		menubar = gtk.MenuBar()
 	   
		menu_file = gtk.Menu()
		menu_edit = gtk.Menu()
		menu_help = gtk.Menu()
		
		item_open = gtk.MenuItem('Open')
		item_open.connect('button-press-event', self.openFile)
		item_save = gtk.MenuItem('Save')
		item_save.connect('button-press-event', self.saveFile)
		item_quit = gtk.MenuItem('Quit')
		item_quit.connect('button-press-event', lambda w, e: gtk.main_quit())
		menu_file.append(item_open)
		menu_file.append(item_save)
		menu_file.append(item_quit)

		item_cut = gtk.MenuItem('Cut')
		item_copy = gtk.MenuItem('Copy')
		item_paste = gtk.MenuItem('Paste')
		menu_edit.append(item_cut)
		menu_edit.append(item_copy)
		menu_edit.append(item_paste)
		
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
		# TODO: add messege box for unsucessful file load
		if newListStore == None or tableHeaders == None:
			return
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
			col.set_sort_column_id(i)
			self.treeview.append_column(col)
			self.tableHeaders = headers;
			# notes buffers
			self.notesBuffers = []
			for notes in rowsNotes:
				nbuffer = gtk.TextBuffer()
				nbuffer.set_text(notes)
				self.notesBuffers.append(nbuffer)
			self.liststore = liststore;
		self.treeview.set_model(self.liststore)

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

	def main(self):
		gtk.main()

if __name__ == '__main__':
	mainForm = MainForm()
	mainForm.main()

