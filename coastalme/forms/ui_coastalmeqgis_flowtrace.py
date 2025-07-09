# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_flowtrace.ui'
#
# Created: Tue Jan 19 11:20:12 2016
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


class Ui_coastalmeqgis_flowtrace(object):
    def setupUi(self, coastalmeqgis_flowtrace):
        coastalmeqgis_flowtrace.setObjectName(_fromUtf8("coastalmeqgis_flowtrace"))
        coastalmeqgis_flowtrace.resize(400, 300)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_flowtrace)
        self.buttonBox.setGeometry(QtCore.QRect(100, 260, 171, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.cb_US = QCheckBox(coastalmeqgis_flowtrace)
        self.cb_US.setGeometry(QtCore.QRect(27, 27, 121, 17))
        self.cb_US.setChecked(True)
        self.cb_US.setObjectName(_fromUtf8("cb_US"))
        self.pb_Run = QPushButton(coastalmeqgis_flowtrace)
        self.pb_Run.setGeometry(QtCore.QRect(160, 230, 75, 23))
        self.pb_Run.setObjectName(_fromUtf8("pb_Run"))
        self.cb_DS = QCheckBox(coastalmeqgis_flowtrace)
        self.cb_DS.setGeometry(QtCore.QRect(220, 30, 121, 17))
        self.cb_DS.setChecked(True)
        self.cb_DS.setObjectName(_fromUtf8("cb_DS"))
        self.lw_Log = QListWidget(coastalmeqgis_flowtrace)
        self.lw_Log.setGeometry(QtCore.QRect(20, 90, 361, 131))
        self.lw_Log.setObjectName(_fromUtf8("lw_Log"))
        self.le_dt = QLineEdit(coastalmeqgis_flowtrace)
        self.le_dt.setGeometry(QtCore.QRect(20, 60, 113, 20))
        self.le_dt.setObjectName(_fromUtf8("le_dt"))
        self.label = QLabel(coastalmeqgis_flowtrace)
        self.label.setGeometry(QtCore.QRect(140, 60, 141, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(coastalmeqgis_flowtrace)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_flowtrace)

    def retranslateUi(self, coastalmeqgis_flowtrace):
        coastalmeqgis_flowtrace.setWindowTitle(_translate("coastalmeqgis_flowtrace", "Trace Connectivity", None))
        self.cb_US.setText(_translate("coastalmeqgis_flowtrace", "Search upstream", None))
        self.pb_Run.setText(_translate("coastalmeqgis_flowtrace", "Run", None))
        self.cb_DS.setText(_translate("coastalmeqgis_flowtrace", "Search downstream", None))
        self.le_dt.setText(_translate("coastalmeqgis_flowtrace", "1.0", None))
        self.label.setText(_translate("coastalmeqgis_flowtrace", "Snap Tolerance (map units)", None))

