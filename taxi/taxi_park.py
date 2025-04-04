import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import List, Optional


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

            # Таблица клиентов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Таблица поездок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rides (
                    ride_id INT AUTO_INCREMENT PRIMARY KEY,
                    driver_id INT NOT NULL,
                    client_id INT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    start_location VARCHAR(255) NOT NULL,
                    end_location VARCHAR(255),
                    distance FLOAT DEFAULT 0,
                    fare FLOAT DEFAULT 0,
                    payment_method ENUM('cash', 'card', 'mobile'),
                    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
                    FOREIGN KEY (client_id) REFERENCES clients(client_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Таблица технического обслуживания
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance (
                    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
                    car_id INT NOT NULL,
                    maintenance_type VARCHAR(100) NOT NULL,
                    maintenance_date DATE NOT NULL,
                    cost FLOAT NOT NULL,
                    description TEXT,
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
        """Добавляет нового водителя"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

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
            print(f"Ошибка при добавлении водителя: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def assign_car_to_driver(self, driver_id: int, car_id: int) -> bool:
        """Назначает автомобиль водителю"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            update_query = """
                UPDATE drivers 
                SET car_id = %s 
                WHERE driver_id = %s
            """

            cursor.execute(update_query, (car_id, driver_id))
            self.connection.commit()
            print(f"Автомобиль {car_id} назначен водителю {driver_id}")
            return True

        except Error as e:
            print(f"Ошибка при назначении автомобиля: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def start_ride(self, driver_id: int, client_id: int,
                   start_location: str) -> bool:
        """Начинает новую поездку"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Начинаем поездку
            insert_query = """
                INSERT INTO rides (driver_id, client_id, start_time, start_location)
                VALUES (%s, %s, NOW(), %s)
            """

            cursor.execute(insert_query, (driver_id, client_id, start_location))

            # Меняем статус водителя
            update_query = """
                UPDATE drivers 
                SET status = 'on_ride' 
                WHERE driver_id = %s
            """

            cursor.execute(update_query, (driver_id,))
            self.connection.commit()
            print(f"Поездка для водителя {driver_id} начата")
            return True

        except Error as e:
            print(f"Ошибка при начале поездки: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def complete_ride(self, ride_id: int, end_location: str,
                      distance: float, fare: float) -> bool:
        """Завершает поездку"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Завершаем поездку
            update_ride_query = """
                UPDATE rides 
                SET end_time = NOW(), 
                    end_location = %s, 
                    distance = %s, 
                    fare = %s 
                WHERE ride_id = %s
            """

            cursor.execute(update_ride_query, (end_location, distance, fare, ride_id))

            # Получаем driver_id для этой поездки
            cursor.execute("SELECT driver_id FROM rides WHERE ride_id = %s", (ride_id,))
            driver_id = cursor.fetchone()[0]

            # Меняем статус водителя
            update_driver_query = """
                UPDATE drivers 
                SET status = 'available' 
                WHERE driver_id = %s
            """

            cursor.execute(update_driver_query, (driver_id,))

            # Обновляем пробег автомобиля
            update_car_query = """
                UPDATE cars c
                JOIN drivers d ON c.car_id = d.car_id
                SET c.mileage = c.mileage + %s
                WHERE d.driver_id = %s
            """

            cursor.execute(update_car_query, (distance, driver_id))
            self.connection.commit()
            print(f"Поездка {ride_id} успешно завершена")
            return True

        except Error as e:
            print(f"Ошибка при завершении поездки: {e}")
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