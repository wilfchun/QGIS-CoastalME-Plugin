# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coastalmeqgis_import_check.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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


from ..compatibility_routines import QT_WINDOW_MODALITY_APPLICATION_MODAL, QT_BUTTON_BOX_CANCEL, QT_BUTTON_BOX_OK, QT_HORIZONTAL


class Ui_coastalmeqgis_import_check(object):
    def setupUi(self, coastalmeqgis_import_check):
        coastalmeqgis_import_check.setObjectName(_fromUtf8("coastalmeqgis_import_check"))
        coastalmeqgis_import_check.setWindowModality(QT_WINDOW_MODALITY_APPLICATION_MODAL)
        coastalmeqgis_import_check.setEnabled(True)
        coastalmeqgis_import_check.resize(388, 183)
        coastalmeqgis_import_check.setMouseTracking(False)
        self.gridLayout = QGridLayout(coastalmeqgis_import_check)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label1 = QLabel(coastalmeqgis_import_check)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.gridLayout.addWidget(self.label1, 0, 0, 1, 1)
        self.browsedir = QPushButton(coastalmeqgis_import_check)
        self.browsedir.setObjectName(_fromUtf8("browsedir"))
        self.gridLayout.addWidget(self.browsedir, 1, 0, 1, 1)
        self.emptydir = QLineEdit(coastalmeqgis_import_check)
        self.emptydir.setReadOnly(False)
        self.emptydir.setObjectName(_fromUtf8("emptydir"))
        self.gridLayout.addWidget(self.emptydir, 2, 0, 1, 1)
        self.label3 = QLabel(coastalmeqgis_import_check)
        self.label3.setObjectName(_fromUtf8("label3"))
        self.gridLayout.addWidget(self.label3, 3, 0, 1, 1)
        self.txtRunID = QLineEdit(coastalmeqgis_import_check)
        self.txtRunID.setReadOnly(False)
        self.txtRunID.setObjectName(_fromUtf8("txtRunID"))
        self.gridLayout.addWidget(self.txtRunID, 4, 0, 1, 1)
        self.showchecks = QRadioButton(coastalmeqgis_import_check)
        self.showchecks.setChecked(True)
        self.showchecks.setObjectName(_fromUtf8("showchecks"))
        self.gridLayout.addWidget(self.showchecks, 5, 0, 1, 1)
        self.buttonBox = QDialogButtonBox(coastalmeqgis_import_check)
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 1)

        self.retranslateUi(coastalmeqgis_import_check)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), coastalmeqgis_import_check.accept)
        self.buttonBox.accepted.connect(coastalmeqgis_import_check.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), coastalmeqgis_import_check.reject)
        self.buttonBox.rejected.connect(coastalmeqgis_import_check.reject)
        QtCore.QMetaObject.connectSlotsByName(coastalmeqgis_import_check)

    def retranslateUi(self, coastalmeqgis_import_check):
        coastalmeqgis_import_check.setWindowTitle(_translate("coastalmeqgis_import_check", "Import COASTALME Check File", None))
        self.label1.setText(_translate("coastalmeqgis_import_check", "Check Directory", None))
        self.browsedir.setText(_translate("coastalmeqgis_import_check", "Browse...", None))
        self.emptydir.setText(_translate("coastalmeqgis_import_check", "<directory>", None))
        self.label3.setText(_translate("coastalmeqgis_import_check", "Run ID", None))
        self.txtRunID.setText(_translate("coastalmeqgis_import_check", "RunID", None))
        self.showchecks.setText(_translate("coastalmeqgis_import_check", "Check Files Visible (uvpt, zpt and grd are always non-visible by default)", None))

