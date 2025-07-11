# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\esymons\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\coastalme\forms\MapExportImportDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtGui, QtWidgets


from ..compatibility_routines import QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MAXIMUM


class Ui_MapExportImportDialog(object):
    def setupUi(self, MapExportImportDialog):
        MapExportImportDialog.setObjectName("MapExportImportDialog")
        MapExportImportDialog.resize(598, 566)
        self.gridLayout_2 = QtWidgets.QGridLayout(MapExportImportDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.previewTable = QtWidgets.QTableWidget(MapExportImportDialog)
        self.previewTable.setWordWrap(False)
        self.previewTable.setObjectName("previewTable")
        self.previewTable.setColumnCount(0)
        self.previewTable.setRowCount(0)
        self.previewTable.horizontalHeader().setVisible(True)
        self.previewTable.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.previewTable, 14, 0, 1, 5)
        spacerItem = QtWidgets.QSpacerItem(20, 15, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MINIMUM)
        self.gridLayout.addItem(spacerItem, 12, 0, 1, 5)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MINIMUM)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 5)
        self.btnBrowse = QtWidgets.QToolButton(MapExportImportDialog)
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridLayout.addWidget(self.btnBrowse, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(MapExportImportDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 5)
        self.label_5 = QtWidgets.QLabel(MapExportImportDialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 13, 0, 1, 5)
        self.label_8 = QtWidgets.QLabel(MapExportImportDialog)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 4, 0, 1, 5)
        spacerItem2 = QtWidgets.QSpacerItem(20, 15, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MINIMUM)
        self.gridLayout.addItem(spacerItem2, 6, 0, 1, 5)
        self.inFile = QtWidgets.QLineEdit(MapExportImportDialog)
        self.inFile.setObjectName("inFile")
        self.gridLayout.addWidget(self.inFile, 1, 1, 1, 4)
        self.grouBox = QtWidgets.QGroupBox(MapExportImportDialog)
        self.grouBox.setMinimumSize(QtCore.QSize(0, 0))
        self.grouBox.setObjectName("grouBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.grouBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.rbOther = QtWidgets.QRadioButton(self.grouBox)
        self.rbOther.setObjectName("rbOther")
        self.bgDelimiter = QtWidgets.QButtonGroup(MapExportImportDialog)
        self.bgDelimiter.setObjectName("bgDelimiter")
        self.bgDelimiter.addButton(self.rbOther)
        self.gridLayout_3.addWidget(self.rbOther, 0, 3, 1, 1)
        self.rbTab = QtWidgets.QRadioButton(self.grouBox)
        self.rbTab.setObjectName("rbTab")
        self.bgDelimiter.addButton(self.rbTab)
        self.gridLayout_3.addWidget(self.rbTab, 0, 2, 1, 1)
        self.rbSpace = QtWidgets.QRadioButton(self.grouBox)
        self.rbSpace.setObjectName("rbSpace")
        self.bgDelimiter.addButton(self.rbSpace)
        self.gridLayout_3.addWidget(self.rbSpace, 0, 1, 1, 1)
        self.rbCSV = QtWidgets.QRadioButton(self.grouBox)
        self.rbCSV.setChecked(True)
        self.rbCSV.setObjectName("rbCSV")
        self.bgDelimiter.addButton(self.rbCSV)
        self.gridLayout_3.addWidget(self.rbCSV, 0, 0, 1, 1)
        self.delimiter = QtWidgets.QLineEdit(self.grouBox)
        self.delimiter.setObjectName("delimiter")
        self.gridLayout_3.addWidget(self.delimiter, 0, 4, 1, 1)
        self.gridLayout.addWidget(self.grouBox, 2, 0, 1, 5)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelCol1 = QtWidgets.QLabel(MapExportImportDialog)
        self.labelCol1.setObjectName("labelCol1")
        self.horizontalLayout_2.addWidget(self.labelCol1)
        spacerItem3 = QtWidgets.QSpacerItem(0, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.cboCol1 = QtWidgets.QComboBox(MapExportImportDialog)
        self.cboCol1.setMinimumSize(QtCore.QSize(200, 0))
        self.cboCol1.setEditable(True)
        self.cboCol1.setObjectName("cboCol1")
        self.horizontalLayout_2.addWidget(self.cboCol1)
        spacerItem4 = QtWidgets.QSpacerItem(100, 20, QT_SIZE_POLICY_MAXIMUM, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.gridLayout.addLayout(self.horizontalLayout_2, 7, 0, 1, 5)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelCol2 = QtWidgets.QLabel(MapExportImportDialog)
        self.labelCol2.setObjectName("labelCol2")
        self.horizontalLayout_3.addWidget(self.labelCol2)
        spacerItem5 = QtWidgets.QSpacerItem(0, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.cboCol2 = QtWidgets.QComboBox(MapExportImportDialog)
        self.cboCol2.setMinimumSize(QtCore.QSize(200, 0))
        self.cboCol2.setEditable(True)
        self.cboCol2.setObjectName("cboCol2")
        self.horizontalLayout_3.addWidget(self.cboCol2)
        spacerItem6 = QtWidgets.QSpacerItem(100, 20, QT_SIZE_POLICY_MAXIMUM, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.gridLayout.addLayout(self.horizontalLayout_3, 8, 0, 1, 5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.labelCol3 = QtWidgets.QLabel(MapExportImportDialog)
        self.labelCol3.setObjectName("labelCol3")
        self.horizontalLayout_4.addWidget(self.labelCol3)
        spacerItem7 = QtWidgets.QSpacerItem(0, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.cboCol3 = QtWidgets.QComboBox(MapExportImportDialog)
        self.cboCol3.setMinimumSize(QtCore.QSize(200, 0))
        self.cboCol3.setEditable(True)
        self.cboCol3.setObjectName("cboCol3")
        self.horizontalLayout_4.addWidget(self.cboCol3)
        spacerItem8 = QtWidgets.QSpacerItem(100, 20, QT_SIZE_POLICY_MAXIMUM, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_4.addItem(spacerItem8)
        self.gridLayout.addLayout(self.horizontalLayout_4, 9, 0, 1, 5)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.labelCol4 = QtWidgets.QLabel(MapExportImportDialog)
        self.labelCol4.setObjectName("labelCol4")
        self.horizontalLayout_5.addWidget(self.labelCol4)
        spacerItem9 = QtWidgets.QSpacerItem(0, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_5.addItem(spacerItem9)
        self.cboCol4 = QtWidgets.QComboBox(MapExportImportDialog)
        self.cboCol4.setMinimumSize(QtCore.QSize(200, 0))
        self.cboCol4.setEditable(True)
        self.cboCol4.setObjectName("cboCol4")
        self.horizontalLayout_5.addWidget(self.cboCol4)
        spacerItem10 = QtWidgets.QSpacerItem(100, 20, QT_SIZE_POLICY_MAXIMUM, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_5.addItem(spacerItem10)
        self.gridLayout.addLayout(self.horizontalLayout_5, 10, 0, 1, 5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(MapExportImportDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        spacerItem11 = QtWidgets.QSpacerItem(0, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_6.addItem(spacerItem11)
        self.cboCol5 = QtWidgets.QComboBox(MapExportImportDialog)
        self.cboCol5.setMinimumSize(QtCore.QSize(200, 0))
        self.cboCol5.setEditable(True)
        self.cboCol5.setObjectName("cboCol5")
        self.horizontalLayout_6.addWidget(self.cboCol5)
        spacerItem12 = QtWidgets.QSpacerItem(100, 20, QT_SIZE_POLICY_MAXIMUM, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_6.addItem(spacerItem12)
        self.gridLayout.addLayout(self.horizontalLayout_6, 11, 0, 1, 5)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_6 = QtWidgets.QLabel(MapExportImportDialog)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_7.addWidget(self.label_6)
        self.sbLines2Discard = QtWidgets.QSpinBox(MapExportImportDialog)
        self.sbLines2Discard.setMinimumSize(QtCore.QSize(50, 0))
        self.sbLines2Discard.setProperty("value", 1)
        self.sbLines2Discard.setObjectName("sbLines2Discard")
        self.horizontalLayout_7.addWidget(self.sbLines2Discard)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_7.addItem(spacerItem13)
        self.gridLayout.addLayout(self.horizontalLayout_7, 5, 0, 1, 5)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout.addItem(spacerItem14)
        self.pbOk = QtWidgets.QPushButton(MapExportImportDialog)
        self.pbOk.setObjectName("pbOk")
        self.horizontalLayout.addWidget(self.pbOk)
        self.pbCancel = QtWidgets.QPushButton(MapExportImportDialog)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout.addWidget(self.pbCancel)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 10)

        self.retranslateUi(MapExportImportDialog)
        QtCore.QMetaObject.connectSlotsByName(MapExportImportDialog)

    def retranslateUi(self, MapExportImportDialog):
        _translate = QtCore.QCoreApplication.translate
        MapExportImportDialog.setWindowTitle(_translate("MapExportImportDialog", "Import Map Export Data . . ."))
        self.btnBrowse.setText(_translate("MapExportImportDialog", "..."))
        self.label.setText(_translate("MapExportImportDialog", "Delimited File"))
        self.label_5.setText(_translate("MapExportImportDialog", "Preview (first 10 rows):"))
        self.label_8.setText(_translate("MapExportImportDialog", "Header Rows"))
        self.grouBox.setTitle(_translate("MapExportImportDialog", "Delimited Format"))
        self.rbOther.setText(_translate("MapExportImportDialog", "Other:"))
        self.rbTab.setText(_translate("MapExportImportDialog", "Tab"))
        self.rbSpace.setText(_translate("MapExportImportDialog", "Space"))
        self.rbCSV.setText(_translate("MapExportImportDialog", "CSV"))
        self.labelCol1.setText(_translate("MapExportImportDialog", "Column 1 (Result) - optional"))
        self.labelCol2.setText(_translate("MapExportImportDialog", "Column 2 (Scalar Type) - optional"))
        self.labelCol3.setText(_translate("MapExportImportDialog", "Column 3 (Vector Type) - optional"))
        self.labelCol4.setText(_translate("MapExportImportDialog", "Column 4 (Time) - optional"))
        self.label_3.setText(_translate("MapExportImportDialog", "Column 5 (Output) - optional"))
        self.label_6.setText(_translate("MapExportImportDialog", "Number of Header Lines to Discard:"))
        self.pbOk.setText(_translate("MapExportImportDialog", "OK"))
        self.pbCancel.setText(_translate("MapExportImportDialog", "Cancel"))

