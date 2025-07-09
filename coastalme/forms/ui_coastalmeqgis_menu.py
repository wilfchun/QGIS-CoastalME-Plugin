# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_menu.ui'
#
# Created: Tue Jan 19 11:20:11 2016
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtWidgets import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


from ..compatibility_routines import QT_BUTTON_BOX_CANCEL, QT_BUTTON_BOX_OK, QT_HORIZONTAL


class Ui_coastalmeqgis_menu(object):
    def setupUi(self, coastalmeqgis_menu):
        coastalmeqgis_menu.setObjectName(_fromUtf8("coastalmeqgis_menu"))
        coastalmeqgis_menu.resize(400, 300)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_menu)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(coastalmeqgis_menu)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), coastalmeqgis_menu.accept)
        self.buttonBox.accepted.connect(coastalmeqgis_menu.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), coastalmeqgis_menu.reject)
        self.buttonBox.rejected.connect(coastalmeqgis_menu.reject)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_menu)

    def retranslateUi(self, coastalmeqgis_menu):
        coastalmeqgis_menu.setWindowTitle(_translate("coastalmeqgis_menu", "coastalmeqgis_menu", None))

