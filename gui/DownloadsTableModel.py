import datetime
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
		self.parent = parent

	@pyqtSlot(str, str)
	def add_download_to_table(self, fullpath, url):
		name_item = QStandardItem(fullpath.split('/')[-1])
		# adding the full path to the item in order to call the "reveal in finder" later on
		name_item.setData(fullpath, Qt.UserRole + CustomRole.full_path)
		name_item.setData(Qt.Checked, Qt.CheckStateRole)
		time = datetime.datetime.now()
		name_item.setData(
			"{}-{}-{} {}:{}:{}".format(time.day, time.month, time.year, time.hour, time.minute, time.second),
			Qt.UserRole + CustomRole.start_time)
		name_item.setData(url, Qt.UserRole + CustomRole.url)

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
		self.setData(self.index(row, 4), downloaded_size, Qt.UserRole + CustomRole.plain_downloaded_size)
		self.setData(self.index(row, 3), speed)

		# if the complete size of the download is known we also update the progress bar
		# to do so we check the plain dimension in bytes
		plain_dimension = self.data(self.index(row, 1), Qt.UserRole + CustomRole.plain_dimension)
		if plain_dimension is not None:
			# for some files if paused and started again the header content dimension can change, and we want to avoid
			# that at some point the progress bar starts over again
			if downloaded_size > plain_dimension:
				self.setData(self.index(row, 5), 100, Qt.UserRole + CustomRole.progress_bar)
			else:
				self.setData(self.index(row, 5), downloaded_size * 100 / int(plain_dimension),
					Qt.UserRole + CustomRole.progress_bar)

	@pyqtSlot(int, int)
	def completed_row(self, row, download_size):
		# setting the status of the download row as completed
		self.setData(self.index(row, 2), "Completed")
		self.setData(self.index(row, 3), "-")
		self.setData(self.index(row, 1), utils.size_converter(download_size))
		# also updating the plain dimension (maybe first was unknown)
		self.setData(self.index(row, 1), download_size, Qt.UserRole + CustomRole.plain_dimension)
		# setting the progress bar to completed when the download is finished ensures that even the progress bar for
		# downloads that do not have a known length at first displays a full bar at the end
		self.setData(self.index(row, 5), 100, Qt.UserRole + CustomRole.progress_bar)
		# setting also the end time of download
		time = datetime.datetime.now()
		self.setData(
			self.index(row, 0),
			"{}-{}-{} {}:{}:{}".format(time.day, time.month, time.year, time.hour, time.minute, time.second),
			Qt.UserRole + CustomRole.end_time)

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

	def save_model(self, start_i, num_old_data):
		# i indicates the first key. If the json is new or there are no downloads i is 0, otherwise is a number >0
		data_in_model = {}
		for row in range(num_old_data, self.rowCount()):
			data = {
				"name": self.index(row, 0).data(),
				"path": self.index(row, 0).data(Qt.UserRole + CustomRole.full_path),
				"dimension": self.index(row, 1).data(Qt.UserRole + CustomRole.plain_dimension),
				"plain_progress": self.index(row, 4).data(Qt.UserRole + CustomRole.plain_downloaded_size),
				"time_start": self.index(row, 0).data(Qt.UserRole + CustomRole.start_time),
				"time_end": self.index(row, 0).data(Qt.UserRole + CustomRole.end_time),
				"status": self.index(row, 2).data(),
				"url": self.index(row, 0).data(Qt.UserRole + CustomRole.url)
			}
			data_in_model[start_i] = data
			start_i += 1

		return data_in_model

	def insert_custom_data(self, name, fullpath, url, plain_dimension, plain_progress, time_start, status):
		# used by the main to insert data resumed from the json

		name_item = QStandardItem(name)
		# adding the full path to the item in order to call the "reveal in finder" later on
		name_item.setData(fullpath, Qt.UserRole + CustomRole.full_path)
		name_item.setData(Qt.Checked, Qt.CheckStateRole)
		name_item.setData(time_start, Qt.UserRole + CustomRole.start_time)
		name_item.setData(url, Qt.UserRole + CustomRole.url)

		if plain_dimension is None:
			dim_item = QStandardItem("Unknown")
		else:
			dim_item = QStandardItem(utils.size_converter(plain_dimension))

		# here we will be holding the non-decorated dimension in bytes, it will be useful when updating the progress bar
		dim_item.setData(plain_dimension, Qt.UserRole + CustomRole.plain_dimension)
		if status == "Downloading..." or status == "Starting...":
			status = "Paused"
		status_item = QStandardItem(status)
		speed_item = QStandardItem("0 B/s")

		if plain_progress is not None:
			downloaded_item = QStandardItem(utils.size_converter(plain_progress))
		else:
			downloaded_item = QStandardItem("0 B")
			plain_progress = 0

		# inserting the plain progress data
		downloaded_item.setData(plain_progress, Qt.UserRole + CustomRole.plain_downloaded_size)
		progress_item = QStandardItem()

		if plain_dimension is None:
			# if the dimension is unknown then the progress bar is set to zero
			progress_item.setData(0, Qt.UserRole + CustomRole.progress_bar)
		else:
			# otherwise we set the right percentage
			progress_item.setData(plain_progress * 100 / int(plain_dimension), Qt.UserRole + CustomRole.progress_bar)
		self.appendRow([name_item, dim_item, status_item, speed_item, downloaded_item, progress_item])


