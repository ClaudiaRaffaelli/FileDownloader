import os
import time
import requests
from pathlib import Path
import shutil
import tempfile

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QCoreApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon

import gui.Utils as utils


# MODEL


class Worker(QObject):
	download_starting = pyqtSignal(str, str)
	download_started = pyqtSignal(int, int)
	download_update = pyqtSignal(int, int, str)
	download_completed = pyqtSignal(int, int)
	download_paused = pyqtSignal(int)

	def __init__(self, parent=None):
		super(QObject, self).__init__(parent)
		self.url = None
		self.completePath = None
		self.thread = QThread()
		self.threadId = -1
		self.initialized = False
		self.lengthDownload = -1
		# todo maybe set thread id as a name of thread

	def start_download(self, thread_id, filepath, url):
		# if the user has not set where to save the file, it will be saved in a default directory
		if filepath == "":
			# creating the folder where to save the files as default if it doesn't exists
			Path("../Downloads").mkdir(parents=True, exist_ok=True)

			# also by default the file is saved in the Download directory
			self.completePath = "./Downloads/" + url.split('/')[-1]
		else:
			self.completePath = filepath

		self.threadId = thread_id
		print("threadID", self.threadId)
		self.url = url

		# start from the beginning
		self.resume_position = 0
		# bytes of downloads already downloaded
		self.downloaded_size = 0

		self.moveToThread(self.thread)
		self.thread.started.connect(self.download)
		self.thread.start()

		# emitting signal with list of the form [saving path, url] saying that we are starting the download
		# this is connected through DownloadPage to the table model
		self.download_starting.emit(self.completePath, self.url)

	def restart_download(self):
		# if the path already exists we resume
		if os.path.exists(self.completePath):
			# getting the file size (bytes) in order to know where to re-start downloading
			self.resume_position = os.stat(self.completePath).st_size
		else:
			# start from the beginning
			self.resume_position = 0

		self.moveToThread(self.thread)
		self.thread.start()

		# todo qua un segnale che ho iniziato il resume
		# todo investigare come mai non sempre ripartono bene i downloads. Come riprodurre: apk link senza specificare
		#  il percorso, parte, pausa, faccio ripartire, concluso ma non lo era.

	def download(self):
		# todo signal of end download that deletes the model object from the array in downloadPage

		with requests.Session() as session:

			response = session.get(self.url, stream=True, headers={"Range": "bytes={}-".format(self.resume_position)})

			# only at the first start of the download it is set the size of it
			if not self.initialized:
				if 'Content-Length' not in response.headers:
					# the content length header is not provided for this download file and we have to set it to unknown
					pass
				else:
					# there is a content-length header
					self.lengthDownload = response.headers['Content-Length']
					# emitting signal of started download communicating the length of the download itself
					self.download_started.emit(self.threadId, int(self.lengthDownload))

				self.initialized = True

			with open(self.completePath, 'ab+') as fd:
				start = time.time()
				# the chunk size downloaded at a time is of 1MiB
				for chunk in response.iter_content(chunk_size=1024 * 1024):
					# if the download has not been set to pause we continue the download, otherwise the thread returns
					if QThread.currentThread().isInterruptionRequested():
						print("download paused")
						self.download_paused.emit(self.threadId)
						QThread.currentThread().quit()
						return
					else:
						self.downloaded_size += len(chunk)
						self.download_update.emit(self.threadId, self.downloaded_size,
							utils.speed_calculator(self.downloaded_size, time.time() - start))
						fd.write(chunk)

		# when the file has been downloaded we quit the thread
		print("download exited")
		# when the file has been downloaded we quit the thread and send a signal of finish that also sets the downloaded
		# size. If the size was unknown now it is not
		self.download_completed.emit(self.threadId, self.downloaded_size)
		QThread.currentThread().quit()
