from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QPushButton,
                               QSizePolicy, QStatusBar, QWidget)
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        # Увеличиваем размеры кнопок для лучшей читаемости
        button_width = 200
        button_height = 40
        button_spacing = 10
        # Расположение кнопок с увеличенными размерами
        self.btn_add_data = QPushButton(self.centralwidget)
        self.btn_add_data.setObjectName(u"btn_add_data")
        self.btn_add_data.setGeometry(QRect(300, 30, button_width, button_height))
        self.btn_taxi_park = QPushButton(self.centralwidget)
        self.btn_taxi_park.setObjectName(u"btn_taxi_park")
        self.btn_taxi_park.setGeometry(QRect(300, 30 + button_height + button_spacing, button_width, button_height))
        self.btn_taxi_park.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.btn_driver = QPushButton(self.centralwidget)
        self.btn_driver.setObjectName(u"btn_driver")
        self.btn_driver.setGeometry(QRect(300, 30 + 2 * (button_height + button_spacing), button_width, button_height))
        self.btn_free_driver = QPushButton(self.centralwidget)
        self.btn_free_driver.setObjectName(u"btn_free_driver")
        self.btn_free_driver.setGeometry(
            QRect(300, 30 + 3 * (button_height + button_spacing), button_width, button_height))
        self.btn_go_to = QPushButton(self.centralwidget)
        self.btn_go_to.setObjectName(u"btn_free_auto")
        self.btn_go_to.setGeometry(
            QRect(300, 30 + 4 * (button_height + button_spacing), button_width, button_height))
        self.btn_list_to = QPushButton(self.centralwidget)
        self.btn_list_to.setObjectName(u"btn_list_to")
        self.btn_list_to.setGeometry(
            QRect(300, 30 + 5 * (button_height + button_spacing), button_width, button_height))
        self.btn_united_auto = QPushButton(self.centralwidget)
        self.btn_united_auto.setObjectName(u"btn_united_auto")
        self.btn_united_auto.setGeometry(
            QRect(300, 30 + 6 * (button_height + button_spacing), button_width, button_height))
        self.btn_exit = QPushButton(self.centralwidget)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setGeometry(QRect(300, 500, button_width, button_height))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Управление таксопарком", None))
        self.btn_add_data.setText(QCoreApplication.translate("MainWindow", u"Добавить данные", None))
        self.btn_taxi_park.setText(QCoreApplication.translate("MainWindow", u"Данные о такси", None))
        self.btn_driver.setText(QCoreApplication.translate("MainWindow", u"Данные о водителях", None))
        self.btn_free_driver.setText(QCoreApplication.translate("MainWindow", u"Неприкрепленные", None))
        self.btn_go_to.setText(QCoreApplication.translate("MainWindow", u"Пора на ТО!", None))
        self.btn_list_to.setText(QCoreApplication.translate("MainWindow", u"История ТО", None))
        self.btn_united_auto.setText(QCoreApplication.translate("MainWindow", u"Прикрепить водителя", None))
        self.btn_exit.setText(QCoreApplication.translate("MainWindow", u"Выход", None))