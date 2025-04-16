import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import List, Optional, Dict


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
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Таблица распределения водителей и автомобилей
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS driver_car_assignments (
                            assignment_id INT AUTO_INCREMENT PRIMARY KEY,
                            driver_id INT NOT NULL,
                            car_id INT NOT NULL,
                            assignment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
                            FOREIGN KEY (car_id) REFERENCES cars(car_id),
                            UNIQUE KEY unique_assignment (driver_id, car_id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_history (
                    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
                    car_id INT NOT NULL,
                    maintenance_date DATE NOT NULL,
                    mileage INT NOT NULL,
                    service_type ENUM('Регламентное', 'Ремонт', 'Диагностика') NOT NULL,
                    description TEXT,
                    cost DECIMAL(10, 2),
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

    def delete_driver(self, driver_id: int) -> bool:
        """Удаляет водителя по ID"""
        if not self.connect():
            print("Ошибка подключения к базе данных")
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # 1. Проверяем существование водителя
            cursor.execute("SELECT 1 FROM drivers WHERE driver_id = %s", (driver_id,))
            if not cursor.fetchone():
                print(f"Водитель с ID {driver_id} не найден")
                return False

            # 2. Удаляем водителя
            delete_query = "DELETE FROM drivers WHERE driver_id = %s"
            cursor.execute(delete_query, (driver_id,))

            if cursor.rowcount == 0:
                print(f"Водитель с ID {driver_id} не был удален")
                return False

            self.connection.commit()
            print(f"Водитель с ID {driver_id} успешно удален")
            return True

        except Error as e:
            self.connection.rollback()
            print(f"Ошибка при удалении водителя: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def assign_driver_to_car(self, driver_id: int, car_id: int) -> bool:
        """Назначает водителя на автомобиль"""
        if not self.connect():
            return False

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Проверяем, что водитель и автомобиль существуют
            cursor.execute("SELECT 1 FROM drivers WHERE driver_id = %s", (driver_id,))
            if not cursor.fetchone():
                print(f"Водитель с ID {driver_id} не найден")
                return False

            cursor.execute("SELECT 1 FROM cars WHERE car_id = %s", (car_id,))
            if not cursor.fetchone():
                print(f"Автомобиль с ID {car_id} не найден")
                return False

            # Проверяем, что водитель и автомобиль свободны
            cursor.execute("""
                SELECT 1 FROM drivers 
                WHERE driver_id = %s AND status = 'available'
                AND driver_id NOT IN (SELECT driver_id FROM driver_car_assignments)
            """, (driver_id,))
            if not cursor.fetchone():
                print("Водитель уже занят")
                return False

            cursor.execute("""
                SELECT 1 FROM cars 
                WHERE car_id = %s AND is_active = TRUE
                AND car_id NOT IN (SELECT car_id FROM driver_car_assignments)
            """, (car_id,))
            if not cursor.fetchone():
                print("Автомобиль уже занят")
                return False

            # Назначаем
            insert_query = """
                INSERT INTO driver_car_assignments (driver_id, car_id)
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (driver_id, car_id))

            # Обновляем статус водителя
            update_query = """
                UPDATE drivers 
                SET status = 'on_ride' 
                WHERE driver_id = %s
            """
            cursor.execute(update_query, (driver_id,))

            self.connection.commit()
            print(f"Водитель {driver_id} назначен на автомобиль {car_id}")
            return True

        except Error as e:
            self.connection.rollback()
            print(f"Ошибка при назначении водителя: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def get_free_drivers(self):
        """Возвращает список водителей без прикрепленных машин"""
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT d.* FROM drivers d
                LEFT JOIN driver_car_assignments a ON d.driver_id = a.driver_id
                WHERE a.driver_id IS NULL
                AND d.status = 'available'
            """)
            return cursor.fetchall()
        except Error as e:
            print(f"Ошибка при получении свободных водителей: {e}")
            return []
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()

    def get_free_cars(self) -> List[Dict]:
        """Возвращает список свободных автомобилей"""
        if not self.connect():
            return []

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            query = """
                SELECT c.* FROM cars c
                WHERE c.car_id NOT IN (SELECT car_id FROM driver_car_assignments)
                AND c.is_active = TRUE
            """
            cursor.execute(query)
            return cursor.fetchall()

        except Error as e:
            print(f"Ошибка при получении свободных автомобилей: {e}")
            return []
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def get_assigned_drivers(self) -> List[Dict]:
        """Возвращает список распределенных водителей с их автомобилями"""
        if not self.connect():
            return []

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            query = """
                SELECT d.driver_id, d.full_name, c.car_id, c.license_plate, c.model
                FROM driver_car_assignments a
                JOIN drivers d ON a.driver_id = d.driver_id
                JOIN cars c ON a.car_id = c.car_id
            """
            cursor.execute(query)
            return cursor.fetchall()

        except Error as e:
            print(f"Ошибка при получении распределенных водителей: {e}")
            return []
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    # Добавим методы для работы с ТО:
    def add_maintenance_record(self, car_id: int, date: str, mileage: int,
                               service_type: str, description: str, cost: float = None) -> bool:
        """Добавляет запись о техническом обслуживании"""
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO maintenance_history 
                (car_id, maintenance_date, mileage, service_type, description, cost)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (car_id, date, mileage, service_type, description, cost))

            # Обновляем данные автомобиля
            update_query = """
                UPDATE cars 
                SET last_maintenance = %s, mileage = %s 
                WHERE car_id = %s
            """
            cursor.execute(update_query, (date, mileage, car_id))

            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Ошибка при добавлении записи ТО: {e}")
            return False
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()

    def get_maintenance_history(self, car_id: int) -> List[Dict]:
        """Возвращает историю ТО для автомобиля"""
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM maintenance_history 
                WHERE car_id = %s 
                ORDER BY maintenance_date DESC
            """, (car_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Ошибка при получении истории ТО: {e}")
            return []
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()

    def get_car_current_status(self, car_id: int) -> Optional[Dict]:
        """Возвращает текущий статус автомобиля (последнее ТО)"""
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    c.*, 
                    (SELECT MAX(maintenance_date) FROM maintenance_history WHERE car_id = c.car_id) as last_maintenance_date,
                    (SELECT mileage FROM maintenance_history WHERE car_id = c.car_id ORDER BY maintenance_date DESC LIMIT 1) as current_mileage
                FROM cars c
                WHERE c.car_id = %s
            """, (car_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Ошибка при получении статуса автомобиля: {e}")
            return None
        finally:
            if cursor and self.connection.is_connected():
                cursor.close()

def main():
    # Инициализация менеджера базы данных
    db = DatabaseManager()

    # 1. Создаем базу данных и таблицы (если их нет)
    if not db.create_database():
        print("Не удалось создать базу данных")
        return

    if not db.create_tables():
        print("Не удалось создать таблицы")
        return

    print("Инициализация базы данных таксопарка завершена")


if __name__ == '__main__':
    main()