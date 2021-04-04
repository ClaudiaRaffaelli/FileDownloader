from sys import argv, exit
import os, json

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from gui.DownloadPage import DownloadPage
from gui.HistoryPage import HistoryPage
from gui.CloseDialog import CloseDialog
from gui.Utils import CustomRole


class MainWindowUIClass(QMainWindow):

	def __init__(self, parent=None):
		super(MainWindowUIClass, self).__init__(parent)
		uic.loadUi("gui/ui/Main.ui", self)

		# creating the content of the tabs
		self.downloadPage = DownloadPage()
		self.historyPage = HistoryPage()

		# detecting when the user changes tab
		# self.tabWidget.currentChanged.connect(self.onChange)
		self.tabWidget.addTab(self.downloadPage, "Download page")
		self.tabWidget.addTab(self.historyPage, "History page")

		# here is stored the row id (from history) of the rows that now are displayed in downloadPage but come from the
		# unfinished downloads from history
		self.in_progress_data = []

		self.lenJson = None

		self.initialization()

	def initialization(self):
		# read data from history if existing
		if os.path.exists("./UserHistory.json"):
			with open('./UserHistory.json') as json_file:
				data = json.load(json_file)
				for id_row, row_content in data.items():
					print(id_row)
					print(row_content)
					if row_content["status"] == "Completed" or row_content["status"] == "Aborted":
						# if the download is completed or aborted we only want to see it in the history
						self.historyPage.historyTableModel.insert_row(
							row_content["name"], row_content["path"], row_content["dimension"],
							row_content["status"], row_content["time_start"], row_content["time_end"])
					else:
						# the download goes into the model only if it still exists
						if os.path.exists(row_content["path"]):
							# saving the ids of the files loaded from the json (this downloads will be checked for
							# updating the json on close)
							self.in_progress_data.append(id_row)
							self.downloadPage.init_download(url=row_content["url"], saving_location=row_content["path"])
							self.downloadPage.downloadsTableModel.insert_custom_data(
								row_content["name"], row_content["path"], row_content["url"], row_content["dimension"],
								row_content["plain_progress"], row_content["time_start"],
								row_content["status"])
			self.lenJson = len(data)

	# handle close event
	def closeEvent(self, closeEvent):

		# asking the user if they really want to exit and stop all downloads
		close_dialog = CloseDialog(None)
		result = close_dialog.exec()

		if result:
			# if the history json already exists, we only update it with the new data
			# (some download that was in progress now maybe it is over and has changed status)
			if os.path.exists("./UserHistory.json"):
				print("esiste")
				# reading the file
				with open('./UserHistory.json', 'r') as infile:
					json_data = json.load(infile)
					# row contains the row index of the downloads table model (the downloads at start were inserted in order)
					row = 0
					# updating the downloads that were loaded from the json and are already there
					for id_row in self.in_progress_data:
						json_data[id_row]["dimension"] = self.downloadPage.downloadsTableModel.index(row, 1).data(Qt.UserRole + CustomRole.plain_dimension)
						json_data[id_row]["plain_progress"] = self.downloadPage.downloadsTableModel.index(row, 4).data(Qt.UserRole + CustomRole.plain_downloaded_size)
						json_data[id_row]["time_end"] = self.downloadPage.downloadsTableModel.index(row, 0).data(Qt.UserRole + CustomRole.end_time)
						json_data[id_row]["status"] = self.downloadPage.downloadsTableModel.index(row, 2).data()
						row += 1

					# getting the new downloads that are not in the json yet
					print(len(json_data))
					# len(self.in_progress_data) stores the amount of old row of unfinished downloads there
					# are in the model. This rows will be ignored
					data_in_model = self.downloadPage.downloadsTableModel.save_model(
						start_i=len(json_data), num_old_data=len(self.in_progress_data))

					# merging the two dictionaries
					new_data = {**json_data, **data_in_model}

				with open('./UserHistory.json', 'w') as outfile:
					json.dump(new_data, outfile)

			else:
				# if it doesn't exist we create the json and insert the data
				with open('./UserHistory.json', 'w') as outfile:
					data_in_model = self.downloadPage.downloadsTableModel.save_model(start_i=0, num_old_data=0)
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
