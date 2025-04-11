# graph.py
import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QApplication, QMessageBox, QMainWindow)
from autorization.registration import Database
from ui import autorization, main_menu, list_auto, list_driver
from ui.windows_add import Ui_Form
from taxi.taxi_park import DatabaseManager
import random


def load_application_styles(app):
    """Загружает стили из конкретного расположения"""
    style_path = r"D:\taxi\style\styles.qss"
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        return True
    except Exception as e:
        print(f"Ошибка загрузки стилей: {e}")
        return False


class LoginWindow(QMainWindow, autorization.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = Database()
        self.LineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.enter.clicked.connect(self.handle_login)
        self.pushButton.clicked.connect(self.handle_register)

    def sizeHint(self):
        return QSize(400, 300)

    def handle_login(self):
        username = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        success, message = self.db.check_credentials(username, password)
        if success:
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Ошибка", message)

    def handle_register(self):
        username = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 8 символов")
            return

        success, message = self.db.register_user(username, password)
        if success:
            QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован")
        else:
            QMessageBox.warning(self, "Ошибка", message)


class CarManagerWindow(QtWidgets.QMainWindow, list_auto.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.current_items = []

        self.model = QtCore.QStringListModel()
        self.listView.setModel(self.model)

        self.btn_del_auto.clicked.connect(self.delete_selected_car)
        self.exit.clicked.connect(self.go_back)

        self.load_data_car()

    def sizeHint(self):
        return QSize(800, 600)

    def go_back(self):
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.removeWidget(self)
        self.deleteLater()

    def load_data_car(self):
        try:
            items = self.db.get_cars()
            if not items:
                self.model.setStringList(["Нет данных об автомобилях"])
                return

            item_list = [
                f"{car['license_plate']} {car['model']} ({car['car_type']})"
                for car in items
            ]

            self.model.setStringList(item_list)
            self.current_items = items

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные:\n{str(e)}"
            )
            self.current_items = []

    def delete_selected_car(self):
        selected = self.listView.selectedIndexes()
        if not selected:
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка",
                "Выберите автомобиль для удаления"
            )
            return

        try:
            selected_index = selected[0].row()
            if selected_index >= len(self.current_items):
                QtWidgets.QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Неверный индекс выбранного автомобиля"
                )
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
                    QtWidgets.QMessageBox.information(
                        self,
                        "Успех",
                        "Автомобиль успешно удален"
                    )
                    self.load_data_car()
                else:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось удалить автомобиль"
                    )

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при удалении автомобиля:\n{str(e)}"
            )


