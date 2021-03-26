import os
import requests
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QCoreApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon

# MODEL


class Worker(QObject):

	def __init__(self, parent=None):
		super(QObject, self).__init__(parent)
		self.url = None
		self.completePath = None
		self.thread = QThread()

	def start_download(self, filepath, url):
		self.completePath = filepath
		self.url = url

		self.moveToThread(self.thread)
		self.thread.started.connect(self.download)
		self.thread.start()

	def download(self):

		with requests.Session() as session:
			# if the path already exists we resume
			if os.path.exists(self.completePath):
				# getting the file size (bytes) in order to know where to re-start downloading
				resume_position = os.stat(self.completePath).st_size
			else:
				# start from the beginning
				resume_position = 0

			response = session.get(self.url, headers={"Range": "bytes={}-".format(resume_position)})
			with open(self.completePath, 'ab+') as fd:
				for c in response.iter_content():
					# if the download has not been set to pause we continue the download, otherwise the thread returns
					if QThread.currentThread().isInterruptionRequested():
						print("download paused")
						QThread.currentThread().quit()
						return
					else:
						fd.write(c)
		# when the file has been downloaded we quit the thread
		QThread.currentThread().quit()


