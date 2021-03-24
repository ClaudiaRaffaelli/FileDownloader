from sys import argv, exit
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, QThread, Qt, QSettings, QPoint, QFileInfo, QSize, QStandardPaths, \
	QDir, QModelIndex, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QKeySequence, QPixmapCache, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QMenu, QAction, QMainWindow, \
	QSizePolicy, QShortcut

from Worker import Worker

# todo possibility to change the file name with double click and enter
# todo possibility to change the location where the file will be saved

#  CONTROLLER

class MainWindowUIClass(QMainWindow):
	plop = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/BBC_Radio_logo.svg/210px-BBC_Radio_logo.svg.png"

	def __init__(self, parent=None):
		super(MainWindowUIClass, self).__init__(parent)
		uic.loadUi("gui/ui/mainInterface.ui", self)

	@pyqtSlot()
	def start_resume_download(self):
		# passing the url to download
		self.worker = Worker(self.urlLineEdit.text())
		self.thread = QThread()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.download)
		self.thread.start()

	@pyqtSlot()
	def pause_download(self):
		self.thread.requestInterruption()
		self.thread.wait(2000)
		print("interrupt request")


if __name__ == '__main__':
	app = QApplication(argv)

	# setting high DPI allows to have a much better resolution for icons in macOS
	app.setAttribute(Qt.AA_UseHighDpiPixmaps)
	app.setApplicationName("SmartDownloader")
	w = MainWindowUIClass()
	w.showMaximized()
	exit(app.exec_())


