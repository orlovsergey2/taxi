import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox, QStackedWidget
from PySide6.QtTest import QTest
from unittest.mock import patch, MagicMock
from graph.graph import LoginWindow, MainWindow
from autorization.registration import Database
from confest import qt_app
import time


class TestTaxiParkAuthFlow:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Настройка тестовой базы данных"""
        self.db = Database()

        # Убедимся что тестовые пользователи существуют
        if not self.db.check_credentials("admin", "admin123")[0]:
            self.db.register_user("admin", "admin123")
            # Делаем пользователя администратором
            with self.db.get_cursor() as cursor:
                cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")

        if not self.db.check_credentials("user", "user123")[0]:
            self.db.register_user("user", "user123")
        yield

        # Удаляем тестового пользователя после всех тестов
        with self.db.get_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE username = 'newuser'")

    def simulate_typing(self, widget, text):
        """Имитация ввода текста с задержкой"""
        widget.clear()
        for char in text:
            QTest.keyClick(widget, char)
            time.sleep(0.1)  # Небольшая задержка для наглядности

    def test_auth_flow_with_ui(self, qt_app):
        """Тест с визуализацией процесса авторизации"""
        # Создаем реальные виджеты вместо моков
        stacked_widget = QStackedWidget()
        login_window = LoginWindow(stacked_widget)
        stacked_widget.addWidget(login_window)
        stacked_widget.show()

        # 1. Вход администратора
        print("\n=== Вход администратора ===")
        print("Вводим логин: admin")
        self.simulate_typing(login_window.LineEdit, "admin")

        print("Вводим пароль: admin123")
        self.simulate_typing(login_window.LineEdit_2, "admin123")

        print("Нажимаем кнопку 'Войти'")
        QTest.mouseClick(login_window.enter, Qt.LeftButton)

        # Даем время на обработку
        qt_app.processEvents()
        time.sleep(1)

        # Проверяем что открылось главное окно
        assert stacked_widget.currentWidget().__class__.__name__ == "MainWindow"
        main_window = stacked_widget.currentWidget()
        print("Успешный вход как администратор")

        # Возвращаемся к окну авторизации
        main_window.btn_exit.click()
        qt_app.processEvents()
        time.sleep(0.5)

        # 2. Вход обычного пользователя
        print("\n=== Вход обычного пользователя ===")
        print("Вводим логин: user")
        self.simulate_typing(login_window.LineEdit, "sergey")

        print("Вводим пароль: user123")
        self.simulate_typing(login_window.LineEdit_2, "ickq3sp_zx")

        print("Нажимаем кнопку 'Войти'")
        QTest.mouseClick(login_window.enter, Qt.LeftButton)

        qt_app.processEvents()
        time.sleep(1)

        # Проверяем что открылось главное окно
        assert stacked_widget.currentWidget().__class__.__name__ == "MainWindow"
        print("Успешный вход как обычный пользователь")

        # Возвращаемся к окну авторизации
        stacked_widget.currentWidget().btn_exit.click()
        qt_app.processEvents()
        time.sleep(0.5)

        # 3. Неудачная попытка входа
        print("\n=== Неудачная попытка входа ===")
        print("Вводим неверный пароль")
        self.simulate_typing(login_window.LineEdit, "admin")
        self.simulate_typing(login_window.LineEdit_2, "wrongpass")

        with patch.object(QMessageBox, 'warning') as mock_warning:
            QTest.mouseClick(login_window.enter, Qt.LeftButton)
            mock_warning.assert_called_once()
            print("Показано сообщение об ошибке")

        # 4. Регистрация нового пользователя
        print("\n=== Регистрация нового пользователя ===")
        print("Вводим новый логин: newuser")
        self.simulate_typing(login_window.LineEdit, "newuser")

        print("Вводим пароль: newpass123")
        self.simulate_typing(login_window.LineEdit_2, "newpass123")

        with patch.object(QMessageBox, 'information') as mock_info:
            QTest.mouseClick(login_window.pushButton, Qt.LeftButton)
            mock_info.assert_called_once()
            print("Пользователь успешно зарегистрирован")

        # 5. Вход под новым пользователем
        print("\n=== Вход под новым пользователем ===")
        self.simulate_typing(login_window.LineEdit, "newuser")
        self.simulate_typing(login_window.LineEdit_2, "newpass123")

        QTest.mouseClick(login_window.enter, Qt.LeftButton)
        qt_app.processEvents()
        time.sleep(1)

        assert stacked_widget.currentWidget().__class__.__name__ == "MainWindow"
        print("Успешный вход под новым пользователем")

        # Закрываем приложение
        stacked_widget.currentWidget().btn_exit.click()
        qt_app.processEvents()