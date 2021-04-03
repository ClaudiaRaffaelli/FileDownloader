from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QModelIndex

from PyQt5.QtWidgets import QProgressBar

import gui.Utils as utils
from gui.Utils import CustomRole
from gui.Worker import DownloadStatus


class DownloadsTableModel(QStandardItemModel):

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

		dim_item = QStandardItem("Unknown")
		# here we will be holding the non-decorated dimension in bytes, it will be useful when updating the progress bar
		dim_item.setData(None, Qt.UserRole + CustomRole.plain_dimension)
		status_item = QStandardItem("Starting...")
		speed_item = QStandardItem("0 B/s")
		downloaded_item = QStandardItem("0 B")
		progress_item = QStandardItem()
		progress_item.setData(0, Qt.UserRole + CustomRole.progress_bar)
		self.appendRow([name_item, dim_item, status_item, speed_item, downloaded_item, progress_item])

	@pyqtSlot(int, int)
	def init_row(self, row, dimension):
		# initialize the row of download with the size of the download
		self.setData(self.index(row, 1), utils.size_converter(dimension))
		self.setData(self.index(row, 1), dimension, Qt.UserRole + CustomRole.plain_dimension)
		self.setData(self.index(row, 2), "Downloading...")

	@pyqtSlot(int, int, str)
	def update_data_to_table(self, row, downloaded_size, speed):
		# updating data of a download at specific table index
		self.setData(self.index(row, 4), utils.size_converter(downloaded_size))
		self.setData(self.index(row, 3), speed)

		# if the complete size of the download is known we also update the progress bar
		# to do so we check the plain dimension in bytes
		plain_dimension = self.data(self.index(row, 1), Qt.UserRole + CustomRole.plain_dimension)
		if plain_dimension is not None:
			self.setData(self.index(row, 5), downloaded_size * 100 / int(plain_dimension),
				Qt.UserRole + CustomRole.progress_bar)

	@pyqtSlot(int, int)
	def completed_row(self, row, download_size):
		# setting the status of the download row as completed
		self.setData(self.index(row, 2), "Completed")
		self.setData(self.index(row, 3), "-")
		self.setData(self.index(row, 1), utils.size_converter(download_size))
		# setting the progress bar to completed when the download is finished ensures that even the progress bar for
		# downloads that do not have a known length at first displays a full bar at the end
		self.setData(self.index(row, 5), 100, Qt.UserRole + CustomRole.progress_bar)

	@pyqtSlot(int, DownloadStatus)
	def interrupted_row(self, row, status):
		print(status)
		if status == DownloadStatus.pause:
			# setting the status of the download row as paused
			self.setData(self.index(row, 2), "Paused")
			self.setData(self.index(row, 3), "-")
		elif status == DownloadStatus.abort:

			# setting the new status
			self.setData(self.index(row, 2), "Aborted")
			# setting to zero the amount of downloaded data
			self.setData(self.index(row, 4), utils.size_converter(0))
			# re-setting the progress bar
			self.setData(self.index(row, 5), 0, Qt.UserRole + CustomRole.progress_bar)
			# re-set the speed
			self.setData(self.index(row, 3), "-")

	@pyqtSlot(int)
	def restarted_row(self, row):
		# setting the status of the download row as started again
		self.setData(self.index(row, 2), "Downloading...")

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

	def get_full_path(self, row):
		return self.index(row, 0).data(Qt.UserRole + CustomRole.full_path)



