import platform
import os
import subprocess

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QFileInfo, QModelIndex, QRegExp
from PyQt5.QtWidgets import QFileDialog, QMenu, QAction, QWidget, QTableView, QHeaderView, QTableWidget
from PyQt5.QtGui import QRegExpValidator
from gui.Worker import Worker
from gui.DownloadsTableModel import DownloadsTableModel
from gui.ProgressBarDelegate import ProgressBarDelegate
from gui.Utils import CustomRole
from gui.CancelDialog import CancelDialog
from gui.Worker import DownloadStatus


class DownloadPage(QWidget):
	# does not have content-length header:
	# https://github.com/ClaudiaRaffaelli/Cindy-s-Bad-Luck-BLS-VR/archive/refs/tags/v1.0.2.zip
	# does have content-length header:
	# https://github.com/ClaudiaRaffaelli/Cindy-s-Bad-Luck-BLS-VR/releases/download/v1.0.2/BLS.apk
	# https://pbs.twimg.com/profile_images/638746415901114368/e4h_VW4A.png
	# todo pdf are not downloading why?
	# https://e-l.unifi.it/pluginfile.php/1123757/mod_resource/content/4/DownloadManager.pdf

	# todo mi salvo in una variabile ogni volta che un download viene completato e magari mi tengo anche che download
	#  era. Quando faccio il click sulla history vedo se ci sono novità e le prendo, sennò nulla.
	#  La history la inizializzo appena apro con le cose di un json
	#  Il json lo riempio ad ogni uscita del programma. Viene chiesto se voglio uscire


	# todo quando carico le cose da json prima controllo che il path sia valido e il file non sia stato spostato mentre
	#  il programma era chiuso

	def __init__(self, parent=None):
		super(DownloadPage, self).__init__(parent)
		uic.loadUi("gui/ui/downloadWidget.ui", self)

		# creating the table view for the downloads and the model that holds the data
		self.downloadsTableModel = DownloadsTableModel()
		self.downloadsTableView = QTableView()
		self.downloadsTableView.setSortingEnabled(True)
		self.downloadsTableView.setSelectionBehavior(QTableView.SelectRows)

		# Init table view
		self.downloadsTableView.setModel(self.downloadsTableModel)

		self.downloadsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
		self.downloadsTableView.horizontalHeader().setStretchLastSection(True)
		# the fields in the table are non editable
		self.downloadsTableView.setEditTriggers(QTableWidget.NoEditTriggers)

		self.mainLayout.addWidget(self.downloadsTableView)
		# connecting the signal for the context menu on right click on download table row
		self.downloadsTableView.setContextMenuPolicy(Qt.CustomContextMenu)
		self.downloadsTableView.customContextMenuRequested.connect(self.context_menu_triggered_downloads_table)
		# connecting the signal for one click on a row
		self.downloadsTableView.clicked.connect(self.row_click)

		# where the file will be saved
		self.savingLocation = ""

		# current threads of download
		# todo make it a dictionary with as keys the ids of the workers 0,1,.. and value the worker object
		#  so that when a worker has finished you can delete it without changing the indices of the dictionary (ex array)
		self.downloadWorkerThreads = []

		# validation of the input in text line for generic URLs:
		reg_ex = QRegExp("https?:\/\/[-a-zA-Z0-9@:%._\+~#=\/]{2,256}")
		input_line_edit_validator = QRegExpValidator(reg_ex, self.urlLineEdit)
		self.urlLineEdit.setValidator(input_line_edit_validator)

		# number of checked rows (this will activate if >0 or deactivate if ==0 the buttons of Start, Pause, Cancel
		self.numCheckedRows = 0

		delegate = ProgressBarDelegate(self.downloadsTableView)
		self.downloadsTableView.setItemDelegateForColumn(5, delegate)

	@pyqtSlot()
	def start_individual_download(self):
		# todo save all in a json to maintain chronology

		# taking the url from the lineEdit
		url = self.urlLineEdit.text()

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
		# this signal will be used to set the row in table model as paused or aborted
		worker.download_interrupted.connect(self.downloadsTableModel.interrupted_row)
		# this signal will be used to set the row as re-started a delete
		worker.download_restarted.connect(self.downloadsTableModel.restarted_row)

		# todo change icon of stop with trash can

		# starting the worker assigning an ID
		worker.start_download(thread_id=len(self.downloadWorkerThreads) - 1, filepath=self.savingLocation, url=url)

		# if this is the first time start a download (there are no rows) we activate the buttons
		if self.numCheckedRows == 0:
			self.cancelSelectedDownloadButton.setEnabled(True)
			self.pauseSelectedDownloadButton.setEnabled(True)
			self.startSelectedDownloadButton.setEnabled(True)
		self.numCheckedRows += 1

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
		# resume all the checked downloads if not already running nor already completed
		checked_rows = self.downloadsTableModel.get_all_checked_rows()
		print("le checked")
		print(checked_rows)
		for row in checked_rows:
			print(self.downloadWorkerThreads[row].status)
			if (not self.downloadWorkerThreads[row].thread.isRunning()) \
					and (not self.downloadWorkerThreads[row].status == DownloadStatus.complete):
				print("Aveva status {}".format(self.downloadWorkerThreads[row].status))
				print("non è running la riga ", row, " la faccio partire")
				self.downloadWorkerThreads[row].restart_download()

	@pyqtSlot()
	def pause_download(self):
		# pauses all the checked downloads if not already paused
		checked_rows = self.downloadsTableModel.get_all_checked_rows()
		print("le checked")
		print(checked_rows)
		for row in checked_rows:
			if self.downloadWorkerThreads[row].thread.isRunning():
				# pause the download at row if it is running, asking the worker to pause
				self.downloadWorkerThreads[row].status = DownloadStatus.pause
				self.interrupt_row(row)
		print("interrupt request")

	def interrupt_row(self, row):
		# status indicates how the row needs to be interrupted (if paused or aborted)
		print("è running la riga ", row, " la fermo")
		self.downloadWorkerThreads[row].thread.requestInterruption()
		self.downloadWorkerThreads[row].thread.wait(2000)

	@pyqtSlot()
	def cancel_download(self):
		# asking the user if they really want to cancel all progress for selected downloads.
		cancel_dialog = CancelDialog(None)
		result = cancel_dialog.exec()

		if result:
			# if the user presses Yes we delete the downloads
			checked_rows = self.downloadsTableModel.get_all_checked_rows()
			# obtain the path to the file for all checked_rows downloads and delete the file
			for row in checked_rows:
				if self.downloadWorkerThreads[row].thread.isRunning():
					# setting for the thread the request to abort
					self.downloadWorkerThreads[row].status = DownloadStatus.abort
					self.interrupt_row(row)
				else:
					# it means that the download was paused or concluded and we only have to reset the table model
					self.downloadsTableModel.interrupted_row(row, DownloadStatus.abort)
					# If we decide to start again the download (which is possible since that the url is still kept)
					# the progress of download to zero is resetted from the worker
					self.downloadWorkerThreads[row].status = DownloadStatus.idle


				# then try to delete the file
				print("deleting the selected downloads {}".format(self.downloadsTableModel.get_full_path(row)))
				# todo set the status of the download to Aborted and if started again it must be done from the start
				try:
					os.remove(self.downloadsTableModel.get_full_path(row))
				except:
					print("Could not delete file {}".format(self.downloadsTableModel.get_full_path(row)))

		# if result is True it means that the user has pressed No or the x on the corner of the dialog,
		# as default the downloads are not deleted

	@pyqtSlot()
	def parse_url(self):
		# todo url such as https://gattoblabla CRASHA CORREGGI ASSOLUTAMENTE
		# enabling the choose save location and start download buttons when there is a URL with a valid start text
		if self.urlLineEdit.text().startswith(("http://", "https://")) and \
				self.startIndividualDownloadButton.isEnabled() is False:
			self.startIndividualDownloadButton.setEnabled(True)
			self.chooseLocationButton.setEnabled(True)
		elif not self.urlLineEdit.text().startswith(("http://", "https://")) and \
				self.startIndividualDownloadButton.isEnabled() is True:
			self.startIndividualDownloadButton.setEnabled(False)
			self.chooseLocationButton.setEnabled(False)

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
			# todo maybe more actions here like start, pause, cancel
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

	@pyqtSlot(QModelIndex)
	def row_click(self, index):
		# single click on first column, the checkbox state is changed
		if index.isValid() and index.column() == 0:
			# the return is a boolean that tells if the row now is checked or unchecked
			is_checked = self.downloadsTableModel.toggle_checkbox(index)
			# there is a one more checked row now and we increment the counter
			if is_checked is True:
				# if before there wasn't any row selected, we have to enable this buttons
				if self.numCheckedRows == 0:
					self.cancelSelectedDownloadButton.setEnabled(True)
					self.pauseSelectedDownloadButton.setEnabled(True)
					self.startSelectedDownloadButton.setEnabled(True)
				self.numCheckedRows += 1
			else:
				self.numCheckedRows -= 1
				# deactivating the buttons of Start, Pause, Cancel because there are no selected rows of downloads
				if self.numCheckedRows == 0:
					self.cancelSelectedDownloadButton.setEnabled(False)
					self.pauseSelectedDownloadButton.setEnabled(False)
					self.startSelectedDownloadButton.setEnabled(False)

