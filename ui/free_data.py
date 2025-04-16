# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'free_data.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListView, QMainWindow,
                               QMenuBar, QPushButton, QSizePolicy, QStatusBar,
                               QWidget, QVBoxLayout, QHBoxLayout,
                               QAbstractItemView)
from PySide6.QtCore import QStringListModel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 500)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Основной вертикальный layout
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)

        # Горизонтальный layout для кнопки
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins(0, 0, 0, 20)

        # Добавляем растяжку перед кнопкой "Назад"
        self.buttonLayout.addStretch()

        # Кнопка "Назад"
        self.btn_back = QPushButton(self.centralwidget)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setMinimumSize(QSize(120, 35))
        font = QFont()
        font.setBold(True)
        self.btn_back.setFont(font)
        self.buttonLayout.addWidget(self.btn_back)

        self.verticalLayout.addLayout(self.buttonLayout)

        # Горизонтальный layout для списков
        self.listsLayout = QHBoxLayout()
        self.listsLayout.setSpacing(30)

        # Модели данных
        self.drivers_model = QStringListModel()
        self.cars_model = QStringListModel()

        # Вертикальный layout для водителей
        self.driversLayout = QVBoxLayout()
        self.driversLayout.setSpacing(10)

        # Заголовок для списка водителей
        self.label_drivers = QLabel(self.centralwidget)
        self.label_drivers.setObjectName(u"label_drivers")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_drivers.setFont(font)
        self.driversLayout.addWidget(self.label_drivers)

        # Список свободных водителей (только для чтения)
        self.listView_drivers = QListView(self.centralwidget)
        self.listView_drivers.setObjectName(u"listView_drivers")
        self.listView_drivers.setMinimumSize(QSize(350, 300))
        self.listView_drivers.setModel(self.drivers_model)
        self.listView_drivers.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.listView_drivers.setSelectionMode(QAbstractItemView.NoSelection)  # Запрет выделения
        self.driversLayout.addWidget(self.listView_drivers)

        self.listsLayout.addLayout(self.driversLayout)

        # Вертикальный layout для автомобилей
        self.carsLayout = QVBoxLayout()
        self.carsLayout.setSpacing(10)

        # Заголовок для списка автомобилей
        self.label_cars = QLabel(self.centralwidget)
        self.label_cars.setObjectName(u"label_cars")
        self.label_cars.setFont(font)
        self.carsLayout.addWidget(self.label_cars)

        # Список свободных автомобилей (только для чтения)
        self.listView_cars = QListView(self.centralwidget)
        self.listView_cars.setObjectName(u"listView_cars")
        self.listView_cars.setMinimumSize(QSize(350, 300))
        self.listView_cars.setModel(self.cars_model)
        self.listView_cars.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования
        self.listView_cars.setSelectionMode(QAbstractItemView.NoSelection)  # Запрет выделения
        self.carsLayout.addWidget(self.listView_cars)

        self.listsLayout.addLayout(self.carsLayout)

        self.verticalLayout.addLayout(self.listsLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 21))
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Свободные водители и автомобили", None))
        self.btn_back.setText(QCoreApplication.translate("MainWindow", u"Назад", None))
        self.label_drivers.setText(QCoreApplication.translate("MainWindow", u"Свободные водители", None))
        self.label_cars.setText(QCoreApplication.translate("MainWindow", u"Свободные автомобили", None))