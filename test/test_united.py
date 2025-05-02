import pytest
import random
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QStackedWidget, QMessageBox
from PySide6.QtTest import QTest
from graph.graph import UnitedDriverWindow
from confest import qt_app
from taxi.taxi_park import DatabaseManager
from unittest.mock import patch
@pytest.fixture
def test_db():
    """Фикстура для тестовой базы данных"""
    db = DatabaseManager()
    yield db
@pytest.fixture
def united_driver_window(qt_app, test_db):
    """Фикстура для создания и показа окна таксопарка"""
    stacked_widget = QStackedWidget()
    window = UnitedDriverWindow(stacked_widget)
    window.db = test_db
    stacked_widget.addWidget(window)
    stacked_widget.show()
    return window

class TestUnitedDriverWindow:
    def test_initial_state(self, united_driver_window):
        """Проверка начального состояния окна"""
        assert united_driver_window.windowTitle() == "Управление водителями и автомобилями"
        assert united_driver_window.btn_ununited.text() == "Открепить всех водителей"
        assert united_driver_window.btn_united.text() == "Распределить водителей"
        assert united_driver_window.label.text() == "Прикрепление водителей"

    def test_ununited_driver(self, united_driver_window, test_db):
        """Тест открепления водителя"""
        QTest.mouseClick(united_driver_window.btn_ununited, Qt.LeftButton)
        # Проверяем что назначений больше нет
        with test_db._get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM driver_car_assignments")
            assert cursor.fetchone()[0] == 0

    def test_united_driver(self, united_driver_window, test_db):
        """Тест распределения водителя"""
        # Получаем ID свободных водителей и автомобилей
        free_drivers = test_db.get_free_drivers()
        free_cars = test_db.get_free_cars()

        assert len(free_drivers) >= 1
        assert len(free_cars) >= 1

        # Распределяем водителей
        with patch.object(QMessageBox, 'information') as mock_msg:
            QTest.mouseClick(united_driver_window.btn_united, Qt.LeftButton)
            mock_msg.assert_called_once()

        # Проверяем что появилось назначение
        assigned_drivers = test_db.get_assigned_drivers()
        assert len(assigned_drivers) == min(len(free_drivers), len(free_cars))

        # Проверяем что статус водителя изменился
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT status FROM drivers WHERE driver_id = %s",
                           (assigned_drivers[0]['driver_id'],))
            assert cursor.fetchone()['status'] == 'on_ride'
