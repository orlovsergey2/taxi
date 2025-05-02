from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform,
                           QDoubleValidator, QIntValidator)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
                               QListView, QMainWindow, QMenuBar, QPushButton,
                               QSizePolicy, QStatusBar, QTextEdit, QVBoxLayout,
                               QWidget, QFormLayout, QDateEdit, QGroupBox,
                               QHBoxLayout, QSpacerItem, QFrame)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 700)

        # Создаем центральный виджет
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Основной layout (горизонтальный)
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(15)

        # Левая часть - список автомобилей
        self.setup_left_panel()

        # Правая часть - ТО и история
        self.setup_right_panel()

        # Устанавливаем центральный виджет
        MainWindow.setCentralWidget(self.centralwidget)

        # Меню и статусбар
        self.setup_menu_and_statusbar(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def setup_left_panel(self):
        """Настройка левой панели со списком автомобилей"""
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setSpacing(10)

        # Группа для списка автомобилей
        self.carsGroup = QGroupBox(self.centralwidget)
        self.carsGroup.setTitle(QCoreApplication.translate("MainWindow", u"Список автомобилей", None))

        # Список автомобилей
        self.carsListView = QListView(self.carsGroup)
        self.carsListView.setObjectName(u"carsListView")
        self.carsListView.setMinimumHeight(300)

        # Настройки для нередактируемого, но кликабельного списка
        self.carsListView.setEditTriggers(QListView.NoEditTriggers)  # Запрет редактирования
        self.carsListView.setSelectionMode(QListView.SingleSelection)  # Одиночный выбор
        self.carsListView.setFocusPolicy(Qt.StrongFocus)  # Возможность фокусировки

        carsLayout = QVBoxLayout(self.carsGroup)
        carsLayout.addWidget(self.carsListView)
        self.leftLayout.addWidget(self.carsGroup)

        # Кнопка Назад
        self.btnBack = QPushButton(self.centralwidget)
        self.btnBack.setObjectName(u"btnBack")
        self.btnBack.setText(QCoreApplication.translate("MainWindow", u"Назад", None))
        self.leftLayout.addWidget(self.btnBack)

        self.mainLayout.addLayout(self.leftLayout)

    def setup_right_panel(self):
        """Настройка правой панели с формой ТО и историей"""
        self.rightLayout = QVBoxLayout()
        self.rightLayout.setSpacing(10)

        # Группа для информации о ТО
        self.setup_maintenance_group()

        # Группа для истории ТО
        self.setup_history_group()

        self.mainLayout.addLayout(self.rightLayout)

    def setup_maintenance_group(self):
        """Настройка группы технического обслуживания"""
        self.maintenanceGroup = QGroupBox(self.centralwidget)
        self.maintenanceGroup.setTitle(QCoreApplication.translate("MainWindow", u"Техническое обслуживание", None))
        self.maintenanceGroup.setEnabled(False)
        self.maintenanceGroup.setMinimumWidth(400)

        # Форма для данных ТО
        self.formLayout = QFormLayout(self.maintenanceGroup)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setHorizontalSpacing(15)

        # Создаем и настраиваем элементы формы
        self.setup_form_elements()

        # Добавляем кнопку "Добавить ТО"
        self.setup_maintenance_button()

        self.rightLayout.addWidget(self.maintenanceGroup)

    def setup_form_elements(self):
        """Настройка элементов формы ТО"""
        # Заголовки
        self.dateLabel = QLabel("Дата ТО:")
        self.mileageLabel = QLabel("Пробег (км):")
        self.typeLabel = QLabel("Тип обслуживания:")
        self.descLabel = QLabel("Описание работ:")
        self.costLabel = QLabel("Стоимость:")

        # Поля формы
        self.dateEdit = QDateEdit(self.maintenanceGroup)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit.setDisplayFormat("dd.MM.yyyy")

        self.mileageEdit = QLineEdit(self.maintenanceGroup)
        self.mileageEdit.setValidator(QIntValidator(0, 1000000))
        self.mileageEdit.setPlaceholderText("0.00")

        self.serviceTypeCombo = QComboBox(self.maintenanceGroup)
        self.serviceTypeCombo.addItems(['Регламентное', 'Ремонт', 'Диагностика'])

        self.descriptionEdit = QTextEdit(self.maintenanceGroup)
        self.descriptionEdit.setMaximumHeight(100)
        self.descriptionEdit.setMinimumHeight(80)
        self.descriptionEdit.setPlaceholderText("Подробное описание выполненных работ...")

        self.costEdit = QLineEdit(self.maintenanceGroup)
        self.costEdit.setValidator(QDoubleValidator(0, 100000, 2))
        self.costEdit.setPlaceholderText("0.00")

        # Добавляем поля в форму
        self.formLayout.addRow(self.dateLabel, self.dateEdit)
        self.formLayout.addRow(self.mileageLabel, self.mileageEdit)
        self.formLayout.addRow(self.typeLabel, self.serviceTypeCombo)
        self.formLayout.addRow(self.descLabel, self.descriptionEdit)
        self.formLayout.addRow(self.costLabel, self.costEdit)

    def setup_maintenance_button(self):
        """Настройка кнопки добавления ТО"""
        self.btnAddMaintenance = QPushButton(self.maintenanceGroup)
        self.btnAddMaintenance.setObjectName(u"btnAddMaintenance")
        self.btnAddMaintenance.setText(QCoreApplication.translate("MainWindow", u"Добавить ТО", None))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.btnAddMaintenance)
        self.formLayout.addRow(buttonLayout)

    def setup_history_group(self):
        """Настройка группы истории ТО"""
        self.historyGroup = QGroupBox(self.centralwidget)
        self.historyGroup.setTitle(QCoreApplication.translate("MainWindow", u"История ТО", None))
        self.historyListView = QListView(self.historyGroup)
        self.historyListView.setMinimumHeight(200)
        # Настройки для нередактируемого, но кликабельного списка
        self.historyListView.setEditTriggers(QListView.NoEditTriggers)
        self.historyListView.setSelectionMode(QListView.SingleSelection)
        self.historyListView.setFocusPolicy(Qt.StrongFocus)
        historyLayout = QVBoxLayout(self.historyGroup)
        historyLayout.addWidget(self.historyListView)

        self.rightLayout.addWidget(self.historyGroup)

    def setup_menu_and_statusbar(self, MainWindow):
        """Настройка меню и статусбара"""
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 22))
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)