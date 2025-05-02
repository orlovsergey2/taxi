import pytest
import random
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QStackedWidget, QMessageBox
from PySide6.QtTest import QTest
from graph.graph import TaxiParkWindow
from confest import qt_app
from taxi.taxi_park import DatabaseManager
from unittest.mock import patch


@pytest.fixture
def test_db():
    """Фикстура для тестовой базы данных"""
    db = DatabaseManager()
    yield db
    # Очищаем тестовые данные после тестов
    '''with db._get_cursor() as cursor:
        cursor.execute("DELETE FROM cars WHERE model LIKE 'TestModel%'")
        cursor.execute("DELETE FROM drivers WHERE full_name LIKE 'Test Driver%'")'''


@pytest.fixture
def taxi_park_window(qt_app, test_db):
    """Фикстура для создания и показа окна таксопарка"""
    stacked_widget = QStackedWidget()
    window = TaxiParkWindow(stacked_widget)
    window.db = test_db
    stacked_widget.addWidget(window)
    stacked_widget.show()
    return window


class TestTaxiParkWindow:
    def test_initial_state(self, taxi_park_window):
        """Проверка начального состояния окна"""
        assert taxi_park_window.windowTitle() == "Таксопарк"
        assert taxi_park_window.lineEdit_number_auto.placeholderText() == "Нажмите 'Сгенерировать номер'"
        assert taxi_park_window.lineEdit.placeholderText() == "Нажмите 'Сгенерировать ID'"
        assert taxi_park_window.lineEdit_number.placeholderText() == "+7XXXXXXXXXX"
        assert taxi_park_window.dateEdit_hire.date() == QDate.currentDate()

    def test_generate_auto_id(self, taxi_park_window):
        """Тест генерации номера автомобиля"""
        QTest.mouseClick(taxi_park_window.btn_generate_number, Qt.LeftButton)
        license_plate = taxi_park_window.lineEdit_number_auto.text()
        assert license_plate.isdigit()
        assert len(license_plate) == 6

    def test_generate_driver_id(self, taxi_park_window):
        """Тест генерации ID водителя"""
        QTest.mouseClick(taxi_park_window.btn_generate_id, Qt.LeftButton)
        driver_id = taxi_park_window.lineEdit.text()
        assert driver_id.isdigit()
        assert len(driver_id) == 6

    def test_add_car(self, taxi_park_window, test_db):
        """Тест добавления автомобиля"""
        # Генерируем номер
        QTest.mouseClick(taxi_park_window.btn_generate_number, Qt.LeftButton)
        license_plate = taxi_park_window.lineEdit_number_auto.text()

        # Заполняем тестовые данные
        test_model = f"TestModel_{random.randint(1000, 9999)}"
        taxi_park_window.lineEdit_model.setText(test_model)
        taxi_park_window.lineEdit_year_edit.setText("2020")
        taxi_park_window.comboBox_mark_auto.setCurrentText("sedan")
        taxi_park_window.lineEdit_capicaty.setText("5")

        # Мокаем QMessageBox для проверки успешного добавления
        with patch.object(QMessageBox, 'information') as mock_msg:
            QTest.mouseClick(taxi_park_window.add_auto, Qt.LeftButton)
            mock_msg.assert_called_once()

        # Проверяем что автомобиль добавился в базу
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM cars WHERE model = %s", (test_model,))
            test_car = cursor.fetchone()

        assert test_car is not None
        assert str(test_car['year']) == "2020"  # Проверяем как строку
        assert test_car['license_plate'] == license_plate
        assert test_car['car_type'] == "sedan"
        assert str(test_car['capacity']) == "5"

    def test_add_driver(self, taxi_park_window, test_db):
        """Тест добавления водителя"""
        # Генерируем ID
        QTest.mouseClick(taxi_park_window.btn_generate_id, Qt.LeftButton)
        driver_id = taxi_park_window.lineEdit.text()

        # Заполняем тестовые данные
        test_name = f"Test Driver {random.randint(1000, 9999)}"
        taxi_park_window.lineEdit_name.setText(test_name)
        taxi_park_window.lineEdit_number.setText("+79998887766")
        taxi_park_window.dateEdit_hire.setDate(QDate(2020, 1, 15))

        # Мокаем QMessageBox для проверки успешного добавления
        with patch.object(QMessageBox, 'information') as mock_msg:
            QTest.mouseClick(taxi_park_window.add_driver, Qt.LeftButton)
            mock_msg.assert_called_once()

        # Проверяем что водитель добавился в базу
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM drivers WHERE full_name = %s", (test_name,))
            test_driver = cursor.fetchone()

        assert test_driver is not None
        assert test_driver['phone'] == "+79998887766"
        assert test_driver['hire_date'].strftime("%Y-%m-%d") == "2020-01-15"

    def test_invalid_car_data(self, taxi_park_window):
        """Тест валидации данных автомобиля"""
        with patch.object(QMessageBox, 'warning') as mock_msg:
            QTest.mouseClick(taxi_park_window.add_auto, Qt.LeftButton)
            mock_msg.assert_called_once()

    def test_invalid_driver_data(self, taxi_park_window):
        """Тест валидации данных водителя"""
        with patch.object(QMessageBox, 'warning') as mock_msg:
            QTest.mouseClick(taxi_park_window.add_driver, Qt.LeftButton)
            mock_msg.assert_called_once()

    def test_navigation_buttons(self, taxi_park_window):
        """Тест кнопок навигации"""
        with patch.object(taxi_park_window, 'show_cars') as mock_show_cars:
            QTest.mouseClick(taxi_park_window.pushButton_3, Qt.LeftButton)
            mock_show_cars.assert_called_once()

        with patch.object(taxi_park_window, 'show_drivers') as mock_show_drivers:
            QTest.mouseClick(taxi_park_window.pushButton_2, Qt.LeftButton)
            mock_show_drivers.assert_called_once()