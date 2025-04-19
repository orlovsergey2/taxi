from PySide6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Увеличиваем размеры и отступы для формы
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(200, 180, 400, 120))  # Увеличенная область
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(15)  # Увеличенный отступ между элементами
        self.verticalLayout.setObjectName("verticalLayout")

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setVerticalSpacing(15)  # Увеличенный отступ между строками
        self.formLayout.setObjectName("formLayout")

        # Поле логина
        self.login = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.login.setObjectName("login")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.login)

        self.LineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.LineEdit.setObjectName("LineEdit")
        self.LineEdit.setMinimumSize(QtCore.QSize(250, 40))  # Увеличенная высота
        self.LineEdit.setPlaceholderText("Введите логин")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.LineEdit)

        # Поле пароля
        self.password = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.password.setObjectName("password")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.password)

        self.LineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.LineEdit_2.setObjectName("LineEdit_2")
        self.LineEdit_2.setMinimumSize(QtCore.QSize(250, 40))  # Увеличенная высота
        self.LineEdit_2.setPlaceholderText("Введите пароль")
        self.LineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.LineEdit_2)

        self.verticalLayout.addLayout(self.formLayout)

        # Заголовок
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(300, 80, 200, 50))  # Увеличенный размер
        self.label.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(18)  # Увеличенный шрифт
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Кнопки
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(200, 320, 400, 60))  # Увеличенная область
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(20)  # Увеличенный отступ между кнопками
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.enter = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.enter.setObjectName("enter")
        self.enter.setMinimumSize(QtCore.QSize(150, 45))  # Увеличенный размер
        self.horizontalLayout.addWidget(self.enter)

        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(QtCore.QSize(150, 45))  # Увеличенный размер
        self.horizontalLayout.addWidget(self.pushButton)

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