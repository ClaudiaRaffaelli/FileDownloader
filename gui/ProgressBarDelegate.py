from PyQt5.QtCore import Qt
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
        opt.text = "{}%".format(progress)
        opt.textVisible = True
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)
