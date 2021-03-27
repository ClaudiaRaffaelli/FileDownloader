import os
import requests
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QCoreApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon

# MODEL


class Worker(QObject):

	download_starting = pyqtSignal(str, str)
	download_started = pyqtSignal(int, int)
	download_update = pyqtSignal(int, int)

	def __init__(self, parent=None):
		super(QObject, self).__init__(parent)
		self.url = None
		self.completePath = None
		self.thread = QThread()
		self.threadId = -1

	def start_download(self, thread_id, filepath, url):
		self.threadId = thread_id
		print("threadID", self.threadId)
		self.completePath = filepath
		self.url = url

		self.moveToThread(self.thread)
		self.thread.started.connect(self.download)
		self.thread.start()

	def download(self):
		# todo signal of end download that deletes the model object from the array in downloadPage

		# emitting signal with list of the form [saving path, url] saying that we are starting the download
		# this is connected through DownloadPage to the table model
		self.download_starting.emit(self.completePath, self.url)

		with requests.Session() as session:
			# if the path already exists we resume
			if os.path.exists(self.completePath):
				# getting the file size (bytes) in order to know where to re-start downloading
				resume_position = os.stat(self.completePath).st_size
			else:
				# start from the beginning
				resume_position = 0
			print("qui veloce")
			# todo why is this next line executed so slow for large files? Maybe stream does not works this way
			response = session.get(self.url, stream=True, headers={"Range": "bytes={}-".format(resume_position)})
			# todo this is not the entire lenght in the case of restarted download
			length_download_data = len(response.content)
			print("qui super lento")

			# emitting signal with list of the form [saving path, url, dimension of download]
			self.download_started.emit(self.threadId, length_download_data)
			downloaded_size = 0
			with open(self.completePath, 'ab+') as fd:
				# the chunk size downloaded at a time is of 1MiB todo put 1024x1024
				for chunk in response.iter_content(chunk_size=1024*1024):
					print(len(chunk))
					# if the download has not been set to pause we continue the download, otherwise the thread returns
					if QThread.currentThread().isInterruptionRequested():
						print("download paused")
						QThread.currentThread().quit()
						return
					else:
						downloaded_size += len(chunk)
						self.download_update.emit(self.threadId, downloaded_size)
						fd.write(chunk)
		# when the file has been downloaded we quit the thread
		print("download exited")
		QThread.currentThread().quit()


