from sys import argv, exit
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, QThread, Qt, QSettings, QPoint, QFileInfo, QSize, QStandardPaths, \
	QDir, QModelIndex, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QKeySequence, QPixmapCache, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QMenu, QAction, QMainWindow, \
	QSizePolicy, QShortcut, QWidget, QTableView, QHeaderView, QProgressBar

from Worker import Worker
from DownloadsTableModel import DownloadsTableModel

# controller


class DownloadPage(QWidget):
	# https://github.com/ClaudiaRaffaelli/Cindy-s-Bad-Luck-BLS-VR/archive/refs/tags/v1.0.2.zip

	def __init__(self, parent=None):
		super(DownloadPage, self).__init__(parent)
		uic.loadUi("gui/ui/downloadWidget.ui", self)

		# creating the table view for the downloads and the model that holds the data
		self.downloadsTableModel = DownloadsTableModel()
		self.downloadsTableView = QTableView()
		self.downloadsTableView.setSortingEnabled(True)

		# Init table view
		self.downloadsTableView.setModel(self.downloadsTableModel)
		self.downloadsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
		self.downloadsTableView.horizontalHeader().setStretchLastSection(True)

		self.mainLayout.addWidget(self.downloadsTableView)

		# creating the folder where to save the files as default if it doesn't exists
		# Path("./Downloads").mkdir(parents=True, exist_ok=True)

		# also by default the file is saved in the Download directory
		# self.rootPath = "./Downloads/"
		self.savingLocation = ""

		# current threads of download
		self.downloadWorkerThreads = []


	@pyqtSlot()
	def start_individual_download(self):
		# taking the url from the lineEdit
		url = self.urlLineEdit.text()

		# adding the download to the model in order to display it in the table view
		self.downloadsTableModel.add_download_to_table(fullpath=self.savingLocation, url=url)
		# todo 0 is the row and 5 the fixed column. The index should be taken as input
		#self.downloadsTableView.setIndexWidget(self.downloadsTableModel.index(0, 5), QProgressBar())

		# creating the worker that will download
		worker = Worker()
		# putting the worker for this download in the array of worker threads
		self.downloadWorkerThreads.append(worker)
		# starting the worker
		worker.start_download(filepath=self.savingLocation, url=url)

	@pyqtSlot()
	def choose_location_save(self):
		# todo maybe write somewhere on the gui the location of saving
		dialog = QFileDialog(self, "Choose location")
		dialog.setOption(QFileDialog.DontUseNativeDialog, True)
		dialog.setOption(QFileDialog.DontResolveSymlinks, True)
		dialog.setFileMode(QFileDialog.AnyFile)
		# todo activate the commented line, use the following only for debug
		dialog.setDirectory("./Downloads/")
		# dialog.setDirectory(QDir.homePath())
		# as default the downloaded file will be called with the original file name but it can be changed by the user
		url = self.urlLineEdit.text()
		filename = url.split('/')[-1]
		self.savingLocation = dialog.getSaveFileName(self, "Choose file name", filename)[0]

	@pyqtSlot()
	def start_resume_download(self):
		# todo this one will start all downloads that are stopped (or only the selected ones)
		pass

	@pyqtSlot()
	def pause_download(self):
		# pauses all downloads todo maybe it will only pause the selected ones
		for worker in self.downloadWorkerThreads:
			worker.thread.requestInterruption()
			worker.thread.wait(2000)
			print("interrupt request")
