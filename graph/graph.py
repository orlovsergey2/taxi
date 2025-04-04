# graph.py
import sys
from PySide6 import QtWidgets
from autorization.registration import Database
import main_menu
import window_add
from taxi.taxi_park import DatabaseManager


class TaxiParkWindow(QtWidgets.QMainWindow):
    """Окно управления таксопарком"""

    def __init__(self,parent=None):
        super(TaxiParkWindow, self).__init__(parent)
        self.ui = window_add.Ui_Menu_add()
        self.ui.setupUi(self)
        self.db = DatabaseManager()

        # Настройка интерфейса
        self.LineEdit_date.setPlaceholderText("ГГГГ-ММ-ДД")

        # Подключение кнопок
        self.add_auto.clicked.connect(self.add_car)
        self.pushButton.clicked.connect(self.add_driver)
        self.data_auto.clicked.connect(self.view_cars)
        self.data_auto_2.clicked.connect(self.view_drivers)

        # Настройка формата даты
        self.LineEdit_date.setPlaceholderText("ГГГГ-ММ-ДД")

    def add_car(self):
        """Добавление автомобиля в базу данных"""
        license_plate = self.LineEdit_auto.text().strip()
        model = self.LineEdit_model.text().strip()
        year = self.LineEdit_year.text().strip()
        car_type = self.LineEdit_marka.text().strip()
        capacity = self.LineEdit_capicaty.text().strip()

        if not all([license_plate, model, year, car_type, capacity]):
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            year = int(year)
            capacity = int(capacity)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Год и вместимость должны быть числами")
            return

        # Добавляем автомобиль в базу данных
        success = self.db.add_car(license_plate, model, year, car_type, capacity)
        if success:
            QtWidgets.QMessageBox.information(self, "Успех", "Автомобиль добавлен")
            self.clear_car_fields()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить автомобиль")

    def add_driver(self):
        """Добавление водителя в базу данных"""
        full_name = self.LineEdit_full_name.text().strip()
        license_number = self.id_driver.text().strip()
        phone = self.LineEdit_phone.text().strip()
        hire_date = self.LineEdit_date.text().strip()

        if not all([full_name, license_number, phone, hire_date]):
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        # Добавляем водителя в базу данных
        success = self.db.add_driver(full_name, license_number, phone, hire_date)
        if success:
            QtWidgets.QMessageBox.information(self, "Успех", "Водитель добавлен")
            self.clear_driver_fields()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить водителя")

    def view_cars(self):
        """Просмотр списка автомобилей"""
        cars = self.db.get_cars()
        if cars:
            message = "\n".join([f"{car['license_plate']} - {car['model']}" for car in cars])
            QtWidgets.QMessageBox.information(self, "Автомобили", message)
        else:
            QtWidgets.QMessageBox.information(self, "Автомобили", "Нет данных об автомобилях")

    def view_drivers(self):
        """Просмотр списка водителей"""
        drivers = self.db.get_drivers()
        if drivers:
            message = "\n".join([f"{driver['full_name']} (ID: {driver['driver_id']})" for driver in drivers])
            QtWidgets.QMessageBox.information(self, "Водители", message)
        else:
            QtWidgets.QMessageBox.information(self, "Водители", "Нет данных о водителях")

    def clear_car_fields(self):
        """Очистка полей автомобиля"""
        self.LineEdit_auto.clear()
        self.LineEdit_model.clear()
        self.LineEdit_year.clear()
        self.LineEdit_marka.clear()
        self.LineEdit_capicaty.clear()

    def clear_driver_fields(self):
        """Очистка полей водителя"""
        self.LineEdit_full_name.clear()
        self.id_driver.clear()
        self.LineEdit_phone.clear()
        self.LineEdit_date.clear()


class LoginWindow(QtWidgets.QMainWindow, main_menu.Ui_MainWindow):
    """Окно авторизации с наследованием от сгенерированного UI"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Инициализация баз данных
        self.auth_db = Database()
        self.taxi_db = DatabaseManager()

        # Настройка интерфейса
        self.LineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)

        # Подключение кнопок
        self.enter.clicked.connect(self.on_login)
        self.pushButton.clicked.connect(self.on_register)

        # Проверка инициализации БД
        if not self.auth_db.create_database():
            self.show_error("Ошибка инициализации базы данных")

    def on_login(self):
        login = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not login or not password:
            self.show_error("Введите логин и пароль")
            return

        success, message = self.auth_db.check_credentials(login, password)
        if success:
            self.open_taxi_park()
        else:
            self.show_error(message)

    def on_register(self):
        login = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not login or not password:
            self.show_error("Введите логин и пароль")
            return

        if len(password) < 8:
            self.show_error("Пароль должен содержать минимум 8 символов")
            return

        success, message = self.auth_db.register_user(login, password)
        if success:
            self.show_message("Успех", "Пользователь успешно зарегистрирован")
        else:
            self.show_error(message)

    def open_taxi_park(self):
        """Открытие окна таксопарка"""
        self.taxi_park_window = TaxiParkWindow()
        self.taxi_park_window.show()
        self.close()

    def show_message(self, title, message):
        QtWidgets.QMessageBox.information(self, title, message)

    def show_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Ошибка", message)


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Установка стиля (опционально)
    app.setStyle("Fusion")

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()