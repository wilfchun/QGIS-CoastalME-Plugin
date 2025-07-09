# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_splitMI_folder.ui'
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


class Ui_coastalmeqgis_splitMI_folder(object):
    def setupUi(self, coastalmeqgis_splitMI_folder):
        coastalmeqgis_splitMI_folder.setObjectName(_fromUtf8("coastalmeqgis_splitMI_folder"))
        coastalmeqgis_splitMI_folder.resize(402, 165)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_splitMI_folder)
        self.buttonBox.setGeometry(QtCore.QRect(100, 120, 171, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label2 = QLabel(coastalmeqgis_splitMI_folder)
        self.label2.setGeometry(QtCore.QRect(10, 20, 121, 22))
        self.label2.setObjectName(_fromUtf8("label2"))
        self.outfolder = QLineEdit(coastalmeqgis_splitMI_folder)
        self.outfolder.setGeometry(QtCore.QRect(10, 50, 261, 21))
        self.outfolder.setReadOnly(False)
        self.outfolder.setObjectName(_fromUtf8("outfolder"))
        self.browseoutfile = QPushButton(coastalmeqgis_splitMI_folder)
        self.browseoutfile.setGeometry(QtCore.QRect(290, 50, 81, 26))
        self.browseoutfile.setObjectName(_fromUtf8("browseoutfile"))
        self.cbRecursive = QCheckBox(coastalmeqgis_splitMI_folder)
        self.cbRecursive.setGeometry(QtCore.QRect(20, 90, 191, 17))
        self.cbRecursive.setObjectName(_fromUtf8("cbRecursive"))

        self.retranslateUi(coastalmeqgis_splitMI_folder)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_splitMI_folder)

    def retranslateUi(self, coastalmeqgis_splitMI_folder):
        coastalmeqgis_splitMI_folder.setWindowTitle(_translate("coastalmeqgis_splitMI_folder", "Convert MI Files in Folder to Shapefile", None))
        self.label2.setText(_translate("coastalmeqgis_splitMI_folder", "Input Folder", None))
        self.outfolder.setText(_translate("coastalmeqgis_splitMI_folder", "<folder>", None))
        self.browseoutfile.setText(_translate("coastalmeqgis_splitMI_folder", "Browse...", None))
        self.cbRecursive.setText(_translate("coastalmeqgis_splitMI_folder", "Search in subfolder", None))

