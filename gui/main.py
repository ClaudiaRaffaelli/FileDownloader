from sys import argv, exit

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from gui.DownloadPage import DownloadPage

# todo possibility to change the file name with double click and enter
# todo possibility to change the location where the file will be saved
# todo paste link directly to the page
# todo preventing a download with same url or name to start


class MainWindowUIClass(QMainWindow):

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
