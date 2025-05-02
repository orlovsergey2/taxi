import pytest
import random

from PySide6 import QtCore
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QStackedWidget, QMessageBox, QListView
from PySide6.QtTest import QTest
from graph.graph import DriverManagerWindow
from confest import qt_app
from taxi.taxi_park import DatabaseManager
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_db():
    """Фикстура для тестовой базы данных с тестовыми автомобилями"""
    db = DatabaseManager()

    # Очищаем тестовые данные перед началом
    with db._get_cursor() as cursor:
        cursor.execute("DELETE FROM driver_car_assignments WHERE driver_id IN (SELECT driver_id FROM drivers WHERE full_name LIKE 'test%')")
        cursor.execute("DELETE FROM drivers WHERE full_name LIKE 'test%'")

    # Добавляем тестовые данные
    with db._get_cursor(dictionary=True) as cursor:
        cursor.execute("""
            INSERT INTO drivers (full_name, license_number, phone, hire_date)
            VALUES 
                ('test Иванов Иван', '1234567890', '+79998887766', '2023-01-01'),
                ('test Петров Петр', '0987654321', '+79997776655', '2023-02-01'),
                ('test Сидоров Алексей', '1122334455', '+79996665544', '2023-03-01')
        """)
    yield db

    # Очищаем тестовые данные после завершения
    with db._get_cursor() as cursor:
        cursor.execute("DELETE FROM driver_car_assignments WHERE driver_id IN (SELECT driver_id FROM drivers WHERE full_name LIKE 'test%')")
        cursor.execute("DELETE FROM drivers WHERE full_name LIKE 'test%'")
@pytest.fixture
def driver_manager_window(qt_app, test_db):
    """Фикстура для создания и показа окна ТО"""
    stacked_widget = QStackedWidget()
    window = DriverManagerWindow(stacked_widget, is_admin=True)
    window.db = test_db

    # Мокаем метод load_maintenance_history для тестов
    window.load_maintenance_history = MagicMock()

    stacked_widget.addWidget(window)
    stacked_widget.show()

    # Даем время на загрузку данных
    QTest.qWait(500)
    return window

