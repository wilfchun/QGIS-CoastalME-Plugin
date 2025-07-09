# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_1d_results.ui'
#
# Created: Fri May 08 12:43:29 2015
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


class Ui_coastalmeqgis_1d_results(object):
    def setupUi(self, coastalmeqgis_1d_results):
        coastalmeqgis_1d_results.setObjectName(_fromUtf8("coastalmeqgis_1d_results"))
        coastalmeqgis_1d_results.resize(400, 300)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_1d_results)
        self.buttonBox.setGeometry(QtCore.QRect(80, 240, 191, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QLabel(coastalmeqgis_1d_results)
        self.label.setGeometry(QtCore.QRect(30, 20, 321, 51))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QLabel(coastalmeqgis_1d_results)
        self.label_2.setGeometry(QtCore.QRect(30, 70, 321, 101))
        font = QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(coastalmeqgis_1d_results)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), coastalmeqgis_1d_results.accept)
        self.buttonBox.accepted.connect(coastalmeqgis_1d_results.acceptt)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), coastalmeqgis_1d_results.reject)
        self.buttonBox.rejected.connect(coastalmeqgis_1d_results.reject)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_1d_results)

    def retranslateUi(self, coastalmeqgis_1d_results):
        coastalmeqgis_1d_results.setWindowTitle(_translate("coastalmeqgis_1d_results", "COASTALME 1D Results Viewer", None))
        self.label.setText(_translate("coastalmeqgis_1d_results", "This 1D results visualisation is currently \n"
"being interegrated with QGIS.", None))
        self.label_2.setText(_translate("coastalmeqgis_1d_results", "Clicking OK will launch the utility in \n"
"stand-alone mode. \n"
"It requires the results in the format \n"
"outputted in the beta 2013 COASTALME release.", None))

