import os
import time
from enum import Enum
import requests
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QThread

import gui.Utils as utils


class DownloadStatus(Enum):
	idle = 0
	downloading = 1
	pause = 2
	abort = 3
	complete = 4


class Worker(QObject):
	download_starting = pyqtSignal(str, str)
	download_started = pyqtSignal(int, int)
	download_update = pyqtSignal(int, int, str)
	download_completed = pyqtSignal(int, int)
	download_interrupted = pyqtSignal(int, DownloadStatus)
	download_restarted = pyqtSignal(int)

	def __init__(self, parent=None):
		super(QObject, self).__init__(parent)
		self.url = None
		self.completePath = None
		self.thread = QThread()
		self.threadId = -1
		self.initialized = False
		self.lengthDownload = -1
		self.status = DownloadStatus.idle

	def init_download(self, thread_id, filepath, url, start):
		"""
		:param thread_id: int ID that identifies uniquely the worker
		:param filepath: the complete path to the file. If not specified is ""
		:param url: the input url of the download
		:param start: boolean that tells if the worker has to start the download immediately or not. If False it means
						that the download has been loaded from json file
		"""
		# if the user has not set where to save the file, it will be saved in a default directory
		if filepath == "":
			# creating the folder where to save the files as default if it doesn't exists
			Path("./Downloads").mkdir(parents=True, exist_ok=True)

			# also by default the file is saved in the Downloads directory
			self.completePath = "./Downloads/" + url.split('/')[-1]
		else:
			self.completePath = filepath

		self.threadId = thread_id
		self.url = url

		# start from the beginning
		self.resume_position = 0
		# bytes of downloads already downloaded
		self.downloaded_size = 0

		self.status = DownloadStatus.downloading
		if start is True:
			self.start_download()

	def start_download(self):
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
			self.downloaded_size = self.resume_position
		else:
			# if it doesn't it means that the download has been deleted/moved externally or the downloaded was
			# deleted from button. In any case, we re-start from the beginning of the download, and reset any progress
			# start from the beginning
			self.resume_position = 0
			# bytes of downloads already downloaded
			self.downloaded_size = 0

		self.download_restarted.emit(self.threadId)

		if not self.initialized:
			self.moveToThread(self.thread)
			self.thread.started.connect(self.download)
			self.thread.start()
			if self.resume_position != 0:
				self.initialized = True
		else:
			self.status = DownloadStatus.downloading
			self.moveToThread(self.thread)
			self.thread.start()

	def download(self):

		with requests.Session() as session:
			response = session.get(self.url, stream=True, headers={"Range": "bytes={}-".format(self.resume_position)})

			# only at the first start of the download it is set the size of it
			if not self.initialized:
				if 'Content-Length' not in response.headers:
					# the content length header is not provided for this download file and is left as unknown
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
					# if the download has not been set to pause or aborted we continue the download,
					# otherwise the thread returns
					if QThread.currentThread().isInterruptionRequested():
						# print("download interrupted with status {}".format(self.status))
						self.download_interrupted.emit(self.threadId, self.status)
						# resetting the status to idle
						self.status = DownloadStatus.idle
						QThread.currentThread().quit()
						return
					else:
						self.downloaded_size += len(chunk)
						self.download_update.emit(self.threadId, self.downloaded_size,
							utils.speed_calculator(self.downloaded_size, time.time() - start))
						fd.write(chunk)

		# print("download exited")
		# when the file has been downloaded we quit the thread and send a signal of finish that also sets the downloaded
		# size. If the size was unknown now it is not.
		# This also covers the case where the content length has changed from a pause to a re-start
		self.download_completed.emit(self.threadId, self.downloaded_size)
		self.status = DownloadStatus.complete
		QThread.currentThread().quit()
