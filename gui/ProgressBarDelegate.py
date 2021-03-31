import os
import time
import requests
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QCoreApplication, QRect, pyqtSignal
from PyQt5.QtWidgets import QStyle, QStyledItemDelegate, QApplication, QStyleOptionProgressBar
from gui.Utils import CustomRole


class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progress = index.data(Qt.UserRole + CustomRole.progress_bar)
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        # TODO IMPORTANT CHECK PROGRESS BAR ON UBUNTU (ON MAC DOESN'T SHOW TEXT)
        opt.text = "{}%".format(progress)
        opt.textVisible = True
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
