import os
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem, QColor
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QModelIndex


import gui.Utils as utils
from gui.Utils import CustomRole


class HistoryTableModel(QStandardItemModel):

	def __init__(self, parent=None):
		super(HistoryTableModel, self).__init__(0, 5)
		self.setHeaderData(0, Qt.Horizontal, "Name")
		self.setHeaderData(1, Qt.Horizontal, "Dimension")
		self.setHeaderData(2, Qt.Horizontal, "Status")  # Completed, Aborted, Moved
		self.setHeaderData(3, Qt.Horizontal, "Time started")
		self.setHeaderData(4, Qt.Horizontal, "Time completed")
		self.parent = parent

		#todo connetti le azioni per aprire nel finder

	def insert_row(self, name, full_path, dimension, status, time_started, time_completed):
		# loading rows from the json file

		name_item = QStandardItem(name)
		# adding the full path to the item in order to call the "reveal in finder" later on
		name_item.setData(full_path, Qt.UserRole + CustomRole.full_path)
		name_item.setData(time_started, Qt.UserRole + CustomRole.start_time)

		dim_item = QStandardItem(utils.size_converter(dimension))
		time_started_item = QStandardItem(time_started)
		time_completed_item = QStandardItem(time_completed)

		# if the path to the file doesn't exists anymore we set the status as Moved and color it red
		if not os.path.exists(full_path):
			status_item = QStandardItem("Moved")
			status_item.setData(QColor(Qt.red), Qt.ForegroundRole)
		else:
			status_item = QStandardItem(status)

		self.appendRow([name_item, dim_item, status_item, time_started_item, time_completed_item])

	def delete_all(self):
		# deletes from the model all the data except headers
		self.setRowCount(0)
