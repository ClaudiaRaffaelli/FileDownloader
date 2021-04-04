import platform
import os
import subprocess

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QFileInfo, QModelIndex, QRegExp
from PyQt5.QtWidgets import QFileDialog, QMenu, QAction, QWidget, QTableView, QHeaderView, QTableWidget
from PyQt5.QtGui import QRegExpValidator
from gui.Worker import Worker
from gui.HistoryTableModel import HistoryTableModel
from gui.ProgressBarDelegate import ProgressBarDelegate
from gui.Utils import CustomRole
from gui.Worker import DownloadStatus
from gui.EraseHistoryDialog import EraseHistoryDialog


class HistoryPage(QWidget):

	def __init__(self, parent=None):
		super(HistoryPage, self).__init__(parent)
		uic.loadUi("gui/ui/historyWidget.ui", self)

		# creating the table view for the chronology and the model that holds the data
		self.historyTableModel = HistoryTableModel()
		self.historyTableView = QTableView()
		self.historyTableView.setSortingEnabled(True)
		self.historyTableView.setSelectionBehavior(QTableView.SelectRows)

		# Init table view
		self.historyTableView.setModel(self.historyTableModel)

		self.historyTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
		self.historyTableView.horizontalHeader().setStretchLastSection(True)
		# the fields in the table are non editable
		self.historyTableView.setEditTriggers(QTableWidget.NoEditTriggers)

		self.mainLayout.addWidget(self.historyTableView)

	@pyqtSlot()
	def empty_history(self):
		# todo disattiva e attiva pulsante a seconda che ci sia qualcosa da cancellare o meno
		# deleting the whole model after that the user has pressed the button of delete history and confirmed
		# asking the user
		cancel_dialog = EraseHistoryDialog(None)
		result = cancel_dialog.exec()

		if result:
			# emptying the model
			self.historyTableModel.delete_all()
			# deleting from the file
			try:
				os.remove("./UserHistory.json")
			except:
				print("No history to delete")