class TestDriverManagerWindow:
    def test_initial_state(self, driver_manager_window):
        """Проверка начального состояния окна"""
        assert driver_manager_window.windowTitle() == "Список водителей"
        assert driver_manager_window.exit.text() == "Назад"
        assert driver_manager_window.btn_del_driver.text() == "Удалить водителя"
        assert isinstance(driver_manager_window.listView.model(), QtCore.QStringListModel)
        assert driver_manager_window.listView.selectionMode() == QListView.SingleSelection

    def test_delete_driver_no_selection(self, driver_manager_window, qt_app):
        """Проверка сообщения при попытке удаления без выбора водителя"""
        # Снимаем выделение (если есть)
        driver_manager_window.listView.clearSelection()
        # Проверяем, что ничего не выбрано
        assert not driver_manager_window.listView.selectedIndexes()
        # Мокаем QMessageBox.warning и проверяем его вызов
        with patch.object(QMessageBox, 'warning') as mock_warning:
            QTest.mouseClick(driver_manager_window.btn_del_driver, Qt.LeftButton)
            # Проверяем, что сообщение было показано
            mock_warning.assert_called_once()
            # Получаем аргументы вызова
            args, kwargs = mock_warning.call_args
            # Проверяем текст сообщения
            assert args[0] == driver_manager_window  # родительское окно
            assert args[1] == "Ошибка"  # заголовок
            assert args[2] == "Выберите водителя для удаления"  # текст сообщения
    def test_delete_driver_cancel(self, driver_manager_window):
        """Проверка отмены удаления водителя"""
        model = driver_manager_window.listView.model()
        initial_count = model.rowCount()
        # Выбираем первого водителя
        driver_manager_window.listView.setCurrentIndex(model.index(0))
        selected_index = driver_manager_window.listView.selectedIndexes()[0]
        driver_info = model.data(selected_index, Qt.DisplayRole)
        assert len(driver_manager_window.listView.selectedIndexes()) == 1
        # Извлекаем только имя водителя и номер прав (без телефона) для проверки
        driver_name = driver_info.split("(")[0].strip()  # "Василий Васильев"
        license_part = driver_info.split("(")[1].split(")")[0]  # "№ прав: 123"
        driver_name_and_license = f"{driver_name} ({license_part})"  # "Василий Васильев (№ прав: 123)"
        expected_message = f"Вы уверены, что хотите удалить водителя:\n{driver_name_and_license}?"
        # Мокаем QMessageBox.question
        with patch('PySide6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.No
            # Симулируем клик по кнопке удаления
            QTest.mouseClick(driver_manager_window.btn_del_driver, Qt.LeftButton)
            # Проверяем, что question был вызван
            mock_question.assert_called_once()
            # Проверяем параметры вызова диалога
            args, _ = mock_question.call_args
            assert args[0] == driver_manager_window  # Родительское окно
            assert args[1] == "Подтверждение удаления"  # Заголовок
            assert args[2] == expected_message  # Текст сообщения
            assert args[3] == QMessageBox.Yes | QMessageBox.No  # Кнопки
            assert args[4] == QMessageBox.No  # Кнопка по умолчанию

        # Проверяем, что количество водителей не изменилось
        assert model.rowCount() == initial_count

        # Проверяем, что водитель остался в списке
        assert driver_info in [model.data(model.index(i), Qt.DisplayRole)
                               for i in range(model.rowCount())]

    def test_delete_unassigned_driver_success(self, driver_manager_window, test_db):
        """Test successful deletion of unassigned driver (Петрова)"""
        model = driver_manager_window.listView.model()
        initial_count = model.rowCount()

        # Получаем конкретно Петрова из БД
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT d.* FROM drivers d
                LEFT JOIN driver_car_assignments a ON d.driver_id = a.driver_id
                WHERE d.full_name = 'test Петров Петр' AND a.driver_id IS NULL
            """)
            petrov = cursor.fetchone()
            assert petrov, "Петров не найден или он прикреплен к автомобилю!"

        # Находим Петрова в списке
        driver_index = next(
            i for i in range(model.rowCount())
            if "Петров Петр" in model.data(model.index(i), Qt.DisplayRole)
        )
        driver_manager_window.listView.setCurrentIndex(model.index(driver_index))

        # Мокаем подтверждение и тестируем удаление
        with patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            with patch('PySide6.QtWidgets.QMessageBox.information') as mock_info:
                QTest.mouseClick(driver_manager_window.btn_del_driver, Qt.LeftButton)

                # Проверяем сообщение об успехе
                mock_info.assert_called_once()
                assert "успешно удален" in mock_info.call_args[0][2]

        # Проверяем изменения в UI и БД
        assert model.rowCount() == initial_count - 1

        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT 1 FROM drivers WHERE driver_id = %s", (petrov['driver_id'],))
            assert not cursor.fetchone(), "Петров все еще существует в БД"

            # Проверяем, что Иванов остался
            cursor.execute("SELECT 1 FROM drivers WHERE full_name = 'test Иванов Иван'")
            assert cursor.fetchone(), "Иванов был удален, хотя не должен был"

    def test_delete_assigned_driver_failure(self, driver_manager_window, test_db):
        """Test full flow when trying to delete assigned driver (Иванов Иван)"""
        # 1. Подготовка данных - прикрепляем Иванова к автомобилю
        with test_db._get_cursor() as cursor:
            # Очищаем возможные старые данные
            cursor.execute(
                "DELETE FROM driver_car_assignments WHERE driver_id IN (SELECT driver_id FROM drivers WHERE full_name = 'test Иванов Иван')")
            cursor.execute("DELETE FROM cars WHERE license_plate = 'TEST001'")

            # Находим ID Иванова
            cursor.execute("SELECT driver_id FROM drivers WHERE full_name = 'test Иванов Иван'")
            driver_id = cursor.fetchone()[0]

            # Создаем тестовый автомобиль
            cursor.execute(
                "INSERT INTO cars (license_plate, model, year, car_type, capacity) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("TEST001", "Test Model", 2020, "sedan", 4)
            )
            car_id = cursor.lastrowid

            # Прикрепляем Иванова к автомобилю
            cursor.execute(
                "INSERT INTO driver_car_assignments (driver_id, car_id) "
                "VALUES (%s, %s)",
                (driver_id, car_id)
            )
        # 2. Обновляем интерфейс и находим Иванова
        driver_manager_window.load_driver_data()
        model = driver_manager_window.listView.model()
        driver_index = next(
            i for i in range(model.rowCount())
            if "Иванов Иван" in model.data(model.index(i), Qt.DisplayRole)
        )
        driver_manager_window.listView.setCurrentIndex(model.index(driver_index))
        driver_info = model.data(model.index(driver_index), Qt.DisplayRole)
        # Извлекаем только имя водителя и номер прав для проверки
        driver_name = driver_info.split("(")[0].strip()
        license_part = driver_info.split("(")[1].split(")")[0]
        driver_name_and_license = f"{driver_name} ({license_part})"
        expected_message = f"Вы уверены, что хотите удалить водителя:\n{driver_name_and_license}?"
        # 3. Мокаем все QMessageBox в одном контексте
        with patch('PySide6.QtWidgets.QMessageBox.question') as mock_question, \
                patch('PySide6.QtWidgets.QMessageBox.critical') as mock_critical:
            # Настраиваем mock для подтверждения удаления (нажатие Yes)
            mock_question.return_value = QMessageBox.Yes
            # Настраиваем mock для ошибки (нажатие Ok)
            mock_msg_box = MagicMock()
            mock_msg_box.exec.return_value = QMessageBox.Ok
            mock_critical.return_value = mock_msg_box
            # Имитируем клик по кнопке удаления
            QTest.mouseClick(driver_manager_window.btn_del_driver, Qt.LeftButton)
            # Проверяем что было показано подтверждение удаления
            mock_question.assert_called_once()
            question_args, _ = mock_question.call_args
            assert question_args[0] == driver_manager_window
            assert question_args[1] == "Подтверждение удаления"
            assert question_args[2] == expected_message
            assert question_args[3] == QMessageBox.Yes | QMessageBox.No
            assert question_args[4] == QMessageBox.No
            mock_critical.assert_called_once()
            args, kwargs = mock_critical.call_args
            assert args[0] == driver_manager_window  # parent
            assert args[1] == "Ошибка"  # title
            assert "Не удалось удалить водителя" in args[2]  # message
            assert "назначен к автомобилю" in args[2]

        # 4. Проверяем что водитель остался в системе
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT 1 FROM drivers WHERE full_name = 'test Иванов Иван'")
            assert cursor.fetchone(), "Водитель Иванов Иван был удален, хотя не должен был"