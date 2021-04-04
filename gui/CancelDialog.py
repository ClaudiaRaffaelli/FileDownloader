from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class CancelDialog(QDialog):

    def __init__(self, parent=None):
        super(CancelDialog, self).__init__(parent)
        uic.loadUi("gui/ui/Dialogs/cancelDownloadsDialog.ui", self)

        # setting the No button as default
        self.buttonBox.buttons()[0].setAutoDefault(False)
        self.buttonBox.buttons()[1].setDefault(True)

        # setting the stylesheet
        stylesheet_file = "gui/stylesheet.txt"
        with open(stylesheet_file, "r") as fh:
            self.setStyleSheet(fh.read())
