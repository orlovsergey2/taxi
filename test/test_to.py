import pytest
import random
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QStackedWidget, QMessageBox
from PySide6.QtTest import QTest
from graph.graph import TaxiOnTO
from confest import qt_app
from taxi.taxi_park import DatabaseManager
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_db():
    """Фикстура для тестовой базы данных с тестовыми автомобилями"""
    db = DatabaseManager()

    # Проверяем есть ли автомобили в базе, если нет - добавляем
    with db._get_cursor(dictionary=True) as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM cars")
        if cursor.fetchone()['count'] == 0:
            cursor.execute("""
                INSERT INTO cars (license_plate, model, year, car_type, capacity, mileage)
                VALUES 
                    ('test Toyota Camry', 2020, 'sedan', 4, 50000),
                    ('test Hyundai Solaris', 2021, 'sedan', 4, 30000),
                    ('test Kia Rio', 2019, 'sedan', 4, 70000)
            """)
    yield db

    # Очищаем тестовые данные (если нужно)
    with db._get_cursor() as cursor:
         cursor.execute("DELETE FROM maintenance_history WHERE car_id IN (SELECT car_id FROM cars WHERE model LIKE 'test%')")
         cursor.execute("DELETE FROM cars WHERE model LIKE 'test%'")


@pytest.fixture
def taxi_on_to(qt_app, test_db):
    """Фикстура для создания и показа окна ТО"""
    stacked_widget = QStackedWidget()
    window = TaxiOnTO(stacked_widget)
    window.db = test_db

    # Мокаем метод load_maintenance_history для тестов
    window.load_maintenance_history = MagicMock()

    stacked_widget.addWidget(window)
    stacked_widget.show()

    # Даем время на загрузку данных
    QTest.qWait(500)
    return window


