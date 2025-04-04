# registration.py
import mysql.connector
from mysql.connector import Error
import bcrypt
from typing import Optional, Tuple


class Database:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 9306
        self.user = "myuser"
        self.password = "mypassword"  # Оставьте пустым или укажите пароль, если он установлен
        self.database = "registration"
        self.connection = None

    def connect(self):
        """Устанавливает соединение с MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            return False

    def create_database(self):
        """Создает базу данных и таблицы"""
        try:
            # Подключаемся без указания базы данных
            temp_conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )

            cursor = temp_conn.cursor()

            # Создаем базу данных если не существует
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")

            # Создаем таблицу пользователей
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.database}.users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            """)

            temp_conn.commit()
            cursor.close()
            temp_conn.close()
            return True

        except Error as e:
            print(f"Ошибка создания базы данных: {e}")
            return False

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Регистрирует нового пользователя"""
        if not self.connect():
            return False, "Ошибка подключения к базе данных"

        try:
            cursor = self.connection.cursor()

            # Проверяем существование пользователя
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Пользователь уже существует"

            # Хешируем пароль
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Добавляем пользователя
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )

            self.connection.commit()
            return True, "Пользователь успешно зарегистрирован"

        except Error as e:
            return False, f"Ошибка регистрации: {str(e)}"
        finally:
            if self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def check_credentials(self, username: str, password: str) -> Tuple[bool, str]:
        """Проверяет учетные данные пользователя"""
        if not self.connect():
            return False, "Ошибка подключения к базе данных"

        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT password_hash FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

            if not user:
                return False, "Пользователь не найден"

            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return True, "Аутентификация успешна"
            else:
                return False, "Неверный пароль"

        except Error as e:
            return False, f"Ошибка аутентификации: {str(e)}"
        finally:
            if self.connection.is_connected():
                cursor.close()
                self.connection.close()


if __name__ == "__main__":
    db = Database()
