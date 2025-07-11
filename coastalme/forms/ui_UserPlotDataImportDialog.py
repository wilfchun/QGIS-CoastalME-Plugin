# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\esymons\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\coastalme\forms\ui_UserPlotDataImportDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtGui, QtWidgets


from ..compatibility_routines import QT_ALIGN_V_CENTER, QT_ALIGN_TRAILING, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_FIXED, QT_ALIGN_RIGHT, QT_SIZE_POLICY_MINIMUM


class Ui_UserPlotDataImportDialog(object):
    def setupUi(self, UserPlotDataImportDialog):
        UserPlotDataImportDialog.setObjectName("UserPlotDataImportDialog")
        UserPlotDataImportDialog.resize(684, 579)
        self.gridLayout_2 = QtWidgets.QGridLayout(UserPlotDataImportDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(UserPlotDataImportDialog)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.btnBrowse = QtWidgets.QToolButton(UserPlotDataImportDialog)
        self.btnBrowse.setObjectName("btnBrowse")
        self.horizontalLayout_5.addWidget(self.btnBrowse)
        self.inFile = QtWidgets.QLineEdit(UserPlotDataImportDialog)
        self.inFile.setObjectName("inFile")
        self.horizontalLayout_5.addWidget(self.inFile)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.grouBox = QtWidgets.QGroupBox(UserPlotDataImportDialog)
        self.grouBox.setMinimumSize(QtCore.QSize(0, 0))
        self.grouBox.setObjectName("grouBox")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.grouBox)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.rbCSV = QtWidgets.QRadioButton(self.grouBox)
        self.rbCSV.setChecked(True)
        self.rbCSV.setObjectName("rbCSV")
        self.bgDelimiter = QtWidgets.QButtonGroup(UserPlotDataImportDialog)
        self.bgDelimiter.setObjectName("bgDelimiter")
        self.bgDelimiter.addButton(self.rbCSV)
        self.horizontalLayout_6.addWidget(self.rbCSV)
        self.rbSpace = QtWidgets.QRadioButton(self.grouBox)
        self.rbSpace.setObjectName("rbSpace")
        self.bgDelimiter.addButton(self.rbSpace)
        self.horizontalLayout_6.addWidget(self.rbSpace)
        self.rbTab = QtWidgets.QRadioButton(self.grouBox)
        self.rbTab.setObjectName("rbTab")
        self.bgDelimiter.addButton(self.rbTab)
        self.horizontalLayout_6.addWidget(self.rbTab)
        self.rbOther = QtWidgets.QRadioButton(self.grouBox)
        self.rbOther.setObjectName("rbOther")
        self.bgDelimiter.addButton(self.rbOther)
        self.horizontalLayout_6.addWidget(self.rbOther)
        self.delimiter = QtWidgets.QLineEdit(self.grouBox)
        self.delimiter.setObjectName("delimiter")
        self.horizontalLayout_6.addWidget(self.delimiter)
        self.verticalLayout_2.addWidget(self.grouBox)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MINIMUM)
        self.verticalLayout_2.addItem(spacerItem)
        self.label_8 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_2.addWidget(self.label_8)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_6 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.sbLines2Discard = QtWidgets.QSpinBox(UserPlotDataImportDialog)
        self.sbLines2Discard.setMinimumSize(QtCore.QSize(50, 0))
        self.sbLines2Discard.setProperty("value", 1)
        self.sbLines2Discard.setObjectName("sbLines2Discard")
        self.horizontalLayout.addWidget(self.sbLines2Discard)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cbHeadersAsLabels = QtWidgets.QCheckBox(UserPlotDataImportDialog)
        self.cbHeadersAsLabels.setChecked(True)
        self.cbHeadersAsLabels.setObjectName("cbHeadersAsLabels")
        self.horizontalLayout_2.addWidget(self.cbHeadersAsLabels)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QT_SIZE_POLICY_FIXED, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.label_7 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_7.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.sbLabelRow = QtWidgets.QSpinBox(UserPlotDataImportDialog)
        self.sbLabelRow.setMinimumSize(QtCore.QSize(50, 0))
        self.sbLabelRow.setMinimum(1)
        self.sbLabelRow.setProperty("value", 1)
        self.sbLabelRow.setObjectName("sbLabelRow")
        self.horizontalLayout_2.addWidget(self.sbLabelRow)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 15, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MINIMUM)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_2.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.cbXColumn = QtWidgets.QComboBox(UserPlotDataImportDialog)
        self.cbXColumn.setMinimumSize(QtCore.QSize(125, 0))
        self.cbXColumn.setEditable(True)
        self.cbXColumn.setObjectName("cbXColumn")
        self.horizontalLayout_3.addWidget(self.cbXColumn)
        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QT_SIZE_POLICY_FIXED, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.label_4 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_4.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.mcbYColumn = TableCheckableComboBox(UserPlotDataImportDialog)
        self.mcbYColumn.setMinimumSize(QtCore.QSize(125, 0))
        self.mcbYColumn.setEditable(True)
        self.mcbYColumn.setObjectName("mcbYColumn")
        self.horizontalLayout_3.addWidget(self.mcbYColumn)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.nullValue = QtWidgets.QLineEdit(UserPlotDataImportDialog)
        self.nullValue.setObjectName("nullValue")
        self.horizontalLayout_4.addWidget(self.nullValue)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        spacerItem8 = QtWidgets.QSpacerItem(20, 15, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_MINIMUM)
        self.verticalLayout_2.addItem(spacerItem8)
        self.gbUseDates = QgsCollapsibleGroupBox(UserPlotDataImportDialog)
        self.gbUseDates.setMinimumSize(QtCore.QSize(0, 0))
        self.gbUseDates.setFlat(True)
        self.gbUseDates.setCheckable(True)
        self.gbUseDates.setChecked(False)
        self.gbUseDates.setCollapsed(False)
        self.gbUseDates.setSaveCollapsedState(False)
        self.gbUseDates.setObjectName("gbUseDates")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.gbUseDates)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.cbUSDateFormat = QtWidgets.QCheckBox(self.gbUseDates)
        self.cbUSDateFormat.setObjectName("cbUSDateFormat")
        self.horizontalLayout_7.addWidget(self.cbUSDateFormat)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.cbManualZeroTime = QtWidgets.QCheckBox(self.gbUseDates)
        self.cbManualZeroTime.setObjectName("cbManualZeroTime")
        self.horizontalLayout_9.addWidget(self.cbManualZeroTime)
        self.dteZeroTime = QtWidgets.QDateTimeEdit(self.gbUseDates)
        self.dteZeroTime.setCalendarPopup(True)
        self.dteZeroTime.setObjectName("dteZeroTime")
        self.horizontalLayout_9.addWidget(self.dteZeroTime)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.verticalLayout_2.addWidget(self.gbUseDates)
        self.label_5 = QtWidgets.QLabel(UserPlotDataImportDialog)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.previewTable = QtWidgets.QTableWidget(UserPlotDataImportDialog)
        self.previewTable.setObjectName("previewTable")
        self.previewTable.setColumnCount(0)
        self.previewTable.setRowCount(0)
        self.previewTable.horizontalHeader().setVisible(True)
        self.verticalLayout_2.addWidget(self.previewTable)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout_8.addItem(spacerItem9)
        self.pbOk = QtWidgets.QPushButton(UserPlotDataImportDialog)
        self.pbOk.setObjectName("pbOk")
        self.horizontalLayout_8.addWidget(self.pbOk)
        self.pbCancel = QtWidgets.QPushButton(UserPlotDataImportDialog)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout_8.addWidget(self.pbCancel)
        self.gridLayout_2.addLayout(self.horizontalLayout_8, 1, 0, 1, 2)
        self.gridLayout_2.setColumnStretch(0, 10)

        self.retranslateUi(UserPlotDataImportDialog)
        QtCore.QMetaObject.connectSlotsByName(UserPlotDataImportDialog)

    def retranslateUi(self, UserPlotDataImportDialog):
        _translate = QtCore.QCoreApplication.translate
        UserPlotDataImportDialog.setWindowTitle(_translate("UserPlotDataImportDialog", "Import User Plot Data . . ."))
        self.textBrowser.setHtml(_translate("UserPlotDataImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">ToolTip</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Converts a delimited text file (e.g. *.csv) into X, Y data to be plotted in COASTALME Viewer.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Delimeter File:</span> file containing plot data</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Delimited Format: </span>Character delimiting data</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Number of Header Lines to Discard: </span>The number of rows at the top of file to ignore</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">User Header Line as Data Labels: </span>Uses row values as labels for data series- can be changed later.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">X Column: </span>Column containing X-Values</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Y Column: </span>Column containing Y-Values- can be multiple</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Null Value: </span>Value to be treated as null when plotting- blank values will always be treated as null</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">US date format: </span>If date format is in ambiguous 3 integer format e.g. 03/05/2000 the tool will assume day/month/year unless this check box is ticked and then it will assume month/day/year</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Manually Specify Zero Date Time: </span>Date for zero hour, if none specified will use first value.</p></body></html>"))
        self.label.setText(_translate("UserPlotDataImportDialog", "Delimited File"))
        self.btnBrowse.setText(_translate("UserPlotDataImportDialog", "..."))
        self.grouBox.setTitle(_translate("UserPlotDataImportDialog", "Delimited Format"))
        self.rbCSV.setText(_translate("UserPlotDataImportDialog", "CSV"))
        self.rbSpace.setText(_translate("UserPlotDataImportDialog", "Space"))
        self.rbTab.setText(_translate("UserPlotDataImportDialog", "Tab"))
        self.rbOther.setText(_translate("UserPlotDataImportDialog", "Other:"))
        self.label_8.setText(_translate("UserPlotDataImportDialog", "Header Rows"))
        self.label_6.setText(_translate("UserPlotDataImportDialog", "Number of Header Lines to Discard:"))
        self.cbHeadersAsLabels.setText(_translate("UserPlotDataImportDialog", "Use Header Line as Data Labels"))
        self.label_7.setText(_translate("UserPlotDataImportDialog", "Use Row:"))
        self.label_2.setText(_translate("UserPlotDataImportDialog", "X Column:"))
        self.label_4.setText(_translate("UserPlotDataImportDialog", "Y Column:"))
        self.label_3.setText(_translate("UserPlotDataImportDialog", "Null Value (optional)"))
        self.gbUseDates.setTitle(_translate("UserPlotDataImportDialog", "Convert From Date Format (only required if importing time as dates)"))
        self.cbUSDateFormat.setText(_translate("UserPlotDataImportDialog", "US date format i.e. uses month/day/year if ambiguous 3 integer date"))
        self.cbManualZeroTime.setText(_translate("UserPlotDataImportDialog", "Manually Specify Zero Date Time"))
        self.label_5.setText(_translate("UserPlotDataImportDialog", "Preview (First 10 Rows):"))
        self.pbOk.setText(_translate("UserPlotDataImportDialog", "OK"))
        self.pbCancel.setText(_translate("UserPlotDataImportDialog", "Cancel"))

from qgscollapsiblegroupbox import QgsCollapsibleGroupBox
from ..DataTable import TableCheckableComboBox