class TestTaxiOnTO:
    def test_initial_state(self, taxi_on_to):
        """Проверка начального состояния окна"""
        assert taxi_on_to.carsGroup.title() == "Список автомобилей"
        assert taxi_on_to.maintenanceGroup.title() == "Техническое обслуживание"
        assert taxi_on_to.dateLabel.text() == "Дата ТО:"
        assert taxi_on_to.mileageLabel.text() == "Пробег (км):"
        assert taxi_on_to.typeLabel.text() == "Тип обслуживания:"
        assert taxi_on_to.descLabel.text() == "Описание работ:"
        assert taxi_on_to.costLabel.text() == "Стоимость:"

        # Проверяем что список автомобилей загружен
        assert taxi_on_to.model.rowCount() > 0

    def test_add_maintenance_random_car(self, taxi_on_to, test_db):
        """Тест добавления записи ТО с полной проверкой данных"""
        # 1. Подготовка тестовых данных
        car_count = taxi_on_to.model.rowCount()
        if car_count == 0:
            pytest.skip("Нет автомобилей для тестирования")

        # Выбираем первый автомобиль для стабильности теста
        selected_car = taxi_on_to.current_items[0]
        taxi_on_to.carsListView.setCurrentIndex(taxi_on_to.model.index(0))

        # Получаем текущие данные автомобиля
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT mileage, last_maintenance 
                FROM cars 
                WHERE car_id = %s
            """, (selected_car['car_id'],))
            car_data = cursor.fetchone()
            initial_mileage = car_data['mileage'] if car_data else 0

        print(f"\nТестируем автомобиль {selected_car['license_plate']} (ID: {selected_car['car_id']})")
        print(f"Начальный пробег: {initial_mileage} км")

        # 2. Устанавливаем тестовые значения
        test_mileage = initial_mileage + 5000  # Фиксированное увеличение
        test_date = QDate.currentDate().addDays(-7)  # Фиксированная дата (неделю назад)
        test_service_type = "Регламентное"
        test_description = "Тестовое ТО"
        test_cost = 10000.00

        # 3. Заполняем форму
        taxi_on_to.mileageEdit.setText(str(test_mileage))
        taxi_on_to.dateEdit.setDate(test_date)
        taxi_on_to.serviceTypeCombo.setCurrentText(test_service_type)
        taxi_on_to.descriptionEdit.setPlainText(test_description)
        taxi_on_to.costEdit.setText(str(test_cost))

        # 4. Добавляем запись ТО
        with patch.object(QMessageBox, 'information') as mock_msg:
            QTest.mouseClick(taxi_on_to.btnAddMaintenance, Qt.LeftButton)
            mock_msg.assert_called_once()

        # 5. Проверяем результат в новой транзакции
        with test_db._get_cursor(dictionary=True) as cursor:
            # 5.1 Проверяем запись в истории ТО
            cursor.execute("""
                SELECT * FROM maintenance_history
                WHERE car_id = %s
                ORDER BY maintenance_date DESC, maintenance_id DESC
                LIMIT 1
            """, (selected_car['car_id'],))

            maintenance_record = cursor.fetchone()
            assert maintenance_record is not None, "Запись ТО не добавлена в БД"

            print(f"\nДобавленная запись ТО:")
            print(f"- ID: {maintenance_record['maintenance_id']}")
            print(f"- Пробег: {maintenance_record['mileage']} км")
            print(f"- Тип: {maintenance_record['service_type']}")
            print(f"- Дата: {maintenance_record['maintenance_date']}")
            print(f"- Описание: {maintenance_record['description']}")
            print(f"- Стоимость: {maintenance_record['cost']} руб.")

            # Проверяем соответствие данных
            assert maintenance_record['mileage'] == test_mileage, "Несоответствие пробега"
            assert maintenance_record['service_type'] == test_service_type, "Несоответствие типа ТО"
            assert maintenance_record['description'] == test_description, "Несоответствие описания"
            assert float(maintenance_record['cost']) == test_cost, "Несоответствие стоимости"
            assert str(maintenance_record['maintenance_date']) == test_date.toString(
                "yyyy-MM-dd"), "Несоответствие даты"

            # 5.2 Проверяем обновление данных автомобиля
            cursor.execute("""
                SELECT mileage, last_maintenance 
                FROM cars 
                WHERE car_id = %s
            """, (selected_car['car_id'],))

            updated_car = cursor.fetchone()
            assert updated_car is not None, "Данные автомобиля не найдены"

            print(f"\nОбновленные данные автомобиля:")
            print(f"- Пробег: {updated_car['mileage']} км")
            print(f"- Дата последнего ТО: {updated_car['last_maintenance']}")

            assert updated_car['mileage'] == test_mileage, "Пробег автомобиля не обновился"
            assert str(updated_car['last_maintenance']) == test_date.toString("yyyy-MM-dd"), "Дата ТО не обновилась"

            # 5.3 Проверяем количество записей ТО для этого автомобиля
            cursor.execute("""
                SELECT COUNT(*) as cnt 
                FROM maintenance_history 
                WHERE car_id = %s
            """, (selected_car['car_id'],))

            total_records = cursor.fetchone()['cnt']
            print(f"\nВсего записей ТО для автомобиля: {total_records}")
    def test_add_maintenance_invalid_mileage(self, taxi_on_to):
        """Тест добавления ТО с некорректным пробегом"""
        # Выбираем первый автомобиль
        taxi_on_to.carsListView.setCurrentIndex(taxi_on_to.model.index(0))
        # Устанавливаем некорректный пробег
        taxi_on_to.mileageEdit.setText("invalid")
        # Мокаем метод show_warning
        taxi_on_to.show_warning = MagicMock()
        #QTest.mouseClick(taxi_on_to.btnAddMaintenance, Qt.LeftButton)
        with patch.object(QMessageBox, 'warning') as mock_warning:
            QTest.mouseClick(taxi_on_to.btnAddMaintenance, Qt.LeftButton)
            mock_warning.assert_called_once()
    def test_add_maintenance_negative_cost(self, taxi_on_to):
        """Тест добавления ТО с отрицательной стоимостью"""
        # Выбираем первый автомобиль
        taxi_on_to.carsListView.setCurrentIndex(taxi_on_to.model.index(0))
        # Устанавливаем тестовые данные
        taxi_on_to.mileageEdit.setText("50000")
        taxi_on_to.costEdit.setText("-1000")
        # Мокаем метод show_warning
        taxi_on_to.show_warning = MagicMock()
        QTest.mouseClick(taxi_on_to.btnAddMaintenance, Qt.LeftButton)
        with patch.object(QMessageBox, 'warning') as mock_warning:
            QTest.mouseClick(taxi_on_to.btnAddMaintenance, Qt.LeftButton)
            mock_warning.assert_called_once()
    def test_load_maintenance_history(self, taxi_on_to, test_db):
        """Тест загрузки истории ТО для выбранного автомобиля"""
        # Выбираем первый автомобиль
        first_index = taxi_on_to.model.index(0)
        taxi_on_to.carsListView.setCurrentIndex(first_index)
        selected_car = taxi_on_to.current_items[0]
        # Добавляем тестовую запись ТО
        with test_db._get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO maintenance_history 
                (car_id, maintenance_date, mileage, service_type, description)
                VALUES (%s, '2023-01-15', 50000, 'Регламентное', 'Тестовая запись')
            """, (selected_car['car_id'],))
        # Сбрасываем mock перед вызовом
        taxi_on_to.load_maintenance_history.reset_mock()
        # Эмулируем выбор автомобиля
        taxi_on_to.on_selection_changed()
        # Проверяем что метод load_maintenance_history был вызван ровно один раз
        taxi_on_to.load_maintenance_history.assert_called_once()