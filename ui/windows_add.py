from PySide6 import QtCore
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
                               QListView, QPushButton, QSizePolicy, QWidget,
                               QVBoxLayout, QHBoxLayout, QGroupBox, QSpacerItem, QFormLayout, QDateEdit)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1000, 700)  # Оптимальный размер окна

        # Центральный виджет и основной layout
        self.central_widget = QWidget(Form)
        self.central_widget.setObjectName(u"central_widget")
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок (центрированный)
        self.label = QLabel(self.central_widget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label)

        # Добавляем отступ после заголовка
        self.main_layout.addSpacing(20)

        # Группа для данных автомобиля
        self.car_group = QGroupBox(self.central_widget)
        self.car_group.setObjectName(u"car_group")
        self.car_layout = QVBoxLayout(self.car_group)

        # Форма для полей ввода автомобиля
        self.car_form_layout = QFormLayout()
        self.car_form_layout.setHorizontalSpacing(10)
        self.car_form_layout.setVerticalSpacing(8)

        # Поля для автомобиля
        self.lineEdit_number_auto = QLineEdit(self.car_group)
        self.lineEdit_number_auto.setReadOnly(True)
        self.lineEdit_number_auto.setPlaceholderText("Нажмите 'Сгенерировать номер'")
        self.lineEdit_number_auto.setObjectName(u"lineEdit_number_auto")
        self.lineEdit_number_auto.setMinimumSize(250, 30)

        self.lineEdit_model = QLineEdit(self.car_group)
        self.lineEdit_model.setObjectName(u"lineEdit_model")
        self.lineEdit_model.setMinimumSize(250, 30)

        self.lineEdit_year_edit = QLineEdit(self.car_group)
        self.lineEdit_year_edit.setObjectName(u"lineEdit_year_edit")
        self.lineEdit_year_edit.setMinimumSize(250, 30)

        self.comboBox_mark_auto = QComboBox(self.car_group)
        self.comboBox_mark_auto.setObjectName(u"comboBox_mark_auto")
        self.comboBox_mark_auto.setMinimumSize(250, 30)
        self.comboBox_mark_auto.addItems(["sedan", "minivan", "suv", "business", "electric"])

        self.lineEdit_capicaty = QLineEdit(self.car_group)
        self.lineEdit_capicaty.setObjectName(u"lineEdit_capicaty")
        self.lineEdit_capicaty.setMinimumSize(250, 30)

        # Добавляем поля в форму
        self.car_form_layout.addRow("Номер авто:", self.lineEdit_number_auto)
        self.car_form_layout.addRow("Модель:", self.lineEdit_model)
        self.car_form_layout.addRow("Год выпуска:", self.lineEdit_year_edit)
        self.car_form_layout.addRow("Марка авто:", self.comboBox_mark_auto)
        self.car_form_layout.addRow("Вместительность:", self.lineEdit_capicaty)

        self.car_layout.addLayout(self.car_form_layout)

        # Кнопки для автомобиля (уменьшенные)
        self.car_buttons_layout = QHBoxLayout()
        self.car_buttons_layout.setSpacing(5)  # Уменьшил расстояние между кнопками

        self.btn_generate_number = QPushButton(self.car_group)
        self.btn_generate_number.setObjectName(u"btn_generate_number")
        self.btn_generate_number.setFixedSize(200, 40)  # Уменьшил размер кнопок

        self.add_auto = QPushButton(self.car_group)
        self.add_auto.setObjectName(u"add_auto")
        self.add_auto.setFixedSize(200, 40)

        self.car_buttons_layout.addWidget(self.btn_generate_number)
        self.car_buttons_layout.addWidget(self.add_auto)
        self.car_layout.addLayout(self.car_buttons_layout)

        self.main_layout.addWidget(self.car_group)
        self.main_layout.addSpacing(20)

        # Группа для данных водителя
        self.driver_group = QGroupBox(self.central_widget)
        self.driver_group.setObjectName(u"driver_group")
        self.driver_layout = QVBoxLayout(self.driver_group)

        # Форма для полей ввода водителя
        self.driver_form_layout = QFormLayout()
        self.driver_form_layout.setHorizontalSpacing(10)
        self.driver_form_layout.setVerticalSpacing(8)

        # Поля для водителя
        self.lineEdit_name = QLineEdit(self.driver_group)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(250, 30)

        self.lineEdit = QLineEdit(self.driver_group)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(250, 30)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setPlaceholderText("Нажмите 'Сгенерировать ID'")

        self.lineEdit_number = QLineEdit(self.driver_group)
        self.lineEdit_number.setObjectName(u"lineEdit_number")
        self.lineEdit_number.setMinimumSize(250, 30)

        # Заменяем QLineEdit для даты на QDateEdit с календарем
        self.dateEdit_hire = QDateEdit(self.driver_group)  # Заменяем lineEdit_date
        self.dateEdit_hire.setObjectName(u"dateEdit_hire")
        self.dateEdit_hire.setMinimumSize(250, 30)
        self.dateEdit_hire.setCalendarPopup(True)  # Включаем выпадающий календарь
        self.dateEdit_hire.setDisplayFormat("yyyy-MM-dd")  # Формат даты
        self.dateEdit_hire.setDate(QtCore.QDate.currentDate())  # Установка текущей даты

        # Добавляем поля в форму
        self.driver_form_layout.addRow("Имя водителя:", self.lineEdit_name)
        self.driver_form_layout.addRow("ID водителя:", self.lineEdit)
        self.driver_form_layout.addRow("Номер телефона:", self.lineEdit_number)
        self.driver_form_layout.addRow("Дата найма:", self.dateEdit_hire)

        self.driver_layout.addLayout(self.driver_form_layout)

        # Кнопки для водителя (уменьшенные)
        self.driver_buttons_layout = QHBoxLayout()
        self.driver_buttons_layout.setSpacing(5)  # Уменьшил расстояние между кнопками

        self.btn_generate_id = QPushButton(self.driver_group)
        self.btn_generate_id.setObjectName(u"btn_generate_id")
        self.btn_generate_id.setFixedSize(200, 40)

        self.add_driver = QPushButton(self.driver_group)
        self.add_driver.setObjectName(u"add_driver")
        self.add_driver.setFixedSize(200, 40)

        self.driver_buttons_layout.addWidget(self.btn_generate_id)
        self.driver_buttons_layout.addWidget(self.add_driver)
        self.driver_layout.addLayout(self.driver_buttons_layout)

        self.main_layout.addWidget(self.driver_group)
        self.main_layout.addSpacing(20)

        # Кнопки навигации (уменьшенные)
        self.nav_buttons_layout = QHBoxLayout()
        self.nav_buttons_layout.setSpacing(5)  # Уменьшил расстояние между кнопками

        self.pushButton_2 = QPushButton(self.central_widget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setFixedSize(200, 40)

        self.pushButton_3 = QPushButton(self.central_widget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setFixedSize(200, 40)

        self.nav_buttons_layout.addWidget(self.pushButton_2)
        self.nav_buttons_layout.addWidget(self.pushButton_3)
        self.main_layout.addLayout(self.nav_buttons_layout)

        # Кнопка "Назад" (в правом верхнем углу)
        self.pushButton_back = QPushButton(self.central_widget)
        self.pushButton_back.setObjectName(u"pushButton_back")
        self.pushButton_back.setFixedSize(100, 45)
        self.pushButton_back.move(700, 15)

        Form.setCentralWidget(self.central_widget)

        # Установка шрифта для всех кнопок
        button_font = QFont()
        button_font.setPointSize(9)  # Уменьшил размер шрифта
        for button in Form.findChildren(QPushButton):
            button.setFont(button_font)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Таксопарк", None))
        self.label.setText(QCoreApplication.translate("Form", u"Таксонометрический парк", None))
        self.car_group.setTitle(QCoreApplication.translate("Form", u"Данные автомобиля", None))
        self.driver_group.setTitle(QCoreApplication.translate("Form", u"Данные водителя", None))

        # Тексты для полей автомобиля
        self.add_auto.setText(QCoreApplication.translate("Form", u"Добавить авто", None))
        self.btn_generate_number.setText(QCoreApplication.translate("Form", u"Сгенерировать номер", None))

        # Тексты для полей водителя
        self.add_driver.setText(QCoreApplication.translate("Form", u"Добавить водителя", None))
        self.btn_generate_id.setText(QCoreApplication.translate("Form", u"Сгенерировать ID", None))

        # Тексты для кнопок навигации
        self.pushButton_back.setText(QCoreApplication.translate("Form", u"Назад", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Посмотреть водителей", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Посмотреть автомобили", None))