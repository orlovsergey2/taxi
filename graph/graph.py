# graph.py (исправленная и оптимизированная версия)
import os
import sys
import logging
from datetime import datetime
from PySide6.QtGui import QRegularExpressionValidator, QIntValidator
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QSize, QStringListModel, QDate
from PySide6.QtWidgets import (QApplication, QMessageBox, QMainWindow)
from autorization.registration import Database
from ui import autorization, main_menu, list_auto, list_driver, united_driver, free_data, go_to, history_to
from ui.windows_add import Ui_Form
from taxi.taxi_park import DatabaseManager
import random

# Настройка логирования
def setup_logging():
    """Настраивает систему логирования с записью в файл внутри проекта"""
    try:
        # Получаем путь к директории текущего скрипта
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Создаем папку logs внутри проекта, если ее нет
        log_dir = os.path.join(script_dir, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Создана папка для логов: {log_dir}")

        # Формируем имя файла лога с текущей датой
        log_filename = f"taxi_park_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_filepath = os.path.join(log_dir, log_filename)

        # Настраиваем логгер
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filepath),
                logging.StreamHandler(sys.stdout)  # Также выводим в консоль
            ]
        )

        logger = logging.getLogger('taxi_park')
        logger.info(f"Инициализировано логирование. Файл лога: {log_filepath}")
        return logger

    except Exception as e:
        # Если не удалось настроить файловое логирование, используем только консоль
        print(f"Ошибка настройки логирования: {e}")
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        return logging.getLogger('taxi_park_console')

# Глобальный логгер
logger = setup_logging()

def log_action(action, details=None):
    """Логирует действие пользователя с дополнительной информацией"""
    user = getattr(QApplication.instance(), 'current_user', 'Неавторизованный пользователь')
    message = f"Пользователь: {user} | Действие: {action}"
    if details:
        message += f" | Детали: {details}"
    logger.info(message)
def setup_date_limits(date_edit):
    """Устанавливает ограничения на ввод даты (глобальная функция)"""
    log_action("Установка ограничений даты")
    # Текущая дата
    current_date = QtCore.QDate.currentDate()
    # Минимальная дата - 1 января 2000 года
    min_date = QtCore.QDate(2000, 1, 1)
    # Устанавливаем ограничения для dateEdit
    date_edit.setDate(current_date)
    date_edit.setMinimumDate(min_date)
    date_edit.setMaximumDate(current_date)
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat("dd.MM.yyyy")
    date_edit.setToolTip(
        f"Введите дату между {min_date.toString('dd.MM.yyyy')} "
        f"и {current_date.toString('dd.MM.yyyy')}"
    )

def validate_date_input(parent, date_edit):
    """Проверяет корректность введенной даты (глобальная функция)"""
    log_action("Настройка валидаторов в окне ТО")
    current_date = QtCore.QDate.currentDate()
    min_date = QtCore.QDate(2000, 1, 1)
    input_date = date_edit.date()

    if input_date < min_date or input_date > current_date:
        error_msg = f"Дата должна быть между {min_date.toString('dd.MM.yyyy')} и {current_date.toString('dd.MM.yyyy')}"
        QtWidgets.QMessageBox.warning(parent, "Ошибка", error_msg)
        date_edit.setDate(current_date)
        log_action("Ошибка валидации даты", error_msg)
        return False
    return True

def load_application_styles(app):
    """Загружает стили из конкретного расположения"""
    style_path = r"D:\taxi\style\styles.qss"
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        log_action("Загрузка стилей приложения", f"Стили загружены из {style_path}")
        return True
    except Exception as e:
        error_msg = f"Ошибка загрузки стилей: {e}"
        print(error_msg)
        log_action("Ошибка загрузки стилей", error_msg)
        return False

def go_back(widget, stacked_widget):
    """Глобальная функция для возврата в предыдущее окно"""
    log_action("Возврат в предыдущее окно", f"Из {widget.__class__.__name__}")
    stacked_widget.setCurrentIndex(1)
    stacked_widget.removeWidget(widget)
    widget.deleteLater()

class BaseWindow:
    """Базовый класс для окон с общими методами"""
    def check_db_connection(self, db):
        """Проверяет соединение с базой данных"""
        if not db._get_cursor():
            error_msg = "Не удалось подключиться к базе данных"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка подключения к БД", error_msg)
            return False
        return True

