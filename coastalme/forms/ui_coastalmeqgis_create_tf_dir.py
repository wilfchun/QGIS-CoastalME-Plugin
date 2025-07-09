# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_create_tf_dir.ui'
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


class Ui_coastalmeqgis_create_tf_dir(object):
    def setupUi(self, coastalmeqgis_create_tf_dir):
        coastalmeqgis_create_tf_dir.setObjectName(_fromUtf8("coastalmeqgis_create_tf_dir"))
        coastalmeqgis_create_tf_dir.resize(397, 352)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_create_tf_dir)
        self.buttonBox.setGeometry(QtCore.QRect(120, 310, 161, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_1 = QLabel(coastalmeqgis_create_tf_dir)
        self.label_1.setGeometry(QtCore.QRect(12, 10, 121, 22))
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.sourcelayer = QComboBox(coastalmeqgis_create_tf_dir)
        self.sourcelayer.setGeometry(QtCore.QRect(10, 30, 351, 27))
        self.sourcelayer.setObjectName(_fromUtf8("sourcelayer"))
        self.label_3 = QLabel(coastalmeqgis_create_tf_dir)
        self.label_3.setGeometry(QtCore.QRect(10, 153, 108, 22))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.outdir = QLineEdit(coastalmeqgis_create_tf_dir)
        self.outdir.setGeometry(QtCore.QRect(10, 176, 261, 21))
        self.outdir.setReadOnly(False)
        self.outdir.setObjectName(_fromUtf8("outdir"))
        self.browseoutfile = QPushButton(coastalmeqgis_create_tf_dir)
        self.browseoutfile.setGeometry(QtCore.QRect(287, 174, 79, 26))
        self.browseoutfile.setObjectName(_fromUtf8("browseoutfile"))
        self.label_2 = QLabel(coastalmeqgis_create_tf_dir)
        self.label_2.setGeometry(QtCore.QRect(10, 85, 108, 22))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.sourceCRS = QLineEdit(coastalmeqgis_create_tf_dir)
        self.sourceCRS.setGeometry(QtCore.QRect(10, 110, 351, 21))
        self.sourceCRS.setReadOnly(False)
        self.sourceCRS.setObjectName(_fromUtf8("sourceCRS"))
        self.checkBox = QCheckBox(coastalmeqgis_create_tf_dir)
        self.checkBox.setGeometry(QtCore.QRect(20, 210, 251, 21))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.label_4 = QLabel(coastalmeqgis_create_tf_dir)
        self.label_4.setGeometry(QtCore.QRect(10, 240, 108, 22))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.COASTALME_exe = QLineEdit(coastalmeqgis_create_tf_dir)
        self.COASTALME_exe.setGeometry(QtCore.QRect(10, 260, 261, 21))
        self.COASTALME_exe.setReadOnly(False)
        self.COASTALME_exe.setObjectName(_fromUtf8("COASTALME_exe"))
        self.browseexe = QPushButton(coastalmeqgis_create_tf_dir)
        self.browseexe.setGeometry(QtCore.QRect(290, 259, 79, 26))
        self.browseexe.setObjectName(_fromUtf8("browseexe"))

        self.retranslateUi(coastalmeqgis_create_tf_dir)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), coastalmeqgis_create_tf_dir.accept)
        self.buttonBox.accepted.connect(coastalmeqgis_create_tf_dir.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), coastalmeqgis_create_tf_dir.reject)
        self.buttonBox.rejected.connect(coastalmeqgis_create_tf_dir.reject)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_create_tf_dir)

    def retranslateUi(self, coastalmeqgis_create_tf_dir):
        coastalmeqgis_create_tf_dir.setWindowTitle(_translate("coastalmeqgis_create_tf_dir", "Create COASTALME Directory Structure", None))
        self.label_1.setText(_translate("coastalmeqgis_create_tf_dir", "Source Projection Layer", None))
        self.label_3.setText(_translate("coastalmeqgis_create_tf_dir", "Output Directory", None))
        self.outdir.setText(_translate("coastalmeqgis_create_tf_dir", "<directory>", None))
        self.browseoutfile.setText(_translate("coastalmeqgis_create_tf_dir", "Browse...", None))
        self.label_2.setText(_translate("coastalmeqgis_create_tf_dir", "Source Projection", None))
        self.sourceCRS.setText(_translate("coastalmeqgis_create_tf_dir", "<projection>", None))
        self.checkBox.setText(_translate("coastalmeqgis_create_tf_dir", "Run COASTALME to create Empties (Windows Only)", None))
        self.label_4.setText(_translate("coastalmeqgis_create_tf_dir", "COASTALME executable", None))
        self.COASTALME_exe.setText(_translate("coastalmeqgis_create_tf_dir", "<COASTALME exe>", None))
        self.browseexe.setText(_translate("coastalmeqgis_create_tf_dir", "Browse...", None))

