from pyqt_compat.QtWidgets import QStyledItemDelegate, QStyleOptionProgressBar, QStyle, QApplication
from pyqt_compat.QtGui import QPainter, QPalette, QBrush, QColor
from pyqt_compat.QtCore import Qt, QMargins

from pyqt_compat import QT_ITEM_DATA_FOREGROUND_ROLE


class ProgressBarDelegate(QStyledItemDelegate):
    def __init__(self):
        super(ProgressBarDelegate, self).__init__()

    def paint(self, painter, option, index):
        progress = index.data()

        if int(progress) == 100:
            brush = index.data(QT_ITEM_DATA_FOREGROUND_ROLE)
            painter.setBrush(brush)
            painter.drawRect(option.rect.marginsRemoved(QMargins(2, 2, 2, 2)))
        else:
            opt = QStyleOptionProgressBar()
            opt.rect = option.rect
            opt.minimum = 0
            opt.maximum = 100
            opt.progress = int(progress)
            opt.text = f"{opt.progress} %"
            opt.textVisible = True
            # opt.palette.setBrush(QT_PALETTE_NORMAL, QT_PALETTE_BASE, QBrush(QT_RED))
            # p.setColor(QT_PALETTE_WINDOWText, QT_RED)
            # p.setColor(QPalette::Foreground, Qt::red);
            # p.setColor(QPalette::Background, Qt::green);
            # p.setColor(QPalette::Highlight, Qt::yellow);
            opt.state |= QStyle.StateFlag.State_Horizontal  # <--
            style = (
                option.widget.style() if option.widget is not None else QApplication.style()
            )
            # self.setStyleSheet("QProgressBar::chunk {background: hsva(0, 255, 255, 60%);}");
            style.drawControl(
                QStyle.ControlElement.CE_ProgressBar, opt, painter, option.widget
            )
