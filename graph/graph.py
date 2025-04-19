# graph.py
import sys
from aifc import Error

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, QStringListModel
from PySide6.QtWidgets import (QApplication, QMessageBox, QMainWindow)
from autorization.registration import Database
from ui import autorization, main_menu, list_auto, list_driver, united_driver, free_data, go_to, history_to
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
def go_back(widget, stacked_widget):
    """Глобальная функция для возврата в предыдущее окно"""
    stacked_widget.setCurrentIndex(1)
    stacked_widget.removeWidget(widget)
    widget.deleteLater()

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
        return QSize(800, 600)

    def handle_login(self):
        username = self.LineEdit.text().strip()
        password = self.LineEdit_2.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        success, message, is_admin = self.db.check_credentials(username, password)
        if success:
            self.MainWindow = MainWindow(self.stacked_widget, is_admin=bool(is_admin))
            self.stacked_widget.addWidget(self.MainWindow)
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
    def __init__(self, stacked_widget, is_admin=0):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.current_items = []
        self.is_admin = is_admin
        self.model = QtCore.QStringListModel()
        self.listView.setModel(self.model)
        if not self.is_admin:
            self.btn_del_auto.setVisible(False)
        self.btn_del_auto.clicked.connect(self.delete_selected_car)
        self.exit.clicked.connect(lambda: go_back(self, self.stacked_widget))

        self.load_data_car()

    def sizeHint(self):
        return QSize(800, 600)

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
        if not self.is_admin:
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для выполнения этой операции")
            return
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
    def __init__(self, stacked_widget, is_admin=0):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.is_admin = is_admin
        self.model = QtCore.QStringListModel()
        self.listView.setModel(self.model)
        if not self.is_admin:
            self.btn_del_driver.setVisible(False)
        self.btn_del_driver.clicked.connect(self.delete_selected_driver)
        self.exit.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.setup_context_menu()
        self.load_driver_data()

    def sizeHint(self):
        return QSize(800, 600)

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
        if not self.is_admin:
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для выполнения этой операции")
            return
        selected = self.listView.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите водителя для удаления")
            return

        selected_index = selected[0].row()
        drivers = self.db.get_drivers()

        if selected_index >= len(drivers):
            QMessageBox.warning(self, "Ошибка", "Неверный индекс выбранного водителя")
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
                    QMessageBox.information(self, "Успех", "Водитель успешно удален")
                else:
                    QMessageBox.critical(self, "Ошибка",
                                         "Не удалось удалить водителя (возможно, он назначен к автомобилю)")
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
        self.pushButton_back.clicked.connect(lambda: go_back(self, self.stacked_widget))

    def sizeHint(self):
        return QSize(1000, 700)

    def generate_driver_id(self):
        driver_id = random.randint(100000, 999999)
        self.lineEdit.setText(str(driver_id))

    def generate_auto_id(self):
        driver_id = random.randint(100000, 999999)
        self.lineEdit_number_auto.setText(str(driver_id))

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
        hire_date = self.dateEdit_hire.text()

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


