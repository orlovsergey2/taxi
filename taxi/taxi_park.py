import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import List, Dict, Optional
from PySide6.QtWidgets import (QApplication, QMessageBox, QMainWindow)
import random
class DatabaseManager:
    def __init__(self):
        # Конфигурация подключения
        self.host = "127.0.0.1"
        self.port = "9306"
        self.user = "myuser"
        self.password = "mypassword"
        self.database = "taxi_park"

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
        """Создает базу данных если не существует"""
        try:
            temp_conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )

            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"База данных {self.database} создана или уже существует")

            cursor.close()
            temp_conn.close()
            return True

        except Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            return False

    def create_tables(self):
        """Создает все необходимые таблицы"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Таблица автомобилей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    car_id INT AUTO_INCREMENT PRIMARY KEY,
                    license_plate VARCHAR(20) UNIQUE NOT NULL,
                    model VARCHAR(50) NOT NULL,
                    year INT NOT NULL,
                    car_type ENUM('sedan', 'minivan', 'suv', 'business', 'electric') NOT NULL,
                    capacity INT NOT NULL,
                    mileage FLOAT DEFAULT 0,
                    last_maintenance DATE,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Таблица водителей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drivers (
                    driver_id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    license_number VARCHAR(30) UNIQUE NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    status ENUM('available', 'on_ride', 'off_duty', 'sick_leave') DEFAULT 'available',
                    hire_date DATE NOT NULL,
                    car_id INT,
                    FOREIGN KEY (car_id) REFERENCES cars(car_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            self.connection.commit()
            print("Все таблицы успешно созданы")
            return True

        except Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def add_car(self, license_plate: str, model: str, year: int,
                car_type: str, capacity: int) -> bool:
        """Добавляет новый автомобиль в парк"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            insert_query = """
                INSERT INTO cars (license_plate, model, year, car_type, capacity)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(insert_query, (license_plate, model, year, car_type, capacity))
            self.connection.commit()
            print(f"Автомобиль {license_plate} успешно добавлен")
            return True

        except Error as e:
            print(f"Ошибка при добавлении автомобиля: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def add_driver(self, full_name: str, license_number: str,
                   phone: str, hire_date: str = None) -> bool:
        """Добавляет нового водителя с проверкой уникальности номера прав"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Сначала проверяем, существует ли уже водитель с таким номером прав
            check_query = "SELECT COUNT(*) FROM drivers WHERE license_number = %s"
            cursor.execute(check_query, (license_number,))
            if cursor.fetchone()[0] > 0:
                print(f"Ошибка: водитель с номером прав {license_number} уже существует")
                return False
            hire_date = hire_date or datetime.now().strftime('%Y-%m-%d')

            insert_query = """
                INSERT INTO drivers (full_name, license_number, phone, hire_date)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(insert_query, (full_name, license_number, phone, hire_date))
            self.connection.commit()
            print(f"Водитель {full_name} успешно добавлен")
            return True

        except Error as e:
            print (f"Ошибка при добавлении водителя: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def get_cars(self) -> List[Dict]:
        """Возвращает список всех автомобилей из базы данных с диагностикой."""
        if not self.connect():
            print("Ошибка подключения к базе данных")
            return []

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Упрощенный запрос без условия is_active для диагностики
            cursor.execute("SELECT * FROM cars")
            cars = cursor.fetchall()

            # Диагностика полученных данных
            print(f"Получено автомобилей: {len(cars)}")
            for car in cars:
                print(car)

            return cars

        except Error as e:
            print(f"Ошибка при получении автомобилей: {e}")
            return []
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def get_drivers(self) -> List[Dict]:
        """Возвращает список всех водителей из базы данных."""
        if not self.connect():
            print("Ошибка подключения к базе данных")
            return []

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Упрощенный запрос без условия is_active
            cursor.execute("SELECT * FROM drivers")
            drivers = cursor.fetchall()

            # Проверка полученных данных
            print(f"Получено водителей: {len(drivers)}")
            for driver in drivers:
                print(driver)

            return drivers

        except Error as e:
            print(f"Ошибка при получении водителей: {e}")
            return []
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()

    def delete_car(self, car_id: int) -> bool:
        """Удаляет автомобиль по его ID"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Сначала проверяем, не связан ли автомобиль с водителем
            cursor.execute("SELECT COUNT(*) FROM drivers WHERE car_id = %s", (car_id,))
            if cursor.fetchone()[0] > 0:
                print("Ошибка: нельзя удалить автомобиль, так как он назначен водителю")
                return False

            delete_query = "DELETE FROM cars WHERE car_id = %s"
            cursor.execute(delete_query, (car_id,))
            self.connection.commit()
            print(f"Автомобиль с ID {car_id} успешно удален")
            return True

        except Error as e:
            print(f"Ошибка при удалении автомобиля: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def delete_driver(self, license_number: str) -> bool:
        """Удаляет водителя по его ID"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            delete_query = "DELETE FROM drivers WHERE license_number = %s"
            cursor.execute(delete_query, (license_number,))
            self.connection.commit()
            print(f"Водитель с ID {license_number} успешно удален")
            return True

        except Error as e:
            print(f"Ошибка при удалении водителя: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
def main():
    # Инициализация менеджера базы данных
    db = DatabaseManager()

    # Создание базы данных и таблиц
    if not db.create_database():
        print("Не удалось создать базу данных")
        return

    if not db.create_tables():
        print("Не удалось создать таблицы")
        return

    print("Инициализация базы данных таксопарка завершена")


if __name__ == '__main__':
    main()