class LoginWindow(QMainWindow, autorization.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = Database()
        self.LineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.enter.clicked.connect(self.handle_login)
        self.pushButton.clicked.connect(self.handle_register)
        log_action("Инициализация окна входа")

    def sizeHint(self):
        return QSize(800, 600)

    def handle_login(self):
        username = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not username or not password:
            error_msg = "Введите логин и пароль"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка входа", error_msg)
            return

        success, message, is_admin = self.db.check_credentials(username, password)
        if success:
            QApplication.instance().current_user = username
            log_action("Успешный вход", f"Пользователь: {username}, Админ: {bool(is_admin)}")
            self.MainWindow = MainWindow(self.stacked_widget, is_admin=bool(is_admin))
            self.stacked_widget.addWidget(self.MainWindow)
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Ошибка", message)
            log_action("Неудачная попытка входа", f"Пользователь: {username}, Ошибка: {message}")

    def handle_register(self):
        username = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not username or not password:
            error_msg = "Введите логин и пароль"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка регистрации", error_msg)
            return

        if len(password) < 8:
            error_msg = "Пароль должен содержать минимум 8 символов"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка регистрации", error_msg)
            return

        success, message = self.db.register_user(username, password)
        if success:
            QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован")
            log_action("Успешная регистрация", f"Пользователь: {username}")
        else:
            QMessageBox.warning(self, "Ошибка", message)
            log_action("Ошибка регистрации", f"Пользователь: {username}, Ошибка: {message}")


class CarManagerWindow(QtWidgets.QMainWindow, list_auto.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget, is_admin=0):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.current_items = []
        self.is_admin = is_admin
        self.model = QtCore.QStringListModel()
        self.listView.setModel(self.model)
        log_action("Инициализация окна управления автомобилями", f"Админ: {is_admin}")

        if not self.is_admin:
            self.btn_del_auto.setVisible(False)

        self.btn_del_auto.clicked.connect(self.delete_selected_car)
        self.exit.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.load_data_car()

    def sizeHint(self):
        return QSize(800, 600)
    def load_data_car(self):
        try:
            log_action("Загрузка данных об автомобилях")
            items = self.db.get_cars()
            if not items:
                self.model.setStringList(["Нет данных об автомобилях"])
                log_action("Нет данных об автомобилях")
                return

            item_list = [
                f"{car['license_plate']} {car['model']} ({car['car_type']})"
                for car in items
            ]

            self.model.setStringList(item_list)
            self.current_items = items
            log_action(f"Загружено {len(items)} автомобилей")

        except Exception as e:
            error_msg = f"Не удалось загрузить данные: {str(e)}"
            QtWidgets.QMessageBox.critical(self, "Ошибка", error_msg)
            self.current_items = []
            log_action("Ошибка загрузки автомобилей", error_msg)

    def delete_selected_car(self):
        if not self.is_admin:
            error_msg = "У вас нет прав для выполнения этой операции"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка удаления автомобиля без прав", error_msg)
            return

        selected = self.listView.selectedIndexes()
        if not selected:
            error_msg = "Выберите автомобиль для удаления"
            QtWidgets.QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка удаления без выбора", error_msg)
            return

        try:
            selected_index = selected[0].row()
            if selected_index >= len(self.current_items):
                error_msg = "Неверный индекс выбранного автомобиля"
                QtWidgets.QMessageBox.warning(self, "Ошибка", error_msg)
                log_action("Ошибка удаления автомобиля", error_msg)
                return

            car = self.current_items[selected_index]
            car_id = car['car_id']

            reply = QtWidgets.QMessageBox.question(
                self,
                'Подтверждение удаления',
                f"Вы уверены, что хотите удалить автомобиль:\n{car['license_plate']} {car['model']}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.Yes:
                if self.db.delete_car(car_id):
                    QtWidgets.QMessageBox.information(self, "Успех", "Автомобиль успешно удален")
                    log_action("Удаление автомобиля", f"ID: {car_id}, Модель: {car['model']}, Номер: {car['license_plate']}")
                    self.load_data_car()
                else:
                    error_msg = "Не удалось удалить автомобиль"
                    QtWidgets.QMessageBox.warning(self, "Ошибка", error_msg)
                    log_action("Ошибка удаления автомобиля", error_msg)

        except Exception as e:
            error_msg = f"Ошибка при удалении автомобиля: {str(e)}"
            QtWidgets.QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка удаления автомобиля", error_msg)


class DriverManagerWindow(QMainWindow, list_driver.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget, is_admin=0):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.is_admin = is_admin
        self.model = QtCore.QStringListModel()
        self.listView.setModel(self.model)
        log_action("Инициализация окна управления водителями", f"Админ: {is_admin}")

        if not self.is_admin:
            self.btn_del_driver.setVisible(False)

        self.btn_del_driver.clicked.connect(self.delete_selected_driver)
        self.exit.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.setup_context_menu()
        self.load_driver_data()

    def sizeHint(self):
        return QSize(800, 600)
    def setup_context_menu(self):
        log_action("Настройка контекстного меню для водителей")
        self.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listView.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        log_action("Отображение контекстного меню для водителей")
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Удалить")
        refresh_action = menu.addAction("Обновить список")

        action = menu.exec_(self.listView.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_driver()
        elif action == refresh_action:
            log_action("Обновление списка водителей через контекстное меню")
            self.load_driver_data()

    def load_driver_data(self):
        try:
            log_action("Загрузка данных о водителях")
            drivers = self.db.get_drivers()
            driver_list = []

            if not drivers:
                driver_list.append("Нет данных о водителях")
                log_action("Нет данных о водителях")
            else:
                for driver in drivers:
                    driver_info = f"{driver['full_name']} (№ прав: {driver['license_number']}), тел.: {driver['phone']}"
                    driver_list.append(driver_info)

            self.model.setStringList(driver_list)
            log_action(f"Загружено {len(drivers)} водителей")

        except Exception as e:
            error_msg = f"Не удалось загрузить данные: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка загрузки водителей", error_msg)

    def delete_selected_driver(self):
        if not self.is_admin:
            error_msg = "У вас нет прав для выполнения этой операции"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка удаления водителя без прав", error_msg)
            return

        selected = self.listView.selectedIndexes()
        if not selected:
            error_msg = "Выберите водителя для удаления"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка удаления водителя без выбора", error_msg)
            return

        selected_index = selected[0].row()
        drivers = self.db.get_drivers()

        if selected_index >= len(drivers):
            error_msg = "Неверный индекс выбранного водителя"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка удаления водителя", error_msg)
            return

        driver = drivers[selected_index]
        driver_info = f"{driver['full_name']} (№ прав: {driver['license_number']})"
        driver_id = driver['driver_id']

        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить водителя:\n{driver_info}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.db.delete_driver(driver_id):
                    self.load_driver_data()
                    success_msg = "Водитель успешно удален"
                    QMessageBox.information(self, "Успех", success_msg)
                    log_action("Удаление водителя",
                               f"ID: {driver_id}, Имя: {driver['full_name']}, Телефон: {driver['phone']}")
                else:
                    error_msg = "Не удалось удалить водителя (возможно, он назначен к автомобилю)"
                    QMessageBox.critical(self, "Ошибка", error_msg)
                    log_action("Ошибка удаления водителя", error_msg)
            except Exception as e:
                error_msg = f"Ошибка при удалении: {str(e)}"
                QMessageBox.critical(self, "Ошибка", error_msg)
                log_action("Ошибка удаления водителя", error_msg)


class TaxiParkWindow(QMainWindow, Ui_Form, BaseWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        setup_date_limits(self.dateEdit_hire)

        # Настройка валидаторов
        phone_validator = QRegularExpressionValidator(r"^\+7\d{10}$")
        self.lineEdit_number.setValidator(phone_validator)
        self.lineEdit_number.setPlaceholderText("+7XXXXXXXXXX")

        current_year = QtCore.QDate.currentDate().year()
        year_validator = QtGui.QIntValidator(1900, current_year)
        self.lineEdit_year_edit.setValidator(year_validator)

        log_action("Инициализация окна таксопарка")

        self.add_auto.clicked.connect(self.on_add_car)
        self.btn_generate_id.clicked.connect(self.generate_driver_id)
        self.btn_generate_number.clicked.connect(self.generate_auto_id)
        self.add_driver.clicked.connect(self.handle_add_driver)
        self.pushButton_2.clicked.connect(self.show_drivers)
        self.pushButton_3.clicked.connect(self.show_cars)
        self.pushButton_back.clicked.connect(lambda: go_back(self, self.stacked_widget))
    def generate_driver_id(self):
        driver_id = random.randint(100000, 999999)
        self.lineEdit.setText(str(driver_id))
        log_action("Генерация ID водителя", f"Сгенерированный ID: {driver_id}")

    def generate_auto_id(self):
        driver_id = random.randint(100000, 999999)
        self.lineEdit_number_auto.setText(str(driver_id))
        log_action("Генерация номера автомобиля", f"Сгенерированный номер: {driver_id}")

    def show_cars(self):
        if not self.check_db_connection(self.db):
            return

        log_action("Переход к списку автомобилей")
        car_window = CarManagerWindow(self.stacked_widget)
        self.stacked_widget.addWidget(car_window)
        self.stacked_widget.setCurrentWidget(car_window)

    def show_drivers(self):
        if not self.check_db_connection(self.db):
            return

        log_action("Переход к списку водителей")
        driver_window = DriverManagerWindow(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def on_add_car(self):
        license_plate = self.lineEdit_number_auto.text()
        model = self.lineEdit_model.text()
        year = self.lineEdit_year_edit.text()
        car_type = self.comboBox_mark_auto.currentText()
        capacity = self.lineEdit_capicaty.text()
        if not all([license_plate, model, year, car_type, capacity]):
            error_msg = "Заполните все поля для автомобиля!"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка добавления автомобиля", "Не все поля заполнены")
            return
        try:
            year_int = int(year)
            current_year = QtCore.QDate.currentDate().year()
            if year_int > current_year:
                error_msg = f"Год выпуска не может быть больше текущего ({current_year})"
                QMessageBox.warning(self, "Ошибка", error_msg)
                log_action("Ошибка добавления автомобиля", error_msg)
                return

            capacity_int = int(capacity)
        except ValueError:
            error_msg = "Год и вместимость должны быть числами"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления автомобиля", error_msg)
            return

        if not self.check_db_connection(self.db):
            return

        if self.db.add_car(license_plate, model, year, car_type, capacity):
            success_msg = "Автомобиль успешно добавлен"
            QMessageBox.information(self, "Успех", success_msg)
            log_action("Добавление автомобиля",
                       f"Модель: {model}, Год: {year}, Тип: {car_type}, Вместимость: {capacity}, Номер: {license_plate}")
            self.clear_car_fields()
        else:
            error_msg = "Не удалось добавить автомобиль"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления автомобиля", error_msg)

    def handle_add_driver(self):
        full_name = self.lineEdit_name.text()
        driver_id = self.lineEdit.text()
        license_number = self.lineEdit_number.text()
        hire_date = self.dateEdit_hire.date().toString("yyyy-MM-dd")
        if not license_number.startswith("+7") or len(license_number) != 12 or not license_number[1:].isdigit():
            error_msg = "Номер телефона должен быть в формате +7XXXXXXXXXX (10 цифр после +7)"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления водителя", error_msg)
            return

        if not validate_date_input(self, self.dateEdit_hire):
            log_action("Ошибка валидации даты при добавлении водителя")
            return

        if not all([full_name, driver_id, license_number, hire_date]):
            error_msg = "Заполните все поля для водителя!"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка добавления водителя", "Не все поля заполнены")
            return

        if driver_id == "" or driver_id == "Нажмите 'Сгенерировать ID'":
            error_msg = "Сначала сгенерируйте ID водителя"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Попытка добавления водителя", "ID водителя не сгенерирован")
            return

        if not self.check_db_connection(self.db):
            return

        if self.db.add_driver(full_name, driver_id, license_number, hire_date):
            success_msg = "Водитель успешно добавлен"
            QMessageBox.information(self, "Успех", success_msg)
            log_action("Добавление водителя",
                       f"Имя: {full_name}, ID: {driver_id}, Телефон: {license_number}, Дата найма: {hire_date}")
            self.clear_driver_fields()
        else:
            error_msg = "Не удалось добавить водителя"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления водителя", error_msg)

    def clear_car_fields(self):
        self.lineEdit_number_auto.clear()
        self.lineEdit_model.clear()
        self.lineEdit_year_edit.clear()
        self.lineEdit_capicaty.clear()
        self.comboBox_mark_auto.setCurrentIndex(0)

    def clear_driver_fields(self):
        self.lineEdit_name.clear()
        self.lineEdit.clear()
        self.lineEdit.setPlaceholderText("Нажмите 'Сгенерировать ID'")
        self.lineEdit_number.clear()
        self.dateEdit_hire.clear()
    def sizeHint(self):
        return QSize(1000, 700)


class UnitedDriverWindow(QMainWindow, united_driver.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        log_action("Инициализация окна распределения водителей")

        self.btn_back.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.btn_united.clicked.connect(self.distribute_drivers)
        self.btn_ununited.clicked.connect(self.unassign_all_drivers)

        self.assigned_model = QStringListModel()
        self.free_drivers_model = QStringListModel()
        self.free_cars_model = QStringListModel()

        self.listView_united.setModel(self.assigned_model)
        self.listView_free_driver.setModel(self.free_drivers_model)
        self.listView_3.setModel(self.free_cars_model)

        self.update_lists()

    def distribute_drivers(self):
        if not self.check_db_connection(self.db):
            return

        try:
            log_action("Попытка распределения водителей")
            free_drivers = self.db.get_free_drivers()
            free_cars = self.db.get_free_cars()

            if not free_drivers or not free_cars:
                info_msg = "Нет свободных водителей или машин для распределения"
                QMessageBox.information(self, "Информация", info_msg)
                log_action("Распределение водителей", info_msg)
                return

            pairs_count = min(len(free_drivers), len(free_cars))
            success_count = 0

            for i in range(pairs_count):
                if self.db.assign_driver_to_car(free_drivers[i]['driver_id'], free_cars[i]['car_id']):
                    success_count += 1
                    log_action("Назначение водителя на автомобиль",
                               f"Водитель: {free_drivers[i]['full_name']} -> Автомобиль: {free_cars[i]['license_plate']}")

            success_msg = f"Успешно распределено {success_count} водителей по машинам"
            QMessageBox.information(self, "Успех", success_msg)
            log_action("Распределение водителей завершено", success_msg)
            self.update_lists()

        except ValueError as e:
            error_msg = f"Ошибка при распределении водителей: {e}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка распределения водителей", error_msg)

    def unassign_all_drivers(self):
        if not self.check_db_connection(self.db):
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите открепить всех водителей от машин?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                log_action("Попытка открепления всех водителей")
                with self.db._get_cursor() as cursor:
                    cursor.execute("DELETE FROM driver_car_assignments")
                    cursor.execute("UPDATE drivers SET status = 'available' WHERE status = 'on_ride'")

                success_msg = "Все водители откреплены от машин"
                QMessageBox.information(self, "Успех", success_msg)
                log_action("Открепление всех водителей", success_msg)
                self.update_lists()
            except ValueError as e:
                error_msg = f"Ошибка при откреплении водителей: {e}"
                QMessageBox.critical(self, "Ошибка", error_msg)
                log_action("Ошибка открепления водителей", error_msg)

    def update_lists(self):
        if not self.check_db_connection(self.db):
            return

        try:
            log_action("Обновление списков распределения")
            assigned_pairs = self.db.get_assigned_drivers()
            free_drivers = self.db.get_free_drivers()
            free_cars = self.db.get_free_cars()

            assigned_list = [
                f"{pair['full_name']} -> {pair['license_plate']} ({pair['model']})"
                for pair in assigned_pairs
            ]

            free_drivers_list = [
                f"{driver['full_name']} ({driver['license_number']})"
                for driver in free_drivers
            ]

            free_cars_list = [
                f"{car['license_plate']} ({car['model']}, {car['car_type']})"
                for car in free_cars
            ]

            self.assigned_model.setStringList(assigned_list)
            self.free_drivers_model.setStringList(free_drivers_list)
            self.free_cars_model.setStringList(free_cars_list)
            log_action("Списки распределения обновлены",
                       f"Назначено: {len(assigned_pairs)}, Свободных водителей: {len(free_drivers)}, Свободных авто: {len(free_cars)}")

        except ValueError as e:
            error_msg = f"Ошибка при обновлении списков: {e}"
            print(error_msg)
            log_action("Ошибка обновления списков распределения", error_msg)

    def sizeHint(self):
        return QSize(1100, 700)
class FreeDriverWindow(QMainWindow, free_data.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        log_action("Инициализация окна свободных водителей и автомобилей")

        # Инициализация моделей
        self.drivers_model = QStringListModel()
        self.cars_model = QStringListModel()

        # Настройка списков
        self.listView_drivers.setModel(self.drivers_model)
        self.listView_cars.setModel(self.cars_model)

        # Подключение кнопки "Назад"
        self.btn_back.clicked.connect(lambda: go_back(self, self.stacked_widget))

        # Первоначальная загрузка данных
        self.update_lists()
        log_action("Окно свободных водителей и автомобилей готово к работе")

    def sizeHint(self):
        return QSize(900, 500)
    def update_lists(self):
        """Загружает списки свободных водителей и автомобилей"""
        log_action("Обновление списков свободных водителей и автомобилей")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при обновлении списков")
            return

        try:
            # Получаем данные из базы
            free_drivers = self.db.get_free_drivers()
            free_cars = self.db.get_free_cars()
            log_action(f"Получено {len(free_drivers)} свободных водителей и {len(free_cars)} свободных автомобилей")

            # Формируем списки для отображения
            drivers_list = [
                f"{driver['full_name']} (№ прав: {driver['license_number']})"
                for driver in free_drivers
            ] if free_drivers else ["Нет свободных водителей"]

            cars_list = [
                f"{car['license_plate']} - {car['model']} ({car['car_type']})"
                for car in free_cars
            ] if free_cars else ["Нет свободных автомобилей"]

            # Устанавливаем данные в модели
            self.drivers_model.setStringList(drivers_list)
            self.cars_model.setStringList(cars_list)
            log_action("Списки свободных водителей и автомобилей обновлены")

        except ValueError as e:
            error_msg = f"Ошибка при загрузке данных:\n{str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка обновления списков", error_msg)


class TaxiOnTO(QMainWindow, go_to.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.current_items = []
        log_action("Инициализация окна технического обслуживания")

        setup_date_limits(self.dateEdit)
        if not validate_date_input(self, self.dateEdit):
            log_action("Ошибка валидации даты в окне ТО")
            return

        # Настройка валидаторов
        self.setup_validators()

        # Используем carsListView вместо listView
        self.model = QtCore.QStringListModel()
        self.carsListView.setModel(self.model)
        self.carsListView.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Подключаем кнопки
        self.btnBack.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.btnAddMaintenance.clicked.connect(self.add_maintenance)

        # Загрузка данных
        self.load_data()
        log_action("Окно технического обслуживания готово к работе")

    def setup_validators(self):
        """Настройка валидаторов для полей ввода"""
        log_action("Настройка валидаторов в окне ТО")
        # Валидатор для пробега (только цифры, от 0 до 1 000 000 км)
        mileage_validator = QtGui.QIntValidator(0, 1000000, self)
        self.mileageEdit.setValidator(mileage_validator)
        self.mileageEdit.setPlaceholderText("0-1 000 000 км")

        # Валидатор для стоимости (дробные числа с 2 знаками после запятой)
        cost_validator = QtGui.QDoubleValidator(0, 999999.99, 2, self)
        cost_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.costEdit.setValidator(cost_validator)
        self.costEdit.setPlaceholderText("0.00")

    def load_data(self):
        """Загружает список автомобилей с информацией о ТО"""
        log_action("Загрузка данных для окна ТО")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при загрузке данных ТО")
            return

        try:
            cars = self.db.get_cars()
            if not cars:
                self.model.setStringList(["Нет данных об автомобилях"])
                log_action("Нет данных об автомобилях для ТО")
                return

            car_list = []
            self.current_items = cars
            log_action(f"Загружено {len(cars)} автомобилей для ТО")

            for car in cars:
                status = self.db.get_car_current_status(car['car_id'])
                if status and status.get('last_maintenance_date'):
                    info = f"{car['license_plate']} {car['model']} | Последнее ТО: {status['last_maintenance_date']} | Пробег: {status.get('current_mileage', 0)} км"
                else:
                    info = f"{car['license_plate']} {car['model']} | Нет данных о ТО"

                car_list.append(info)

            self.model.setStringList(car_list)

        except Exception as e:
            error_msg = f"Не удалось загрузить данные: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка загрузки данных для ТО", error_msg)

    def on_selection_changed(self):
        """Обрабатывает выбор автомобиля"""
        selected = self.carsListView.selectedIndexes()
        if selected:
            selected_index = selected[0].row()
            if selected_index < len(self.current_items):
                car = self.current_items[selected_index]
                log_action(f"Выбран автомобиль для ТО: {car['license_plate']} {car['model']}")
                self.update_car_info(car)
                self.maintenanceGroup.setEnabled(True)
                self.load_maintenance_history(car['car_id'])

    def update_car_info(self, car):
        """Обновляет информацию о выбранном автомобиле"""
        log_action(f"Обновление информации о выбранном автомобиле: {car['license_plate']}")
        self.mileageEdit.setText(str(car.get('mileage', '')))
        self.dateEdit.setDate(QtCore.QDate.currentDate())

    def load_maintenance_history(self, car_id):
        """Загружает историю ТО для выбранного автомобиля"""
        log_action(f"Загрузка истории ТО для автомобиля с ID: {car_id}")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при загрузке истории ТО")
            return

        try:
            history = self.db.get_maintenance_history(car_id)
            history_model = QtCore.QStringListModel()

            if not history:
                history_model.setStringList(["Нет данных о ТО"])
                log_action(f"Нет истории ТО для автомобиля с ID: {car_id}")
            else:
                history_list = [
                    f"{item['maintenance_date']} - {item['service_type']} ({item['mileage']} км)"
                    for item in history
                ]
                history_model.setStringList(history_list)
                log_action(f"Загружено {len(history)} записей ТО для автомобиля с ID: {car_id}")

            self.historyListView.setModel(history_model)

        except Exception as e:
            error_msg = f"Не удалось загрузить историю ТО: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка загрузки истории ТО", error_msg)

    def add_maintenance(self):
        """Добавляет запись о ТО для выбранного автомобиля"""
        log_action("Попытка добавления записи ТО")
        selected = self.carsListView.selectedIndexes()
        if not selected:
            error_msg = "Выберите автомобиль"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления ТО", error_msg)
            return

        selected_index = selected[0].row()
        if selected_index >= len(self.current_items):
            error_msg = "Неверный индекс автомобиля"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления ТО", error_msg)
            return

        car = self.current_items[selected_index]
        mileage = self.mileageEdit.text()
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        service_type = self.serviceTypeCombo.currentText()
        description = self.descriptionEdit.toPlainText()
        cost = self.costEdit.text() or None

        # Проверка пробега
        if not mileage:
            error_msg = "Введите пробег"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления ТО", error_msg)
            return

        try:
            mileage_int = int(mileage)
            if mileage_int <= 0:
                error_msg = "Пробег должен быть положительным числом"
                QMessageBox.warning(self, "Ошибка", error_msg)
                log_action("Ошибка добавления ТО", error_msg)
                return
        except ValueError:
            error_msg = "Пробег должен быть целым числом"
            QMessageBox.warning(self, "Ошибка", error_msg)
            log_action("Ошибка добавления ТО", error_msg)
            return

        # Проверка стоимости (если введена)
        if cost:
            try:
                cost_float = float(cost)
                if cost_float < 0:
                    error_msg = "Стоимость не может быть отрицательной"
                    QMessageBox.warning(self, "Ошибка", error_msg)
                    log_action("Ошибка добавления ТО", error_msg)
                    return
                if cost_float > 999999.99:
                    error_msg = "Слишком большая стоимость (макс. 999999.99)"
                    QMessageBox.warning(self, "Ошибка", error_msg)
                    log_action("Ошибка добавления ТО", error_msg)
                    return
            except ValueError:
                error_msg = "Некорректный формат стоимости (используйте точку для дробной части)"
                QMessageBox.warning(self, "Ошибка", error_msg)
                log_action("Ошибка добавления ТО", error_msg)
                return

        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при добавлении ТО")
            return

        try:
            if self.db.add_maintenance_record(
                    car['car_id'],
                    date,
                    mileage_int,
                    service_type,
                    description,
                    float(cost) if cost else None
            ):
                success_msg = "Запись о ТО добавлена"
                QMessageBox.information(self, "Успех", success_msg)
                log_action("Добавление записи ТО",
                           f"Автомобиль: {car['license_plate']}, Дата: {date}, Тип: {service_type}, Пробег: {mileage_int}, Стоимость: {cost}")
                self.load_data()
                self.load_maintenance_history(car['car_id'])
            else:
                error_msg = "Не удалось добавить запись"
                QMessageBox.warning(self, "Ошибка", error_msg)
                log_action("Ошибка добавления записи ТО", error_msg)
        except Exception as e:
            error_msg = f"Ошибка при добавлении записи: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка добавления записи ТО", error_msg)
    def sizeHint(self):
        return QSize(1000, 650)

class HistoryTO(QMainWindow, history_to.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        log_action("Инициализация окна истории ТО")

        self.history_model = QStringListModel()
        self.listView_history_to.setModel(self.history_model)
        self.btn_back.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.load_full_maintenance_history()

    def load_full_maintenance_history(self):
        if not self.check_db_connection(self.db):
            return

        try:
            log_action("Загрузка полной истории ТО")
            cars = self.db.get_cars()
            if not cars:
                self.history_model.setStringList(["Нет автомобилей в базе данных"])
                log_action("История ТО", "Нет автомобилей в базе")
                return

            history_list = []

            for car in cars:
                car_info = f"Автомобиль: {car['license_plate']} {car['model']} ({car['car_type']})"
                history_list.append(car_info)
                history_list.append("=" * 50)

                history = self.db.get_maintenance_history(car['car_id'])
                if not history:
                    history_list.append("  Нет записей о ТО")
                else:
                    for record in history:
                        record_str = (
                            f"  Дата: {record['maintenance_date']}\n"
                            f"  Тип: {record['service_type']}\n"
                            f"  Пробег: {record['mileage']} км\n"
                            f"  Описание: {record.get('description', 'нет описания')}"
                        )
                        if record.get('cost'):
                            record_str += f"\n  Стоимость: {record['cost']} руб."
                        history_list.append(record_str)

                history_list.append("")

            self.history_model.setStringList(history_list)
            log_action("История ТО загружена", f"Загружено {len(cars)} автомобилей")

        except Exception as e:
            error_msg = f"Не удалось загрузить историю ТО:\n{str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            log_action("Ошибка загрузки истории ТО", error_msg)
    def sizeHint(self):
        return QSize(1000, 650)


class MainWindow(QMainWindow, main_menu.Ui_MainWindow, BaseWindow):
    def __init__(self, stacked_widget, is_admin=0):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.is_admin = bool(is_admin)
        log_action("Инициализация главного окна", f"Права администратора: {self.is_admin}")

        # Настраиваем интерфейс в зависимости от прав
        if not self.is_admin:
            self.btn_add_data.setVisible(False)
            self.btn_united_auto.setVisible(False)
            self.btn_go_to.setVisible(False)
            log_action("Настройка интерфейса для обычного пользователя")

        self.btn_add_data.clicked.connect(self.show_taxi_park)
        self.btn_taxi_park.clicked.connect(self.show_car_manager)
        self.btn_driver.clicked.connect(self.show_driver_manager)
        self.btn_list_to.clicked.connect(self.history_to)
        self.btn_free_driver.clicked.connect(self.free_driver)
        self.btn_go_to.clicked.connect(self.go_to)
        self.btn_united_auto.clicked.connect(self.united_driver)
        self.btn_exit.clicked.connect(self.close_application)

        self.setWindowTitle("Управление таксопарком")
        log_action("Главное окно готово к работе")

    def show_taxi_park(self):
        log_action("Переход в окно таксопарка")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в таксопарк")
            return

        taxi_park = TaxiParkWindow(self.stacked_widget)
        self.stacked_widget.addWidget(taxi_park)
        self.stacked_widget.setCurrentWidget(taxi_park)

    def show_car_manager(self):
        log_action("Переход в окно управления автомобилями")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в управление автомобилями")
            return

        car_window = CarManagerWindow(self.stacked_widget, self.is_admin)
        self.stacked_widget.addWidget(car_window)
        self.stacked_widget.setCurrentWidget(car_window)

    def show_driver_manager(self):
        log_action("Переход в окно управления водителями")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в управление водителями")
            return

        driver_window = DriverManagerWindow(self.stacked_widget, self.is_admin)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def united_driver(self):
        log_action("Переход в окно распределения водителей")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в распределение водителей")
            return

        driver_window = UnitedDriverWindow(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def close_application(self):
        log_action("Попытка закрытия приложения")
        reply = QMessageBox.question(
            self, 'Подтверждение выхода',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            log_action("Подтверждение выхода из приложения")
            QApplication.instance().quit()
        else:
            log_action("Отмена выхода из приложения")

    def free_driver(self):
        log_action("Переход в окно свободных водителей")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в список свободных водителей")
            return

        driver_window = FreeDriverWindow(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def go_to(self):
        log_action("Переход в окно технического обслуживания")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в ТО")
            return

        driver_window = TaxiOnTO(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def history_to(self):
        log_action("Переход в окно истории ТО")
        if not self.check_db_connection(self.db):
            log_action("Ошибка подключения к БД при переходе в историю ТО")
            return

        driver_window = HistoryTO(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def sizeHint(self):
        return QSize(800, 600)

class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.current_user = None  # Добавляем атрибут для хранения текущего пользователя
        self.stacked_widget = QtWidgets.QStackedWidget()
        db = DatabaseManager()
        log_action("Инициализация приложения")
        if not db.create_database() or not db.create_tables():
            error_msg = "Не удалось инициализировать базу данных"
            QMessageBox.critical(None, "Ошибка", error_msg)
            log_action("Ошибка инициализации БД", error_msg)
            sys.exit(1)

        # Инициализация базы данных для регистрации/авторизации
        auth_db = Database()
        if not auth_db.create_database():
            error_msg = "Не удалось создать базу данных для регистрации"
            QMessageBox.critical(None, "Ошибка", error_msg)
            log_action("Ошибка инициализации БД авторизации", error_msg)
            sys.exit(1)

        load_application_styles(self)
        self.login_window = LoginWindow(self.stacked_widget)
        self.MainWindow = MainWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.login_window)

        # Подключаем обработчик изменения размера
        self.stacked_widget.currentChanged.connect(self.adjust_window_size)
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.show()
        log_action("Приложение успешно запущено")

    def adjust_window_size(self, index):
        """Автоматически подстраивает размер окна под текущий виджет"""
        current_widget = self.stacked_widget.widget(index)
        if current_widget:
            size = current_widget.sizeHint()
            if size.isValid():
                # Добавляем отступы для заголовка окна и границ
                size += QSize(20, 40)
                self.stacked_widget.resize(size)

    def sizeHint(self):
        return QSize(800, 600)


if __name__ == '__main__':
    app = MainApp(sys.argv)
    sys.exit(app.exec())