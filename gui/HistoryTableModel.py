from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QModelIndex

from PyQt5.QtWidgets import QProgressBar

import gui.Utils as utils
from gui.Utils import CustomRole
from gui.Worker import DownloadStatus


class HistoryTableModel(QStandardItemModel):

	def __init__(self, parent=None):
		super(HistoryTableModel, self).__init__(0, 5)
		self.setHeaderData(0, Qt.Horizontal, "Name")
		self.setHeaderData(1, Qt.Horizontal, "Dimension")
		self.setHeaderData(2, Qt.Horizontal, "Status")  # Completed, Aborted, Moved
		self.setHeaderData(3, Qt.Horizontal, "Time started")
		self.setHeaderData(4, Qt.Horizontal, "Time completed")
		self.parent = parent

		# todo far partire la view già con time started come filtro di ordinamento (prima i più recenti)