# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\esymons\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\coastalme\forms\ui_AboutDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from qgis.PyQt import QtCore, QtGui, QtWidgets



from ..compatibility_routines import QT_SIZE_POLICY_MINIMUM, QT_SIZE_POLICY_EXPANDING, QT_ALIGN_CENTER


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(285, 175)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(AboutDialog)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/logo/resources/COASTALME_logo_resized.png"))
        self.label.setAlignment(QT_ALIGN_CENTER)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.textEdit = QtWidgets.QTextBrowser(AboutDialog)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout.addItem(spacerItem)
        self.pbCopyText = QtWidgets.QPushButton(AboutDialog)
        self.pbCopyText.setObjectName("pbCopyText")
        self.horizontalLayout.addWidget(self.pbCopyText)
        self.pbClose = QtWidgets.QPushButton(AboutDialog)
        self.pbClose.setObjectName("pbClose")
        self.horizontalLayout.addWidget(self.pbClose)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QT_SIZE_POLICY_EXPANDING, QT_SIZE_POLICY_MINIMUM)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About"))
        self.pbCopyText.setText(_translate("AboutDialog", "Copy Text"))
        self.pbClose.setText(_translate("AboutDialog", "Close"))
import coastalme.resources.coastalme
