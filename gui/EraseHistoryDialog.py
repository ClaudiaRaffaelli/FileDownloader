from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class EraseHistoryDialog(QDialog):

    def __init__(self, parent=None):
        super(EraseHistoryDialog, self).__init__(parent)
        uic.loadUi("gui/ui/Dialogs/eraseHistoryDialog.ui", self)

        # setting the cancel button as default
        self.buttonBox.buttons()[0].setAutoDefault(False)
        self.buttonBox.buttons()[1].setDefault(True)
