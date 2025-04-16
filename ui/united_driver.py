# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListView, QMainWindow,
                               QMenuBar, QPushButton, QSizePolicy, QStatusBar,
                               QWidget, QAbstractItemView)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        # Увеличиваем размер окна для лучшего отображения
        MainWindow.resize(1100, 800)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Заголовок окна
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(450, 10, 200, 40))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)

        # Кнопка "Назад"
        self.btn_back = QPushButton(self.centralwidget)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setGeometry(QRect(900, 20, 150, 40))
        self.btn_back.setFont(font)

        # Список распределенных пар
        self.listView_united = QListView(self.centralwidget)
        self.listView_united.setObjectName(u"listView_united")
        self.listView_united.setGeometry(QRect(50, 60, 1000, 300))
        self.listView_united.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_united.setSelectionMode(QAbstractItemView.SingleSelection)

        # Кнопка "Распределить водителей"
        self.btn_united = QPushButton(self.centralwidget)
        self.btn_united.setObjectName(u"btn_united")
        self.btn_united.setGeometry(QRect(50, 380, 300, 50))  # Увеличена ширина и высота
        self.btn_united.setFont(font)

        # Кнопка "Открепить водителя"
        self.btn_ununited = QPushButton(self.centralwidget)
        self.btn_ununited.setObjectName(u"btn_ununited")
        self.btn_ununited.setGeometry(QRect(750, 380, 300, 50))  # Увеличена ширина и высота
        self.btn_ununited.setFont(font)

        # Список свободных водителей
        self.listView_free_driver = QListView(self.centralwidget)
        self.listView_free_driver.setObjectName(u"listView_free_driver")
        self.listView_free_driver.setGeometry(QRect(50, 480, 450, 270))
        self.listView_free_driver.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_free_driver.setSelectionMode(QAbstractItemView.SingleSelection)

        # Метка "Свободные водители"
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(50, 450, 450, 30))
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignCenter)

        # Список свободных автомобилей
        self.listView_3 = QListView(self.centralwidget)
        self.listView_3.setObjectName(u"listView_3")
        self.listView_3.setGeometry(QRect(550, 480, 500, 270))
        self.listView_3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_3.setSelectionMode(QAbstractItemView.SingleSelection)

        # Метка "Свободные автомобили"
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(550, 450, 500, 30))
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1100, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", u"Управление водителями и автомобилями", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Прикрепление водителей", None))
        self.btn_back.setText(QCoreApplication.translate("MainWindow", u"Назад", None))
        self.btn_united.setText(QCoreApplication.translate("MainWindow", u"Распределить водителей", None))
        self.btn_ununited.setText(QCoreApplication.translate("MainWindow", u"Открепить всех водителей", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Свободные водители", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Свободные автомобили", None))