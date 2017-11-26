# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(845, 568)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(70, 60, 256, 311))
        self.listWidget.setObjectName("listWidget")
        self.btnBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowse.setGeometry(QtCore.QRect(70, 400, 261, 51))
        self.btnBrowse.setObjectName("btnBrowse")
        self.firstNumber = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.firstNumber.setGeometry(QtCore.QRect(400, 60, 104, 70))
        self.firstNumber.setObjectName("firstNumber")
        self.secondNumber = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.secondNumber.setGeometry(QtCore.QRect(540, 60, 104, 70))
        self.secondNumber.setObjectName("secondNumber")
        self.addThem = QtWidgets.QPushButton(self.centralwidget)
        self.addThem.setGeometry(QtCore.QRect(400, 200, 80, 23))
        self.addThem.setObjectName("addThem")
        self.theResult = QtWidgets.QLabel(self.centralwidget)
        self.theResult.setGeometry(QtCore.QRect(698, 64, 91, 61))
        self.theResult.setObjectName("theResult")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnBrowse.setText(_translate("MainWindow", "pick a folder"))
        self.addThem.setText(_translate("MainWindow", "PushButton"))
        self.theResult.setText(_translate("MainWindow", "TextLabel"))

