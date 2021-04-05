import platform
import os
import subprocess

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QFileInfo
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QTableView, QHeaderView, QTableWidget
from gui.HistoryTableModel import HistoryTableModel
from gui.Utils import CustomRole
from gui.EraseHistoryDialog import EraseHistoryDialog


class HistoryPage(QWidget):

	def __init__(self, parent=None):
		super(HistoryPage, self).__init__(parent)
		uic.loadUi("gui/ui/historyWidget.ui", self)

		# creating the table view for the history and the model that holds the data
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

		# connecting the signal for the context menu on right click on history table row
		self.historyTableView.setContextMenuPolicy(Qt.CustomContextMenu)
		self.historyTableView.customContextMenuRequested.connect(self.context_menu_triggered_history_table)

	@pyqtSlot()
	def empty_history(self):
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
			self.deleteHistoryButton.setEnabled(False)

	@pyqtSlot(QPoint)
	def context_menu_triggered_history_table(self, clickpoint):
		index = self.historyTableView.indexAt(clickpoint)
		if index.isValid():
			context = QMenu(self)
			finder = "Show in Explorer"
			if platform.system() == "Linux":
				finder = "Reveal in File Explorer"
			elif platform.system() == "Darwin":
				finder = "Reveal in Finder"
			openExplorer = QAction(finder, self)

			# getting the path from this row
			currentItem = self.historyTableModel.itemFromIndex(self.historyTableModel.index(index.row(), 0))

			# if this download has been moved the reveal in finder must be not possible
			path = currentItem.data(Qt.UserRole + CustomRole.full_path)
			if not os.path.exists(path):
				openExplorer.setEnabled(False)
				# if the file does not exist anymore we set the status as Moved passing the index at clickpoint
				self.historyTableModel.set_data_moved(index)

			context.addActions([openExplorer])
			openExplorer.triggered.connect(self.open_explorer_item)
			context.exec(self.historyTableView.mapToGlobal(clickpoint))

	@pyqtSlot()
	def open_explorer_item(self):
		index = self.historyTableView.selectionModel().currentIndex()
		currentItem = self.historyTableModel.itemFromIndex(self.historyTableModel.index(index.row(), 0))
		info = QFileInfo(currentItem.data(Qt.UserRole + CustomRole.full_path))
		# revealing in Finder / Explorer / Nautilus the selected file
		if info.isDir():
			filepath = info.canonicalFilePath()
		else:
			filepath = info.canonicalPath()
		try:
			os.startfile(filepath)
		except:
			try:
				subprocess.call(["open", "-R", filepath])
			except:
				subprocess.Popen(["xdg-open", filepath])

