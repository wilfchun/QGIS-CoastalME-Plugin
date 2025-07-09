# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_line_from_points.ui'
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


class Ui_coastalmeqgis_line_from_point(object):
    def setupUi(self, coastalmeqgis_line_from_point):
        coastalmeqgis_line_from_point.setObjectName(_fromUtf8("coastalmeqgis_line_from_point"))
        coastalmeqgis_line_from_point.resize(400, 279)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_line_from_point)
        self.buttonBox.setGeometry(QtCore.QRect(130, 230, 151, 32))
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_1 = QLabel(coastalmeqgis_line_from_point)
        self.label_1.setGeometry(QtCore.QRect(12, 10, 108, 22))
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.sourcelayer = QComboBox(coastalmeqgis_line_from_point)
        self.sourcelayer.setGeometry(QtCore.QRect(10, 30, 351, 27))
        self.sourcelayer.setObjectName(_fromUtf8("sourcelayer"))
        self.label_4 = QLabel(coastalmeqgis_line_from_point)
        self.label_4.setGeometry(QtCore.QRect(12, 170, 108, 22))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.outfilename = QLineEdit(coastalmeqgis_line_from_point)
        self.outfilename.setGeometry(QtCore.QRect(10, 190, 261, 21))
        self.outfilename.setReadOnly(False)
        self.outfilename.setObjectName(_fromUtf8("outfilename"))
        self.browseoutfile = QPushButton(coastalmeqgis_line_from_point)
        self.browseoutfile.setGeometry(QtCore.QRect(300, 190, 79, 26))
        self.browseoutfile.setObjectName(_fromUtf8("browseoutfile"))
        self.label_2 = QLabel(coastalmeqgis_line_from_point)
        self.label_2.setGeometry(QtCore.QRect(12, 120, 351, 22))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.dmax = QLineEdit(coastalmeqgis_line_from_point)
        self.dmax.setGeometry(QtCore.QRect(10, 140, 171, 21))
        self.dmax.setReadOnly(False)
        self.dmax.setObjectName(_fromUtf8("dmax"))
        self.label_3 = QLabel(coastalmeqgis_line_from_point)
        self.label_3.setGeometry(QtCore.QRect(12, 60, 108, 22))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.elev_attr = QComboBox(coastalmeqgis_line_from_point)
        self.elev_attr.setGeometry(QtCore.QRect(10, 80, 351, 27))
        self.elev_attr.setObjectName(_fromUtf8("elev_attr"))

        self.retranslateUi(coastalmeqgis_line_from_point)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_line_from_point)

    def retranslateUi(self, coastalmeqgis_line_from_point):
        coastalmeqgis_line_from_point.setWindowTitle(_translate("coastalmeqgis_line_from_point", "Create Breakline from Points", None))
        self.label_1.setText(_translate("coastalmeqgis_line_from_point", "Source Point Layer", None))
        self.label_4.setText(_translate("coastalmeqgis_line_from_point", "Output File", None))
        self.outfilename.setText(_translate("coastalmeqgis_line_from_point", "<filename.shp>", None))
        self.browseoutfile.setText(_translate("coastalmeqgis_line_from_point", "Browse...", None))
        self.label_2.setText(_translate("coastalmeqgis_line_from_point", "Maximum Distance Between Points", None))
        self.dmax.setText(_translate("coastalmeqgis_line_from_point", "10", None))
        self.label_3.setText(_translate("coastalmeqgis_line_from_point", "Elevation Attribute", None))

