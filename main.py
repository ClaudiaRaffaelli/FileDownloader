from sys import argv, exit
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, QThread, Qt, QSettings, QPoint, QFileInfo, QSize, QStandardPaths, \
	QDir, QModelIndex, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QKeySequence, QPixmapCache, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QMenu, QAction, QMainWindow, \
	QSizePolicy, QShortcut

from Worker import Worker
from DownloadPage import DownloadPage

# todo possibility to change the file name with double click and enter
# todo possibility to change the location where the file will be saved
# todo paste link directly to the page
# todo regex to check input by user, it must be a valid url
# todo preventing a download with same url or name to start

#  CONTROLLER


class MainWindowUIClass(QMainWindow):
	plop = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/BBC_Radio_logo.svg/210px-BBC_Radio_logo.svg.png"

	def __init__(self, parent=None):
		super(MainWindowUIClass, self).__init__(parent)
		uic.loadUi("gui/ui/Main.ui", self)

		# creating the content of the tabs
		self.downloadPage = DownloadPage()

		# detecting when the user changes tab
		#self.tabWidget.currentChanged.connect(self.onChange)
		self.mainViewIndex = self.tabWidget.addTab(self.downloadPage, "Download page")



if __name__ == '__main__':
	app = QApplication(argv)

	# setting high DPI allows to have a much better resolution for icons in macOS
	app.setAttribute(Qt.AA_UseHighDpiPixmaps)
	app.setApplicationName("SmartDownloader")
	w = MainWindowUIClass()
	w.showMaximized()
	exit(app.exec_())
