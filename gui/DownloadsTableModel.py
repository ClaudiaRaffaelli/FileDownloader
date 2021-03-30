from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from PyQt5.QtWidgets import QProgressBar

import gui.Utils as utils


class DownloadsTableModel(QStandardItemModel):
	# acceptIcon = "gui/icons/success.svg"
	# rejectIcon = "gui/icons/redx.svg"
	# images_change_signal = pyqtSignal(list)

	def __init__(self, parent=None):
		super(DownloadsTableModel, self).__init__(0, 6)
		self.setHeaderData(0, Qt.Horizontal, "Name")
		self.setHeaderData(1, Qt.Horizontal, "Dimension")
		self.setHeaderData(2, Qt.Horizontal, "Status")
		self.setHeaderData(3, Qt.Horizontal, "Speed")
		self.setHeaderData(4, Qt.Horizontal, "Downloaded")
		self.setHeaderData(5, Qt.Horizontal, "Progress")
		# todo reimplement header to add checkbox in order to start/stop/pause downloads at groups
		self.parent = parent

	@pyqtSlot(str, str)
	def add_download_to_table(self, fullpath, url):
		# todo maybe the full url of the item with a custom role to know if this same url is already downloading
		name_item = QStandardItem(fullpath.split('/')[-1])
		# adding the full path to the item in order to call the "reveal in finder" later on
		name_item.setData(fullpath, Qt.UserRole + CustomRole.full_path)
		name_item.setData(Qt.Checked, Qt.CheckStateRole)

		#dim_item = QStandardItem(utils.size_converter(dimension))
		dim_item = QStandardItem("N/A")
		status_item = QStandardItem("Starting ...")
		speed_item = QStandardItem("0")
		downloaded_item = QStandardItem("0")
		progress_item = QStandardItem()
		self.appendRow([name_item, dim_item, status_item, speed_item, downloaded_item, progress_item])

	@pyqtSlot(int, int)
	def init_row(self, row, dimension):
		# initialize the row of download with the size of the download
		print(dimension)
		self.setData(self.index(row, 1), utils.size_converter(dimension))
		self.setData(self.index(row, 2), "Downloading ...")

	@pyqtSlot(int, int, str)
	def update_data_to_table(self, row, downloaded_size, speed):
		# updating data of a download at specific table index
		self.setData(self.index(row, 4), utils.size_converter(downloaded_size))
		self.setData(self.index(row, 3), speed)

	@pyqtSlot(int)
	def completed_row(self, row):
		# setting the status of the download row as completed
		self.setData(self.index(row, 2), "Completed")
		self.setData(self.index(row, 3), "-")

	# todo maybe paused_row and completed_row can be merged taking as input the status
	@pyqtSlot(int)
	def paused_row(self, row):
		# setting the status of the download row as completed
		self.setData(self.index(row, 2), "Paused")
		self.setData(self.index(row, 3), "-")

	def select_all(self):
		for row in range(0, self.rowCount()):
			print(self.item(row, 1))

	def toggle_checkbox(self, index):
		# returns True if now the row is checked or False if it is unchecked
		if index.data(Qt.CheckStateRole) == Qt.Checked:
			self.setData(index, Qt.Unchecked, Qt.CheckStateRole)
			return False
		else:
			self.setData(index, Qt.Checked, Qt.CheckStateRole)
			return True

	def get_all_checked_rows(self):
		checked_rows = []
		for row in range(0, self.rowCount()):
			if self.index(row, 0).data(Qt.CheckStateRole) == Qt.Checked:
				checked_rows.append(row)
		return checked_rows


class CustomRole:
	full_path = 0
	url = 1
