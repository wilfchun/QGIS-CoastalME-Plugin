# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\esymons\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\coastalme\forms\animation_plot_properties.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtGui, QtWidgets


from ..compatibility_routines import QT_ALIGN_V_CENTER, QT_ALIGN_TRAILING, QT_BUTTON_BOX_CANCEL, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_FIXED, QT_ALIGN_RIGHT, QT_SIZE_POLICY_MINIMUM, QT_BUTTON_BOX_OK, QT_HORIZONTAL


class Ui_PlotProperties(object):
    def setupUi(self, PlotProperties):
        PlotProperties.setObjectName("PlotProperties")
        PlotProperties.resize(652, 426)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(PlotProperties)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_18 = QtWidgets.QLabel(PlotProperties)
        self.label_18.setObjectName("label_18")
        self.gridLayout.addWidget(self.label_18, 6, 0, 1, 1)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_19 = QtWidgets.QLabel(PlotProperties)
        self.label_19.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_19.setObjectName("label_19")
        self.gridLayout_6.addWidget(self.label_19, 0, 0, 1, 1)
        self.sbX2Max = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbX2Max.setMinimum(-9999999.0)
        self.sbX2Max.setMaximum(9999999.0)
        self.sbX2Max.setObjectName("sbX2Max")
        self.gridLayout_6.addWidget(self.sbX2Max, 0, 3, 1, 1)
        self.label_20 = QtWidgets.QLabel(PlotProperties)
        self.label_20.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_20.setObjectName("label_20")
        self.gridLayout_6.addWidget(self.label_20, 0, 2, 1, 1)
        self.pbAutoCalcX2Lim = QtWidgets.QPushButton(PlotProperties)
        self.pbAutoCalcX2Lim.setObjectName("pbAutoCalcX2Lim")
        self.gridLayout_6.addWidget(self.pbAutoCalcX2Lim, 0, 4, 1, 1)
        self.sbX2min = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbX2min.setMaximum(9999999.0)
        self.sbX2min.setProperty("value", 0.0)
        self.sbX2min.setObjectName("sbX2min")
        self.gridLayout_6.addWidget(self.sbX2min, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_6, 6, 1, 1, 1)
        self.cboLegendPos = QtWidgets.QComboBox(PlotProperties)
        self.cboLegendPos.setObjectName("cboLegendPos")
        self.cboLegendPos.addItem("")
        self.cboLegendPos.addItem("")
        self.cboLegendPos.addItem("")
        self.cboLegendPos.addItem("")
        self.gridLayout.addWidget(self.cboLegendPos, 10, 1, 1, 1)
        self.cbGridX = QtWidgets.QCheckBox(PlotProperties)
        self.cbGridX.setChecked(True)
        self.cbGridX.setObjectName("cbGridX")
        self.gridLayout.addWidget(self.cbGridX, 11, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(PlotProperties)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.leXLabel = QtWidgets.QLineEdit(PlotProperties)
        self.leXLabel.setObjectName("leXLabel")
        self.gridLayout.addWidget(self.leXLabel, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(PlotProperties)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.leYLabel = QtWidgets.QLineEdit(PlotProperties)
        self.leYLabel.setObjectName("leYLabel")
        self.gridLayout.addWidget(self.leYLabel, 3, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(PlotProperties)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 12, 0, 1, 1)
        self.horizontalWidget = QtWidgets.QWidget(PlotProperties)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sbXAxisRotation = QtWidgets.QSpinBox(self.horizontalWidget)
        self.sbXAxisRotation.setMaximum(359)
        self.sbXAxisRotation.setObjectName("sbXAxisRotation")
        self.horizontalLayout.addWidget(self.sbXAxisRotation)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addWidget(self.horizontalWidget, 7, 1, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(75, 20, QT_SIZE_POLICY_FIXED, QT_SIZE_POLICY_MINIMUM)
        self.gridLayout_4.addItem(spacerItem1, 0, 4, 1, 1)
        self.sbFigSizeX = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbFigSizeX.setDecimals(2)
        self.sbFigSizeX.setMaximum(9999999.0)
        self.sbFigSizeX.setProperty("value", 100.0)
        self.sbFigSizeX.setObjectName("sbFigSizeX")
        self.gridLayout_4.addWidget(self.sbFigSizeX, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(PlotProperties)
        self.label_12.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 0, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(PlotProperties)
        self.label_11.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 0, 0, 1, 1)
        self.sbFigSizeY = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbFigSizeY.setMaximum(9999999.0)
        self.sbFigSizeY.setProperty("value", 100.0)
        self.sbFigSizeY.setObjectName("sbFigSizeY")
        self.gridLayout_4.addWidget(self.sbFigSizeY, 0, 3, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_4, 12, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(PlotProperties)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 8, 0, 1, 1)
        self.label = QtWidgets.QLabel(PlotProperties)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_5 = QtWidgets.QLabel(PlotProperties)
        self.label_5.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)
        self.pbAutoCalcXLim = QtWidgets.QPushButton(PlotProperties)
        self.pbAutoCalcXLim.setObjectName("pbAutoCalcXLim")
        self.gridLayout_2.addWidget(self.pbAutoCalcXLim, 0, 6, 1, 1)
        self.sbXMax = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbXMax.setDecimals(2)
        self.sbXMax.setMinimum(-9999999.0)
        self.sbXMax.setMaximum(9999999.0)
        self.sbXMax.setObjectName("sbXMax")
        self.gridLayout_2.addWidget(self.sbXMax, 0, 4, 1, 1)
        self.label_6 = QtWidgets.QLabel(PlotProperties)
        self.label_6.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 3, 1, 1)
        self.sbXmin = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbXmin.setDecimals(2)
        self.sbXmin.setMinimum(-9999999.0)
        self.sbXmin.setMaximum(9999999.0)
        self.sbXmin.setObjectName("sbXmin")
        self.gridLayout_2.addWidget(self.sbXmin, 0, 1, 1, 1)
        self.dteXmin = QtWidgets.QDateTimeEdit(PlotProperties)
        self.dteXmin.setObjectName("dteXmin")
        self.gridLayout_2.addWidget(self.dteXmin, 0, 2, 1, 1)
        self.dteXMax = QtWidgets.QDateTimeEdit(PlotProperties)
        self.dteXMax.setObjectName("dteXMax")
        self.gridLayout_2.addWidget(self.dteXMax, 0, 5, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 5, 1, 1, 1)
        self.leTitle = QtWidgets.QLineEdit(PlotProperties)
        self.leTitle.setObjectName("leTitle")
        self.gridLayout.addWidget(self.leTitle, 0, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_EXPANDING)
        self.gridLayout.addItem(spacerItem2, 13, 0, 1, 1)
        self.cbGridY = QtWidgets.QCheckBox(PlotProperties)
        self.cbGridY.setChecked(True)
        self.cbGridY.setObjectName("cbGridY")
        self.gridLayout.addWidget(self.cbGridY, 11, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(PlotProperties)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 4, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(PlotProperties)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(PlotProperties)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 9, 0, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_16 = QtWidgets.QLabel(PlotProperties)
        self.label_16.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_16.setObjectName("label_16")
        self.gridLayout_5.addWidget(self.label_16, 0, 2, 1, 1)
        self.pbAutoCalcY2Lim = QtWidgets.QPushButton(PlotProperties)
        self.pbAutoCalcY2Lim.setObjectName("pbAutoCalcY2Lim")
        self.gridLayout_5.addWidget(self.pbAutoCalcY2Lim, 0, 4, 1, 1)
        self.label_15 = QtWidgets.QLabel(PlotProperties)
        self.label_15.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_15.setObjectName("label_15")
        self.gridLayout_5.addWidget(self.label_15, 0, 0, 1, 1)
        self.sbY2Max = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbY2Max.setDecimals(2)
        self.sbY2Max.setMinimum(-9999999.0)
        self.sbY2Max.setMaximum(9999999.0)
        self.sbY2Max.setObjectName("sbY2Max")
        self.gridLayout_5.addWidget(self.sbY2Max, 0, 3, 1, 1)
        self.sbY2Min = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbY2Min.setDecimals(2)
        self.sbY2Min.setMinimum(-9999999.0)
        self.sbY2Min.setMaximum(9999999.0)
        self.sbY2Min.setObjectName("sbY2Min")
        self.gridLayout_5.addWidget(self.sbY2Min, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_5, 9, 1, 1, 1)
        self.leY2Label = QtWidgets.QLineEdit(PlotProperties)
        self.leY2Label.setObjectName("leY2Label")
        self.gridLayout.addWidget(self.leY2Label, 4, 1, 1, 1)
        self.label_17 = QtWidgets.QLabel(PlotProperties)
        self.label_17.setObjectName("label_17")
        self.gridLayout.addWidget(self.label_17, 7, 0, 1, 1)
        self.cbLegend = QtWidgets.QCheckBox(PlotProperties)
        self.cbLegend.setObjectName("cbLegend")
        self.gridLayout.addWidget(self.cbLegend, 10, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_9 = QtWidgets.QLabel(PlotProperties)
        self.label_9.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 0, 2, 1, 1)
        self.pbAutoCalcYLim = QtWidgets.QPushButton(PlotProperties)
        self.pbAutoCalcYLim.setObjectName("pbAutoCalcYLim")
        self.gridLayout_3.addWidget(self.pbAutoCalcYLim, 0, 4, 1, 1)
        self.sbYMax = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbYMax.setDecimals(2)
        self.sbYMax.setMinimum(-9999999.0)
        self.sbYMax.setMaximum(9999999.0)
        self.sbYMax.setObjectName("sbYMax")
        self.gridLayout_3.addWidget(self.sbYMax, 0, 3, 1, 1)
        self.sbYMin = QtWidgets.QDoubleSpinBox(PlotProperties)
        self.sbYMin.setDecimals(2)
        self.sbYMin.setMinimum(-9999999.0)
        self.sbYMin.setMaximum(9999999.0)
        self.sbYMin.setObjectName("sbYMin")
        self.gridLayout_3.addWidget(self.sbYMin, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(PlotProperties)
        self.label_8.setAlignment(QT_ALIGN_RIGHT|QT_ALIGN_TRAILING|QT_ALIGN_V_CENTER)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 8, 1, 1, 1)
        self.label_21 = QtWidgets.QLabel(PlotProperties)
        self.label_21.setObjectName("label_21")
        self.gridLayout.addWidget(self.label_21, 2, 0, 1, 1)
        self.leX2Label = QtWidgets.QLineEdit(PlotProperties)
        self.leX2Label.setObjectName("leX2Label")
        self.gridLayout.addWidget(self.leX2Label, 2, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(PlotProperties)
        self.buttonBox.setOrientation(QT_HORIZONTAL)
        self.buttonBox.setStandardButtons(QT_BUTTON_BOX_CANCEL|QT_BUTTON_BOX_OK)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.setStretch(0, 10)
        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(PlotProperties)
        self.buttonBox.accepted.connect(PlotProperties.accept)
        self.buttonBox.rejected.connect(PlotProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(PlotProperties)
        PlotProperties.setTabOrder(self.leTitle, self.leXLabel)
        PlotProperties.setTabOrder(self.leXLabel, self.leYLabel)
        PlotProperties.setTabOrder(self.leYLabel, self.leY2Label)
        PlotProperties.setTabOrder(self.leY2Label, self.sbXmin)
        PlotProperties.setTabOrder(self.sbXmin, self.sbXMax)
        PlotProperties.setTabOrder(self.sbXMax, self.sbYMin)
        PlotProperties.setTabOrder(self.sbYMin, self.sbYMax)
        PlotProperties.setTabOrder(self.sbYMax, self.sbY2Min)
        PlotProperties.setTabOrder(self.sbY2Min, self.sbY2Max)
        PlotProperties.setTabOrder(self.sbY2Max, self.cboLegendPos)
        PlotProperties.setTabOrder(self.cboLegendPos, self.cbGridY)
        PlotProperties.setTabOrder(self.cbGridY, self.cbGridX)
        PlotProperties.setTabOrder(self.cbGridX, self.sbFigSizeX)
        PlotProperties.setTabOrder(self.sbFigSizeX, self.sbFigSizeY)
        PlotProperties.setTabOrder(self.sbFigSizeY, self.cbLegend)

    def retranslateUi(self, PlotProperties):
        _translate = QtCore.QCoreApplication.translate
        PlotProperties.setWindowTitle(_translate("PlotProperties", "Plot Properties"))
        self.label_18.setText(_translate("PlotProperties", "2nd X Axis Limits"))
        self.label_19.setText(_translate("PlotProperties", "Min"))
        self.label_20.setText(_translate("PlotProperties", "Max"))
        self.pbAutoCalcX2Lim.setText(_translate("PlotProperties", "Auto Calc"))
        self.cboLegendPos.setItemText(0, _translate("PlotProperties", "Top-Right"))
        self.cboLegendPos.setItemText(1, _translate("PlotProperties", "Top-Left"))
        self.cboLegendPos.setItemText(2, _translate("PlotProperties", "Bottom-Left"))
        self.cboLegendPos.setItemText(3, _translate("PlotProperties", "Bottom-Right"))
        self.cbGridX.setText(_translate("PlotProperties", "X Grid Lines"))
        self.label_2.setText(_translate("PlotProperties", "X Axis Label"))
        self.label_4.setText(_translate("PlotProperties", "X Axis Limits"))
        self.label_10.setText(_translate("PlotProperties", "Figure Size (mm)"))
        self.label_12.setText(_translate("PlotProperties", "Y: "))
        self.label_11.setText(_translate("PlotProperties", "X: "))
        self.label_7.setText(_translate("PlotProperties", "Y Axis Limits"))
        self.label.setText(_translate("PlotProperties", "Title"))
        self.label_5.setText(_translate("PlotProperties", "Min"))
        self.pbAutoCalcXLim.setText(_translate("PlotProperties", "Auto Calc"))
        self.label_6.setText(_translate("PlotProperties", "Max"))
        self.cbGridY.setText(_translate("PlotProperties", "Y Grid Lines"))
        self.label_13.setText(_translate("PlotProperties", "2nd Y Axis Label"))
        self.label_3.setText(_translate("PlotProperties", "Y Axis Label"))
        self.label_14.setText(_translate("PlotProperties", "2nd Y Axis Limits"))
        self.label_16.setText(_translate("PlotProperties", "Max"))
        self.pbAutoCalcY2Lim.setText(_translate("PlotProperties", "Auto Calc"))
        self.label_15.setText(_translate("PlotProperties", "Min"))
        self.label_17.setText(_translate("PlotProperties", "X Axis Rotation"))
        self.cbLegend.setText(_translate("PlotProperties", "Legend"))
        self.label_9.setText(_translate("PlotProperties", "Max"))
        self.pbAutoCalcYLim.setText(_translate("PlotProperties", "Auto Calc"))
        self.label_8.setText(_translate("PlotProperties", "Min"))
        self.label_21.setText(_translate("PlotProperties", "2nd X Axis Label"))

