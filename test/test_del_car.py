import pytest
import random
from PySide6 import QtCore
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QStackedWidget, QMessageBox, QListView
from PySide6.QtTest import QTest
from unittest.mock import patch, MagicMock
from confest import qt_app
from taxi.taxi_park import DatabaseManager
from graph.graph import CarManagerWindow  # Предполагается, что у вас есть такой класс

@pytest.fixture
def test_db():
    """Фикстура для тестовой базы данных с тестовыми автомобилями"""
    db = DatabaseManager()

    # Очищаем тестовые данные перед началом
    with db._get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM driver_car_assignments WHERE car_id IN (SELECT car_id FROM cars WHERE license_plate LIKE 'TEST%')")
        cursor.execute(
            "DELETE FROM maintenance_history WHERE car_id IN (SELECT car_id FROM cars WHERE license_plate LIKE 'TEST%')")
        cursor.execute("DELETE FROM cars WHERE license_plate LIKE 'TEST%'")

    # Добавляем тестовые данные
    with db._get_cursor(dictionary=True) as cursor:
        cursor.execute("""
            INSERT INTO cars (license_plate, model, year, car_type, capacity)
            VALUES 
                ('TEST001', 'Toyota Camry', 2020, 'sedan', 4),
                ('TEST002', 'Volkswagen Multivan', 2021, 'minivan', 7),
                ('TEST003', 'Tesla Model 3', 2022, 'electric', 5)
        """)
    yield db

    # Очищаем тестовые данные после завершения
    with db._get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM driver_car_assignments WHERE car_id IN (SELECT car_id FROM cars WHERE license_plate LIKE 'TEST%')")
        cursor.execute(
            "DELETE FROM maintenance_history WHERE car_id IN (SELECT car_id FROM cars WHERE license_plate LIKE 'TEST%')")
        cursor.execute("DELETE FROM cars WHERE license_plate LIKE 'TEST%'")


@pytest.fixture
def car_manager_window(test_db, qt_app):
    """Фикстура для создания и показа окна управления автомобилями"""
    stacked_widget = QStackedWidget()
    window = CarManagerWindow(stacked_widget, is_admin=True)
    window.db = test_db
    window.load_data_car()  # Загружаем тестовые данные
    stacked_widget.addWidget(window)
    stacked_widget.show()
    # Даем время на загрузку данных
    QTest.qWait(500)
    return window
