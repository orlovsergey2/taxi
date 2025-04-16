# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QListView, QMainWindow, QMenuBar,
                               QPushButton, QSizePolicy, QStatusBar, QWidget, QVBoxLayout, QHBoxLayout,
                               QAbstractItemView)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(733, 600)

        # Центральный виджет и layout
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Основной вертикальный layout
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)

        # Горизонтальный layout для кнопки "Назад"
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Кнопка "Назад"
        self.exit = QPushButton(self.centralwidget)
        self.exit.setObjectName(u"exit")
        self.exit.setFixedSize(120, 40)
        back_font = QFont()
        back_font.setPointSize(12)
        self.exit.setFont(back_font)
        self.horizontalLayout.addWidget(self.exit, 0, Qt.AlignRight)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # Список водителей
        self.listView = QListView(self.centralwidget)
        self.listView.setObjectName(u"listView")
        list_font = QFont()
        list_font.setPointSize(14)
        self.listView.setFont(list_font)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalLayout.addWidget(self.listView)

        # Кнопка удаления водителя
        self.btn_del_driver = QPushButton(self.centralwidget)
        self.btn_del_driver.setObjectName(u"btn_del_driver")
        self.btn_del_driver.setFixedSize(220, 50)
        btn_font = QFont()
        btn_font.setPointSize(12)
        self.btn_del_driver.setFont(btn_font)
        self.verticalLayout.addWidget(self.btn_del_driver, 0, Qt.AlignHCenter)

        MainWindow.setCentralWidget(self.centralwidget)

        # Меню и статусбар
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 733, 26))
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Список водителей", None))
        self.exit.setText(QCoreApplication.translate("MainWindow", u"Назад", None))
        self.btn_del_driver.setText(QCoreApplication.translate("MainWindow", u"Удалить водителя", None))