class UnitedDriverWindow(QMainWindow, united_driver.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()

        self.btn_back.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.btn_united.clicked.connect(self.distribute_drivers)
        self.btn_ununited.clicked.connect(self.unassign_all_drivers)

        # Инициализация моделей для списков
        self.assigned_model = QStringListModel()
        self.free_drivers_model = QStringListModel()
        self.free_cars_model = QStringListModel()

        self.listView_united.setModel(self.assigned_model)
        self.listView_free_driver.setModel(self.free_drivers_model)
        self.listView_3.setModel(self.free_cars_model)

        self.update_lists()

    def distribute_drivers(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        try:
            # Получаем свободных водителей и машины
            free_drivers = self.db.get_free_drivers()
            free_cars = self.db.get_free_cars()

            if not free_drivers or not free_cars:
                QMessageBox.information(self, "Информация",
                                        "Нет свободных водителей или машин для распределения")
                return

            # Определяем сколько пар можно создать
            pairs_count = min(len(free_drivers), len(free_cars))

            # Прикрепляем водителей к машинам
            success_count = 0
            for i in range(pairs_count):
                if self.db.assign_driver_to_car(free_drivers[i]['driver_id'], free_cars[i]['car_id']):
                    success_count += 1

            QMessageBox.information(self, "Успех",
                                    f"Успешно распределено {success_count} водителей по машинам")

            # Обновляем списки
            self.update_lists()

        except Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при распределении водителей: {e}")
        finally:
            if self.db.connection.is_connected():
                self.db.connection.close()

    def unassign_all_drivers(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите открепить всех водителей от машин?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor = self.db.connection.cursor()
                # Удаляем все назначения
                cursor.execute("DELETE FROM driver_car_assignments")
                # Возвращаем всех водителей в статус 'available'
                cursor.execute("UPDATE drivers SET status = 'available' WHERE status = 'on_ride'")
                self.db.connection.commit()

                QMessageBox.information(self, "Успех", "Все водители откреплены от машин")
                self.update_lists()
            except Error as e:
                self.db.connection.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при откреплении водителей: {e}")
            finally:
                if self.db.connection.is_connected():
                    self.db.connection.close()

    def update_lists(self):
        if not self.db.connect():
            return

        try:
            # Получаем данные из базы
            assigned_pairs = self.db.get_assigned_drivers()
            free_drivers = self.db.get_free_drivers()
            free_cars = self.db.get_free_cars()

            # Формируем списки для отображения
            assigned_list = [
                f"{pair['full_name']} -> {pair['license_plate']} ({pair['model']})"
                for pair in assigned_pairs
            ]

            free_drivers_list = [f"{driver['full_name']} ({driver['license_number']})"
                                 for driver in free_drivers]

            free_cars_list = [
                f"{car['license_plate']} ({car['model']}, {car['car_type']})"
                for car in free_cars
            ]

            # Устанавливаем данные в модели
            self.assigned_model.setStringList(assigned_list)
            self.free_drivers_model.setStringList(free_drivers_list)
            self.free_cars_model.setStringList(free_cars_list)

        except Error as e:
            print(f"Ошибка при обновлении списков: {e}")
        finally:
            if self.db.connection.is_connected():
                self.db.connection.close()

    def sizeHint(self):
        return QSize(1100, 700)


class FreeDriverWindow(QMainWindow, free_data.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()

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

    def sizeHint(self):
        return QSize(900, 500)

    def update_lists(self):
        """Загружает списки свободных водителей и автомобилей"""
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        try:
            # Получаем данные из базы
            free_drivers = self.db.get_free_drivers()
            free_cars = self.db.get_free_cars()

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

        except Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных:\n{str(e)}")
        finally:
            if self.db.connection and self.db.connection.is_connected():
                self.db.connection.close()


class TaxiOnTO(QMainWindow, go_to.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.current_items = []

        # Используем carsListView вместо listView
        self.model = QtCore.QStringListModel()
        self.carsListView.setModel(self.model)  # Изменено с listView на carsListView
        self.carsListView.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Подключаем кнопки
        self.btnBack.clicked.connect(lambda: go_back(self, self.stacked_widget))
        self.btnAddMaintenance.clicked.connect(self.add_maintenance)

        # Загрузка данных
        self.load_data()

    def load_data(self):
        """Загружает список автомобилей с информацией о ТО"""
        try:
            cars = self.db.get_cars()
            if not cars:
                self.model.setStringList(["Нет данных об автомобилях"])
                return

            car_list = []
            self.current_items = cars

            for car in cars:
                status = self.db.get_car_current_status(car['car_id'])
                if status and status.get('last_maintenance_date'):
                    info = f"{car['license_plate']} {car['model']} | Последнее ТО: {status['last_maintenance_date']} | Пробег: {status.get('current_mileage', 0)} км"
                else:
                    info = f"{car['license_plate']} {car['model']} | Нет данных о ТО"

                car_list.append(info)

            self.model.setStringList(car_list)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def on_selection_changed(self):
        """Обрабатывает выбор автомобиля"""
        selected = self.carsListView.selectedIndexes()  # Изменено с listView на carsListView
        if selected:
            selected_index = selected[0].row()
            if selected_index < len(self.current_items):
                car = self.current_items[selected_index]
                self.update_car_info(car)
                self.maintenanceGroup.setEnabled(True)  # Активируем группу ТО
                self.load_maintenance_history(car['car_id'])

    def update_car_info(self, car):
        """Обновляет информацию о выбранном автомобиле"""
        self.mileageEdit.setText(str(car.get('mileage', '')))
        self.dateEdit.setDate(QtCore.QDate.currentDate())

    def load_maintenance_history(self, car_id):
        """Загружает историю ТО для выбранного автомобиля"""
        try:
            history = self.db.get_maintenance_history(car_id)
            history_model = QtCore.QStringListModel()

            if not history:
                history_model.setStringList(["Нет данных о ТО"])
            else:
                history_list = [
                    f"{item['maintenance_date']} - {item['service_type']} ({item['mileage']} км)"
                    for item in history
                ]
                history_model.setStringList(history_list)

            self.historyListView.setModel(history_model)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю ТО: {str(e)}")

    def add_maintenance(self):
        """Добавляет запись о ТО для выбранного автомобиля"""
        selected = self.carsListView.selectedIndexes()  # Изменено с listView на carsListView
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите автомобиль")
            return

        selected_index = selected[0].row()
        if selected_index >= len(self.current_items):
            QMessageBox.warning(self, "Ошибка", "Неверный индекс автомобиля")
            return

        car = self.current_items[selected_index]
        mileage = self.mileageEdit.text()
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        service_type = self.serviceTypeCombo.currentText()
        description = self.descriptionEdit.toPlainText()
        cost = self.costEdit.text() or None

        if not mileage:
            QMessageBox.warning(self, "Ошибка", "Введите пробег")
            return

        try:
            mileage = int(mileage)
            if self.db.add_maintenance_record(
                    car['car_id'],
                    date,
                    mileage,
                    service_type,
                    description,
                    float(cost) if cost else None
            ):
                QMessageBox.information(self, "Успех", "Запись о ТО добавлена")
                self.load_data()
                self.load_maintenance_history(car['car_id'])
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить запись")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность введенных данных")

class HistoryTO(QMainWindow, history_to.Ui_MainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()

        # Инициализация модели для списка истории ТО
        self.history_model = QStringListModel()
        self.listView_history_to.setModel(self.history_model)

        # Подключение кнопки "Назад"
        self.btn_back.clicked.connect(lambda: go_back(self, self.stacked_widget))

        # Загрузка данных при инициализации
        self.load_full_maintenance_history()

    def load_full_maintenance_history(self):
        """Загружает полную историю ТО для всех автомобилей"""
        try:
            # Получаем все автомобили
            cars = self.db.get_cars()
            if not cars:
                self.history_model.setStringList(["Нет автомобилей в базе данных"])
                return

            history_list = []

            # Для каждого автомобиля получаем историю ТО
            for car in cars:
                car_info = f"Автомобиль: {car['license_plate']} {car['model']} ({car['car_type']})"
                history_list.append(car_info)
                history_list.append("=" * 50)  # Разделитель

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

                history_list.append("")  # Пустая строка между автомобилями

            self.history_model.setStringList(history_list)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю ТО:\n{str(e)}")
    def sizeHint(self):
        return QSize(1000, 650)

class MainWindow(QMainWindow, main_menu.Ui_MainWindow):
    def __init__(self, stacked_widget,is_admin=0):
        super().__init__()
        self.setupUi(self)
        self.stacked_widget = stacked_widget
        self.db = DatabaseManager()
        self.is_admin = bool(is_admin)
        print(f"MainWindow is_admin: {self.is_admin}")
        # Настраиваем интерфейс в зависимости от прав
        if not self.is_admin:
            self.btn_add_data.setVisible(False)
            self.btn_united_auto.setVisible(False)
            self.btn_go_to.setVisible(False)
        self.btn_add_data.clicked.connect(self.show_taxi_park)
        self.btn_taxi_park.clicked.connect(self.show_car_manager)
        self.btn_driver.clicked.connect(self.show_driver_manager)
        self.btn_list_to.clicked.connect(self.history_to)
        self.btn_free_driver.clicked.connect(self.free_driver)
        self.btn_go_to.clicked.connect(self.go_to)
        self.btn_united_auto.clicked.connect(self.united_driver)
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

        car_window = CarManagerWindow(self.stacked_widget, self.is_admin)
        self.stacked_widget.addWidget(car_window)
        self.stacked_widget.setCurrentWidget(car_window)

    def show_driver_manager(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        driver_window = DriverManagerWindow(self.stacked_widget, self.is_admin)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)
    def united_driver(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        driver_window = UnitedDriverWindow(self.stacked_widget)
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
    def free_driver(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        driver_window = FreeDriverWindow(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)
    def go_to(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        driver_window = TaxiOnTO(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)
    def history_to(self):
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        driver_window = HistoryTO(self.stacked_widget)
        self.stacked_widget.addWidget(driver_window)
        self.stacked_widget.setCurrentWidget(driver_window)

class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.stacked_widget = QtWidgets.QStackedWidget()
        db = DatabaseManager()
        if not db.create_database() or not db.create_tables():
            QMessageBox.critical(None, "Ошибка", "Не удалось инициализировать базу данных")
            sys.exit(1)
        # Инициализация базы данных для регистрации/авторизации
        auth_db = Database()
        if not auth_db.create_database():
            QMessageBox.critical(None, "Ошибка", "Не удалось создать базу данных для регистрации")
            sys.exit(1)
        load_application_styles(self)
        self.login_window = LoginWindow(self.stacked_widget)
        self.MainWindow = MainWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.login_window)
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
    def sizeHint(self):
        return QSize(800, 600)

if __name__ == '__main__':
    app = MainApp(sys.argv)
    sys.exit(app.exec())