class TestCarManagerWindow:
    def test_initial_state(self, car_manager_window):
        """Проверка начального состояния окна"""
        assert car_manager_window.windowTitle() == "Управление автопарком"
        assert car_manager_window.exit.text() == "Назад"
        assert car_manager_window.btn_del_auto.text() == "Удалить автомобиль"
        assert isinstance(car_manager_window.listView.model(), QtCore.QStringListModel)
        assert car_manager_window.listView.selectionMode() == QListView.SingleSelection
        assert len(car_manager_window.current_items) >= 3  # Проверяем, что загрузились тестовые данные

    def test_delete_car_no_selection(self, car_manager_window):
        """Проверка сообщения при попытке удаления без выбора автомобиля"""
        # Снимаем выделение (если есть)
        car_manager_window.listView.clearSelection()
        # Проверяем, что ничего не выбрано
        assert not car_manager_window.listView.selectedIndexes()
        # Мокаем QMessageBox.warning и проверяем его вызов
        with patch.object(QMessageBox, 'warning') as mock_warning:
            QTest.mouseClick(car_manager_window.btn_del_auto, Qt.LeftButton)
            # Проверяем, что сообщение было показано
            mock_warning.assert_called_once()
            # Получаем аргументы вызова
            args, kwargs = mock_warning.call_args
            # Проверяем текст сообщения
            assert args[0] == car_manager_window  # родительское окно
            assert args[1] == "Ошибка"  # заголовок
            assert args[2] == "Выберите автомобиль для удаления"  # текст сообщения

    def test_delete_car_cancel(self, car_manager_window):
        """Проверка отмены удаления автомобиля"""
        model = car_manager_window.listView.model()
        initial_count = model.rowCount()
        # Выбираем первый автомобиль
        car_manager_window.listView.setCurrentIndex(model.index(0))
        selected_index = car_manager_window.listView.selectedIndexes()[0]
        car_info = model.data(selected_index, Qt.DisplayRole)
        assert len(car_manager_window.listView.selectedIndexes()) == 1
        # Извлекаем номер и модель автомобиля для проверки
        license_plate = car_info.split()[0]
        model_name = car_info.split()[1]
        expected_message = f"Вы уверены, что хотите удалить автомобиль:\n{license_plate} {model_name}?"

        # Мокаем QMessageBox.question
        with patch('PySide6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.No
            # Симулируем клик по кнопке удаления
            QTest.mouseClick(car_manager_window.btn_del_auto, Qt.LeftButton)
            # Проверяем, что question был вызван
            mock_question.assert_called_once()
            # Проверяем параметры вызова диалога
            args, _ = mock_question.call_args
            assert args[0] == car_manager_window  # Родительское окно
            assert args[1] == "Подтверждение удаления"  # Заголовок
            assert args[2] == expected_message  # Текст сообщения
            assert args[3] == QMessageBox.Yes | QMessageBox.No  # Кнопки
            assert args[4] == QMessageBox.No  # Кнопка по умолчанию

        # Проверяем, что количество автомобилей не изменилось
        assert model.rowCount() == initial_count

    def test_delete_unassigned_car_success(self, car_manager_window, test_db):
        """Test successful deletion of unassigned car (Tesla Model 3)"""
        model = car_manager_window.listView.model()
        initial_count = model.rowCount()

        # Получаем Tesla из БД
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.* FROM cars c
                LEFT JOIN driver_car_assignments a ON c.car_id = a.car_id
                WHERE c.license_plate = 'TEST003' AND a.car_id IS NULL
            """)
            tesla = cursor.fetchone()
            assert tesla, "Tesla не найдена или она прикреплена к водителю!"

        # Находим Tesla в списке
        car_index = next(
            i for i in range(model.rowCount())
            if "TEST003" in model.data(model.index(i), Qt.DisplayRole)
        )
        car_manager_window.listView.setCurrentIndex(model.index(car_index))

        # Мокаем подтверждение и тестируем удаление
        with patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            with patch('PySide6.QtWidgets.QMessageBox.information') as mock_info:
                QTest.mouseClick(car_manager_window.btn_del_auto, Qt.LeftButton)

                # Проверяем сообщение об успехе
                mock_info.assert_called_once()
                assert "успешно удален" in mock_info.call_args[0][2]

        # Проверяем изменения в UI и БД
        assert model.rowCount() == initial_count - 1

        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT 1 FROM cars WHERE car_id = %s", (tesla['car_id'],))
            assert not cursor.fetchone(), "Tesla все еще существует в БД"

            # Проверяем, что другие автомобили остались
            cursor.execute("SELECT 1 FROM cars WHERE license_plate = 'TEST001'")
            assert cursor.fetchone(), "Toyota Camry была удалена, хотя не должна была"

    def test_delete_assigned_car_failure(self, car_manager_window, test_db):
        """Test full flow when trying to delete assigned car (Toyota Camry)"""
        # 1. Подготовка данных - прикрепляем водителя к Toyota Camry
        with test_db._get_cursor() as cursor:
            # Очищаем возможные старые данные
            cursor.execute(
                "DELETE FROM driver_car_assignments WHERE driver_id IN (SELECT driver_id FROM drivers WHERE full_name LIKE 'test%')")
            cursor.execute("DELETE FROM drivers WHERE full_name LIKE 'test%'")

            # Находим ID Toyota Camry
            cursor.execute("SELECT car_id FROM cars WHERE license_plate = 'TEST001'")
            car_id = cursor.fetchone()[0]

            # Создаем тестового водителя
            cursor.execute(
                "INSERT INTO drivers (full_name, license_number, phone, hire_date) "
                "VALUES (%s, %s, %s, %s)",
                ("test Иванов Иван", "1234567890", "+79998887766", "2023-01-01")
            )
            driver_id = cursor.lastrowid

            # Прикрепляем водителя к автомобилю
            cursor.execute(
                "INSERT INTO driver_car_assignments (driver_id, car_id) "
                "VALUES (%s, %s)",
                (driver_id, car_id)
            )

        # 2. Обновляем интерфейс и находим Toyota Camry
        car_manager_window.load_data_car()
        model = car_manager_window.listView.model()
        car_index = next(
            i for i in range(model.rowCount())
            if "TEST001" in model.data(model.index(i), Qt.DisplayRole)
        )
        car_manager_window.listView.setCurrentIndex(model.index(car_index))
        car_info = model.data(model.index(car_index), Qt.DisplayRole)

        # Извлекаем номер и модель автомобиля для проверки
        car_parts = car_info.split()
        license_plate = car_parts[0]

        # Находим индекс открывающей скобки или используем длину списка
        bracket_index = next(
            (i for i, part in enumerate(car_parts) if '(' in part),
            len(car_parts)
        )

        # Берем все части между номером и скобкой как название модели
        model_name = ' '.join(car_parts[1:bracket_index]) if len(car_parts) > 1 else ""

        expected_message = f"Вы уверены, что хотите удалить автомобиль:\n{license_plate} {model_name}?"

        # 3. Мокаем все QMessageBox в одном контексте
        with patch('PySide6.QtWidgets.QMessageBox.question') as mock_question, \
                patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Настраиваем mock для подтверждения удаления (нажатие Yes)
            mock_question.return_value = QMessageBox.Yes
            # Настраиваем mock для ошибки (нажатие Ok)
            mock_msg_box = MagicMock()
            mock_msg_box.exec.return_value = QMessageBox.Ok
            mock_warning.return_value = mock_msg_box
            # Имитируем клик по кнопке удаления
            QTest.mouseClick(car_manager_window.btn_del_auto, Qt.LeftButton)
            # Проверяем что было показано подтверждение удаления
            mock_question.assert_called_once()
            question_args, _ = mock_question.call_args
            # Проверяем сообщение
            assert question_args[0] == car_manager_window
            assert question_args[1] == "Подтверждение удаления"
            assert question_args[2] == expected_message
            assert question_args[3] == QMessageBox.Yes | QMessageBox.No
            assert question_args[4] == QMessageBox.No
            mock_warning.assert_called_once()
            args, kwargs = mock_warning.call_args
            assert args[0] == car_manager_window  # parent
            assert args[1] == "Ошибка"  # title
            assert "Не удалось удалить автомобиль" in args[2]  # message
        # 4. Проверяем что автомобиль остался в системе
        with test_db._get_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT 1 FROM cars WHERE license_plate = 'TEST001'")
            assert cursor.fetchone(), "Автомобиль Toyota Camry был удален, хотя не должен был"