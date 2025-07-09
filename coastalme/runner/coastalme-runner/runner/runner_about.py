from pyqt_compat.QtWidgets import QMessageBox
from pyqt_compat.QtCore import Qt

from version import version_text

from pyqt_compat import QT_RICH_TEXT, QT_MESSAGE_BOX_OK, QT_MESSAGE_BOX_INFORMATION


def about_dialog():
    msg_box = QMessageBox()
    msg_box.setTextFormat(QT_RICH_TEXT)  # Makes links clickable
    msg_box.setStandardButtons(QT_MESSAGE_BOX_OK)
    msg_box.setIcon(QT_MESSAGE_BOX_INFORMATION)

    msg_box.setWindowTitle(f"Model Runner {version_text}")

    message = 'Model runner created to run COASTALME and other models.<br>'
    message += 'Model runner can be freely distributed and modified.<br><br>'

    message += "Application icon provided by <a href='https://icons8.com//'>Icons8</a><br><br>"

    message += "Dialog icon are blue bits provided by <a href='http://www.icojam.com'>IcoJam</a>"

    msg_box.setText(message)

    msg_box.exec()
