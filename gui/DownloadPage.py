import platform
import os
import subprocess

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QFileInfo
from PyQt5.QtWidgets import QFileDialog, QMenu, QAction, QWidget, QTableView, QHeaderView

from gui.Worker import Worker
from gui.DownloadsTableModel import DownloadsTableModel, CustomRole


class DownloadPage(QWidget):
	# https://github.com/ClaudiaRaffaelli/Cindy-s-Bad-Luck-BLS-VR/archive/refs/tags/v1.0.2.zip
	# https://github.com/ClaudiaRaffaelli/Cindy-s-Bad-Luck-BLS-VR/releases/download/v1.0.2/BLS.apk


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
		# connecting the signal for the context menu on right click on download table row
		self.downloadsTableView.setContextMenuPolicy(Qt.CustomContextMenu)
		self.downloadsTableView.customContextMenuRequested.connect(self.context_menu_triggered_downloads_table)

		# where the file will be saved
		self.savingLocation = ""

		# current threads of download
		# todo make it a dictionary with as keys the ids of the workers 0,1,.. and value the worker object
		#  so that when a worker has finished you can delete it without changing the indices of the dictionary (ex array)
		self.downloadWorkerThreads = []


	@pyqtSlot()
	def start_individual_download(self):
		# taking the url from the lineEdit
		url = self.urlLineEdit.text()

		# todo 0 is the row and 5 the fixed column. The index should be taken as input
		#self.downloadsTableView.setIndexWidget(self.downloadsTableModel.index(0, 5), QProgressBar())

		# creating the worker that will download
		worker = Worker()
		# putting the worker for this download in the array of worker threads
		self.downloadWorkerThreads.append(worker)

		# Connecting all the signals of the thread.
		# Adding the download to the model in order to display it in the table view with initial data
		worker.download_starting.connect(self.downloadsTableModel.add_download_to_table)

		worker.download_started.connect(self.downloadsTableModel.init_row)
		# This signal will be used to update the table model
		worker.download_update.connect(self.downloadsTableModel.update_data_to_table)
		# this signal will be used to know when the download is over
		worker.download_completed.connect(self.downloadsTableModel.completed_row)
		# this signal will be used to set the row in table model as paused
		worker.download_paused.connect(self.downloadsTableModel.paused_row)

		# starting the worker assigning an ID
		worker.start_download(thread_id=len(self.downloadWorkerThreads)-1, filepath=self.savingLocation, url=url)

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

	@pyqtSlot(QPoint)
	def context_menu_triggered_downloads_table(self, clickpoint):
		index = self.downloadsTableView.indexAt(clickpoint)
		if index.isValid():
			context = QMenu(self)
			finder = "Show in Explorer"
			if platform.system() == "Linux":
				finder = "Reveal in File Explorer"
			elif platform.system() == "Darwin":
				finder = "Reveal in Finder"
			openExplorer = QAction(finder, self)
			# todo maybe more actions here
			context.addActions([openExplorer])
			openExplorer.triggered.connect(self.open_explorer_item)
			context.exec(self.downloadsTableView.mapToGlobal(clickpoint))

	@pyqtSlot()
	def open_explorer_item(self):
		# todo find out what happens if you move the file
		index = self.downloadsTableView.selectionModel().currentIndex()
		currentItem = self.downloadsTableView.model().itemFromIndex(index)
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