from sys import argv, exit
import os, json

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from gui.DownloadPage import DownloadPage
from gui.HistoryPage import HistoryPage
from gui.CloseDialog import CloseDialog

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
		self.historyPage = HistoryPage()

		# detecting when the user changes tab
		#self.tabWidget.currentChanged.connect(self.onChange)
		self.tabWidget.addTab(self.downloadPage, "Download page")
		self.tabWidget.addTab(self.historyPage, "History page")

		# here is stored the row id (from history) of the rows that now are displayed in downloadPage but come from the
		# unfinished downloads from history
		self.in_progress_data = []

		self.initialization()

	def initialization(self):
		# read data from history if existing
		if os.path.exists("./UserHistory.json"):
			with open('./UserHistory.json') as json_file:
				data = json.load(json_file)
				for id_row, row_content in data.items():
					print(id_row)
					print(row_content)
					# todo continua qui
					if row_content["status"] == "Completed" or row_content["status"] == "Aborted":
						# if the download is completed or aborted we only want to see it in the history
						# todo load nella history
						pass
					else:
						self.downloadPage.init_download(url=row_content["url"], saving_location=row_content["path"])
						self.downloadPage.downloadsTableModel.insert_custom_data(
							row_content["name"], row_content["path"], row_content["url"], row_content["dimension"],
							row_content["plain_progress"], row_content["time_start"], row_content["time_end"],
							row_content["status"])


	# handle close event
	def closeEvent(self, closeEvent):

		# asking the user if they really want to exit and stop all downloads
		close_dialog = CloseDialog(None)
		result = close_dialog.exec()

		if result:
			# todo updating the download data
			# qui ci metto tutti i record della downloadTableView con tutti i dati che servono per ripristinare la
			# vista.
			# if the history json already exists, we only update it with the new data
			# (some download that was in progress now maybe it is over and has changed status)
			if os.path.exists("./UserHistory.json"):
				print("esiste")
			else:
				# if it doesn't exist we create the json and insert the data
				with open('./UserHistory.json', 'w') as outfile:
					data_in_model = self.downloadPage.downloadsTableModel.save_model(start_i=0)
					json.dump(data_in_model, outfile)

			closeEvent.accept()
		else:
			closeEvent.ignore()


if __name__ == '__main__':
	app = QApplication(argv)

	# setting high DPI allows to have a much better resolution for icons in macOS
	app.setAttribute(Qt.AA_UseHighDpiPixmaps)
	app.setApplicationName("SmartDownloader")
	w = MainWindowUIClass()
	w.showMaximized()
	exit(app.exec_())
