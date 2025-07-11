# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_splitMI.ui'
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


class Ui_coastalmeqgis_splitMI(object):
    def setupUi(self, coastalmeqgis_splitMI):
        coastalmeqgis_splitMI.setObjectName(_fromUtf8("coastalmeqgis_splitMI"))
        coastalmeqgis_splitMI.resize(400, 225)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_splitMI)
        self.buttonBox.setGeometry(QtCore.QRect(110, 180, 171, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label1 = QLabel(coastalmeqgis_splitMI)
        self.label1.setGeometry(QtCore.QRect(10, 10, 108, 22))
        self.label1.setObjectName(_fromUtf8("label1"))
        self.sourcelayer = QComboBox(coastalmeqgis_splitMI)
        self.sourcelayer.setGeometry(QtCore.QRect(10, 30, 361, 27))
        self.sourcelayer.setObjectName(_fromUtf8("sourcelayer"))
        self.label2 = QLabel(coastalmeqgis_splitMI)
        self.label2.setGeometry(QtCore.QRect(10, 70, 121, 22))
        self.label2.setObjectName(_fromUtf8("label2"))
        self.outfolder = QLineEdit(coastalmeqgis_splitMI)
        self.outfolder.setGeometry(QtCore.QRect(10, 90, 261, 21))
        self.outfolder.setReadOnly(False)
        self.outfolder.setObjectName(_fromUtf8("outfolder"))
        self.browseoutfile = QPushButton(coastalmeqgis_splitMI)
        self.browseoutfile.setGeometry(QtCore.QRect(290, 90, 81, 26))
        self.browseoutfile.setObjectName(_fromUtf8("browseoutfile"))
        self.label3 = QLabel(coastalmeqgis_splitMI)
        self.label3.setGeometry(QtCore.QRect(10, 120, 291, 22))
        self.label3.setObjectName(_fromUtf8("label3"))
        self.outprefix = QLineEdit(coastalmeqgis_splitMI)
        self.outprefix.setGeometry(QtCore.QRect(10, 140, 261, 21))
        self.outprefix.setReadOnly(False)
        self.outprefix.setObjectName(_fromUtf8("outprefix"))

        self.retranslateUi(coastalmeqgis_splitMI)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_splitMI)

    def retranslateUi(self, coastalmeqgis_splitMI):
        coastalmeqgis_splitMI.setWindowTitle(_translate("coastalmeqgis_splitMI", "Split MI File Into Shapefile", None))
        self.label1.setText(_translate("coastalmeqgis_splitMI", "Source Layer", None))
        self.label2.setText(_translate("coastalmeqgis_splitMI", "Output Folder", None))
        self.outfolder.setText(_translate("coastalmeqgis_splitMI", "<folder>", None))
        self.browseoutfile.setText(_translate("coastalmeqgis_splitMI", "Browse...", None))
        self.label3.setText(_translate("coastalmeqgis_splitMI", "Output Prefix (_P.shp, _L.shp and _R.shp will be added)", None))
        self.outprefix.setText(_translate("coastalmeqgis_splitMI", "<prefix>", None))

