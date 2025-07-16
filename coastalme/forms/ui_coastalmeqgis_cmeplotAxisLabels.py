# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_cmeplotAxisLabels.ui'
#
# Created: Sun Jun 03 16:50:12 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtWidgets import *

try:
    _fromUcme8 = QtCore.QString.fromUcme8
except AttributeError:
    def _fromUcme8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


from ..compatibility_routines import QT_FRAME_VLINE, QT_ALIGN_V_CENTER, QT_ALIGN_TRAILING, QT_BUTTON_BOX_CANCEL, QT_ALIGN_RIGHT, QT_BUTTON_BOX_OK, QT_HORIZONTAL, QT_FRAME_SUNKEN


class Ui_cmeplotAxisLabel(object):
    def setupUi(self, cmeplotAxisLabel):
        cmeplotAxisLabel.setObjectName(_fromUcme8("cmeplotAxisLabel"))
        cmeplotAxisLabel.resize(337, 280)
        self.buttonBox = QDialogButtonBox(cmeplotAxisLabel)
        self.buttonBox.setGeometry(QtCore.QRect(170, 250, 161, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUcme8("buttonBox"))
        self.xAxisLabel = QLineEdit(cmeplotAxisLabel)
        self.xAxisLabel.setGeometry(QtCore.QRect(50, 82, 271, 20))
        self.xAxisLabel.setObjectName(_fromUcme8("xAxisLabel"))
        self.label = QLabel(cmeplotAxisLabel)
        self.label.setGeometry(QtCore.QRect(60, 64, 61, 16))
        self.label.setObjectName(_fromUcme8("label"))
        self.label_2 = QLabel(cmeplotAxisLabel)
        self.label_2.setGeometry(QtCore.QRect(60, 104, 61, 16))
        self.label_2.setObjectName(_fromUcme8("label_2"))
        self.yAxisLabel = QLineEdit(cmeplotAxisLabel)
        self.yAxisLabel.setGeometry(QtCore.QRect(50, 122, 271, 20))
        self.yAxisLabel.setObjectName(_fromUcme8("yAxisLabel"))
        self.label_3 = QLabel(cmeplotAxisLabel)
        self.label_3.setGeometry(QtCore.QRect(60, 161, 121, 16))
        self.label_3.setObjectName(_fromUcme8("label_3"))
        self.label_4 = QLabel(cmeplotAxisLabel)
        self.label_4.setGeometry(QtCore.QRect(60, 201, 121, 16))
        self.label_4.setObjectName(_fromUcme8("label_4"))
        self.xAxisLabel2 = QLineEdit(cmeplotAxisLabel)
        self.xAxisLabel2.setGeometry(QtCore.QRect(50, 179, 271, 20))
        self.xAxisLabel2.setObjectName(_fromUcme8("xAxisLabel2"))
        self.yAxisLabel2 = QLineEdit(cmeplotAxisLabel)
        self.yAxisLabel2.setGeometry(QtCore.QRect(50, 219, 271, 20))
        self.yAxisLabel2.setObjectName(_fromUcme8("yAxisLabel2"))
        self.chartTitle = QLineEdit(cmeplotAxisLabel)
        self.chartTitle.setGeometry(QtCore.QRect(50, 32, 271, 20))
        self.chartTitle.setObjectName(_fromUcme8("chartTitle"))
        self.label_5 = QLabel(cmeplotAxisLabel)
        self.label_5.setGeometry(QtCore.QRect(60, 14, 61, 16))
        self.label_5.setObjectName(_fromUcme8("label_5"))
        self.xAxisAuto_cb = QCheckBox(cmeplotAxisLabel)
        self.xAxisAuto_cb.setGeometry(QtCore.QRect(23, 83, 16, 17))
        self.xAxisAuto_cb.setText(_fromUcme8(""))
        self.xAxisAuto_cb.setObjectName(_fromUcme8("xAxisAuto_cb"))
        self.label_6 = QLabel(cmeplotAxisLabel)
        self.label_6.setGeometry(QtCore.QRect(2, 5, 40, 31))
        self.label_6.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName(_fromUcme8("label_6"))
        self.yAxisAuto_cb = QCheckBox(cmeplotAxisLabel)
        self.yAxisAuto_cb.setGeometry(QtCore.QRect(23, 123, 16, 17))
        self.yAxisAuto_cb.setText(_fromUcme8(""))
        self.yAxisAuto_cb.setObjectName(_fromUcme8("yAxisAuto_cb"))
        self.xAxisAuto2_cb = QCheckBox(cmeplotAxisLabel)
        self.xAxisAuto2_cb.setGeometry(QtCore.QRect(25, 180, 16, 17))
        self.xAxisAuto2_cb.setText(_fromUcme8(""))
        self.xAxisAuto2_cb.setObjectName(_fromUcme8("xAxisAuto2_cb"))
        self.yAxisAuto2_cb = QCheckBox(cmeplotAxisLabel)
        self.yAxisAuto2_cb.setGeometry(QtCore.QRect(25, 220, 16, 17))
        self.yAxisAuto2_cb.setText(_fromUcme8(""))
        self.yAxisAuto2_cb.setObjectName(_fromUcme8("yAxisAuto2_cb"))
        self.line = QFrame(cmeplotAxisLabel)
        self.line.setGeometry(QtCore.QRect(37, 5, 20, 271))
        self.line.setFrameShape(QT_FRAME_VLINE)
        self.line.setFrameShadow(QT_FRAME_SUNKEN)
        self.line.setObjectName(_fromUcme8("line"))

        self.retranslateUi(cmeplotAxisLabel)
        self.buttonBox.accepted.connect(cmeplotAxisLabel.accept)
        self.buttonBox.rejected.connect(cmeplotAxisLabel.reject)
        QtCore.QMetaObject.connectSlotsByName(cmeplotAxisLabel)

    def retranslateUi(self, cmeplotAxisLabel):
        cmeplotAxisLabel.setWindowTitle(_translate("cmeplotAxisLabel", "Cmeplot - Axis Labels", None))
        self.label.setText(_translate("cmeplotAxisLabel", "X Axis Label", None))
        self.label_2.setText(_translate("cmeplotAxisLabel", "Y Axis Label", None))
        self.label_3.setText(_translate("cmeplotAxisLabel", "Secondary X Axis Label", None))
        self.label_4.setText(_translate("cmeplotAxisLabel", "Secondary Y Axis Label", None))
        self.label_5.setText(_translate("cmeplotAxisLabel", "Chart Title", None))
        self.label_6.setText(_translate("cmeplotAxisLabel", "Use Custom", None))

