from PySide6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget1")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(180, 190, 371, 61))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")

        self.login = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.login.setObjectName("login")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.login)

        self.LineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.LineEdit.setObjectName("LineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.LineEdit)

        self.password = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.password.setObjectName("password")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.password)

        self.LineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.LineEdit_2.setObjectName("LineEdit_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.LineEdit_2)

        self.verticalLayout.addLayout(self.formLayout)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(310, 60, 81, 41))
        self.label.setObjectName("label")

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(170, 290, 151, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.enter = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.enter.setObjectName("enter")
        self.horizontalLayout.addWidget(self.enter)

        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(390, 290, 161, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.login.setText(_translate("MainWindow", "Логин"))
        self.password.setText(_translate("MainWindow", "Пароль"))
        self.label.setText(_translate("MainWindow", "Авторизация"))
        self.enter.setText(_translate("MainWindow", "Войти"))
        self.pushButton.setText(_translate("MainWindow", "Регистрация"))