class DriverManagerWindow(QMainWindow, list_driver.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()

        self.model = QtCore.QStringListModel()
        self.listView.setModel(self.model)

        self.btn_del_driver.clicked.connect(self.delete_selected_driver)
        self.exit.clicked.connect(self.go_back)
        self.setup_context_menu()
        self.load_driver_data()

    def sizeHint(self):
        return QSize(800, 600)

    def go_back(self):
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.removeWidget(self)
        self.deleteLater()

    def setup_context_menu(self):
        self.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listView.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Удалить")
        refresh_action = menu.addAction("Обновить список")

        action = menu.exec_(self.listView.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_driver()
        elif action == refresh_action:
            self.load_driver_data()

    def load_driver_data(self):
        try:
            drivers = self.db.get_drivers()
            driver_list = []

            if not drivers:
                driver_list.append("Нет данных о водителях")
            else:
                for driver in drivers:
                    driver_info = f"{driver['full_name']} (№ прав: {driver['license_number']}), тел.: {driver['phone']}"
                    driver_list.append(driver_info)

            self.model.setStringList(driver_list)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")

    def delete_selected_driver(self):
        selected = self.listView.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите водителя для удаления")
            return

        selected_index = selected[0]
        driver_info = selected_index.data()

        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить водителя:\n{driver_info}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                driver_id = ...  # Получить ID из driver_info
                if self.db.delete_driver(driver_id):
                    self.load_driver_data()
                    QMessageBox.information(self, "Успех", "Водитель успешно удален")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить водителя")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении:\n{str(e)}")


class TaxiParkWindow(QMainWindow, Ui_Form):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()

        self.add_auto.clicked.connect(self.on_add_car)
        self.btn_generate_id.clicked.connect(self.generate_driver_id)
        self.btn_generate_number.clicked.connect(self.generate_auto_id)
        self.add_driver.clicked.connect(self.handle_add_driver)
        self.pushButton_2.clicked.connect(self.show_drivers)
        self.pushButton_3.clicked.connect(self.show_cars)
        self.pushButton_back.clicked.connect(self.go_back)

    def sizeHint(self):
        return QSize(1000, 700)

    def generate_driver_id(self):
        driver_id = random.randint(100000, 999999)
        self.lineEdit.setText(str(driver_id))

    def generate_auto_id(self):
        driver_id = random.randint(100000, 999999)
        self.lineEdit_number_auto.setText(str(driver_id))

    def go_back(self):
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.removeWidget(self)
        self.deleteLater()

    def show_cars(self):
        car_window = CarManagerWindow(self.stacked_widget)
        self.stacked_widget.addWidget(car_window)
        self.stacked_widget.setCurrentWidget(car_window)

    def show_drivers(self):
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
            QMessageBox.warning(self, "Ошибка", "Заполните все поля для автомобиля!")
            return

        try:
            year = int(year)
            capacity = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Год и вместимость должны быть числами")
            return

        if self.db.add_car(license_plate, model, year, car_type, capacity):
            QMessageBox.information(self, "Успех", "Автомобиль успешно добавлен")
            self.clear_car_fields()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить автомобиль")

    def handle_add_driver(self):
        full_name = self.lineEdit_name.text()
        driver_id = self.lineEdit.text()
        license_number = self.lineEdit_number.text()
        hire_date = self.lineEdit_date.text()

        if not all([full_name, driver_id, license_number, hire_date]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля для водителя!")
            return

        if driver_id == "" or driver_id == "Нажмите 'Сгенерировать ID'":
            QMessageBox.warning(self, "Ошибка", "Сначала сгенерируйте ID водителя")
            return

        if self.db.add_driver(full_name, driver_id, license_number, hire_date):
            QMessageBox.information(self, "Успех", "Водитель успешно добавлен")
            self.clear_driver_fields()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить водителя")

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
        self.lineEdit_date.clear()


class MainWindow(QMainWindow, main_menu.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()

        self.btn_add_data.clicked.connect(self.show_taxi_park)
        self.btn_taxi_park.clicked.connect(self.show_car_manager)
        self.btn_driver.clicked.connect(self.show_driver_manager)
        self.btn_list_drive.clicked.connect(self.show_driver_manager)
        self.btn_free_driver.clicked.connect(self.show_driver_manager)
        self.btn_free_auto.clicked.connect(self.show_driver_manager)
        self.btn_united_auto.clicked.connect(self.show_driver_manager)
        self.btn_exit.clicked.connect(self.close_application)

        self.setWindowTitle("Управление таксопарком")

    def sizeHint(self):
        return QSize(800, 600)

    def show_taxi_park(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        taxi_park = TaxiParkWindow(self.stacked_widget)
        self.stacked_widget.addWidget(taxi_park)
        self.stacked_widget.setCurrentWidget(taxi_park)

    def show_car_manager(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        car_window = CarManagerWindow(self.stacked_widget)
        self.stacked_widget.addWidget(car_window)
        self.stacked_widget.setCurrentWidget(car_window)

    def show_driver_manager(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        driver_window = DriverManagerWindow(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

    def close_application(self):
        reply = QMessageBox.question(
            self, 'Подтверждение выхода',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            QApplication.instance().quit()


class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.stacked_widget = QtWidgets.QStackedWidget()
        db = DatabaseManager()
        if not db.create_database() or not db.create_tables():
            QMessageBox.critical(None, "Ошибка", "Не удалось инициализировать базу данных")
            sys.exit(1)
        load_application_styles(self)
        self.login_window = LoginWindow(self.stacked_widget)
        self.MainWindow = MainWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.MainWindow)
        # Подключаем обработчик изменения размера
        self.stacked_widget.currentChanged.connect(self.adjust_window_size)
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.show()
    def adjust_window_size(self, index):
        """Автоматически подстраивает размер окна под текущий виджет"""
        current_widget = self.stacked_widget.widget(index)
        if current_widget:
            size = current_widget.sizeHint()
            if size.isValid():
                # Добавляем отступы для заголовка окна и границ
                size += QSize(20, 40)
                self.stacked_widget.resize(size)


if __name__ == '__main__':
    app = MainApp(sys.argv)
    sys.exit(app.exec())