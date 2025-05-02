import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from contextlib import contextmanager


class DatabaseManager:
    def __init__(self):
        self.config = {
            "host": "127.0.0.1",
            "port": "9306",
            "user": "myuser",
            "password": "mypassword",
            "database": "taxi_park"
        }
        self.connection = None

    @contextmanager
    def _get_cursor(self, dictionary=False):
        """Контекстный менеджер для работы с курсором"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=dictionary)
            yield cursor
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _execute_query(self, query: str, params: Tuple = None, fetch: bool = False):
        """Универсальный метод выполнения запросов"""
        with self._get_cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            return True

    def create_database(self) -> bool:
        """Создает базу данных если не существует"""
        try:
            with mysql.connector.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    user=self.config["user"],
                    password=self.config["password"]
            ) as temp_conn:
                with temp_conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            return True
        except Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            return False

    def create_tables(self) -> bool:
        """Создает все необходимые таблицы"""
        tables = {
            "cars": """
                CREATE TABLE IF NOT EXISTS cars (
                    car_id INT AUTO_INCREMENT PRIMARY KEY,
                    license_plate VARCHAR(20) UNIQUE NOT NULL,
                    model VARCHAR(50) NOT NULL,
                    year INT NOT NULL,
                    car_type ENUM('sedan', 'minivan', 'suv', 'business', 'electric') NOT NULL,
                    capacity INT NOT NULL,
                    mileage INT DEFAULT 0,
                    last_maintenance DATE,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            "drivers": """
                CREATE TABLE IF NOT EXISTS drivers (
                    driver_id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    license_number VARCHAR(30) UNIQUE NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    status ENUM('available', 'on_ride', 'off_duty', 'sick_leave') DEFAULT 'available',
                    hire_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            "driver_car_assignments": """
                CREATE TABLE IF NOT EXISTS driver_car_assignments (
                    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
                    driver_id INT NOT NULL,
                    car_id INT NOT NULL,
                    assignment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
                    FOREIGN KEY (car_id) REFERENCES cars(car_id),
                    UNIQUE KEY unique_assignment (driver_id, car_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            "maintenance_history": """
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
            """
        }

        try:
            with self._get_cursor() as cursor:
                for table_name, query in tables.items():
                    cursor.execute(query)
            return True
        except Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            return False

    def add_car(self, license_plate: str, model: str, year: int,
                car_type: str, capacity: int) -> bool:
        """Добавляет новый автомобиль в парк"""
        query = """
            INSERT INTO cars (license_plate, model, year, car_type, capacity)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self._execute_query(query, (license_plate, model, year, car_type, capacity))
            return True
        except Error as e:
            print(f"Ошибка при добавлении автомобиля: {e}")
            return False

    def add_driver(self, full_name: str, license_number: str,
                   phone: str, hire_date: str = None) -> bool:
        """Добавляет нового водителя"""
        hire_date = hire_date or datetime.now().strftime('%Y-%m-%d')
        query = """
            INSERT INTO drivers (full_name, license_number, phone, hire_date)
            VALUES (%s, %s, %s, %s)
        """
        try:
            self._execute_query(query, (full_name, license_number, phone, hire_date))
            return True
        except Error as e:
            print(f"Ошибка при добавлении водителя: {e}")
            return False

    def get_cars(self) -> List[Dict]:
        """Возвращает список автомобилей"""
        query = "SELECT * FROM cars"
        try:
            return self._execute_query(query, fetch=True)
        except Error as e:
            print(f"Ошибка при получении автомобилей: {e}")
            return []

    def get_drivers(self, active_only: bool = True) -> List[Dict]:
        """Возвращает список водителей"""
        query = "SELECT * FROM drivers"
        try:
            return self._execute_query(query, fetch=True)
        except Error as e:
            print(f"Ошибка при получении водителей: {e}")
            return []

    def delete_car(self, car_id: int) -> bool:
        """Удаляет автомобиль по его ID"""
        try:
            with self._get_cursor() as cursor:
                # 1. Проверить существование автомобиля
                cursor.execute("SELECT 1 FROM cars WHERE car_id = %s", (car_id,))
                if not cursor.fetchone():
                    print(f"Автомобиль с ID {car_id} не найден")
                    return False

                # 2. Проверить назначение водителя
                cursor.execute("SELECT COUNT(*) FROM driver_car_assignments WHERE car_id = %s", (car_id,))
                if cursor.fetchone()[0] > 0:
                    print("Ошибка: нельзя удалить автомобиль, так как он назначен водителю")
                    return False

                # 3. Удалить связанные записи (например, из maintenance_history)
                cursor.execute("DELETE FROM maintenance_history WHERE car_id = %s", (car_id,))

                # 4. Удалить автомобиль
                cursor.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
                return True

        except Error as e:
            print(f"Ошибка при удалении автомобиля (ID: {car_id}): {e}")
            return False

    def delete_driver(self, driver_id: int) -> bool:
        """Удаляет водителя по ID"""
        try:
            with self._get_cursor() as cursor:
                # Проверка назначения водителя
                cursor.execute("SELECT COUNT(*) FROM driver_car_assignments WHERE driver_id = %s", (driver_id,))
                if cursor.fetchone()[0] > 0:
                    print("Ошибка: нельзя удалить водителя, так как он назначен на автомобиль")
                    return False

                # Удаление водителя
                cursor.execute("DELETE FROM drivers WHERE driver_id = %s", (driver_id,))
                return True
        except Error as e:
            print(f"Ошибка при удалении водителя: {e}")
            return False

    def assign_driver_to_car(self, driver_id: int, car_id: int) -> bool:
        """Назначает водителя на автомобиль"""
        try:
            with self._get_cursor() as cursor:
                # Проверка доступности водителя и автомобиля
                cursor.execute("""
                    SELECT 1 FROM drivers 
                    WHERE driver_id = %s AND status = 'available'
                    AND NOT EXISTS (
                        SELECT 1 FROM driver_car_assignments WHERE driver_id = %s
                    )
                """, (driver_id, driver_id))

                if not cursor.fetchone():
                    print("Водитель не найден или уже занят")
                    return False

                cursor.execute("""
                    SELECT 1 FROM cars 
                    WHERE car_id = %s AND is_active = TRUE
                    AND NOT EXISTS (
                        SELECT 1 FROM driver_car_assignments WHERE car_id = %s
                    )
                """, (car_id, car_id))

                if not cursor.fetchone():
                    print("Автомобиль не найден или уже занят")
                    return False

                # Назначение
                cursor.execute("""
                    INSERT INTO driver_car_assignments (driver_id, car_id)
                    VALUES (%s, %s)
                """, (driver_id, car_id))

                cursor.execute("""
                    UPDATE drivers 
                    SET status = 'on_ride' 
                    WHERE driver_id = %s
                """, (driver_id,))
                return True
        except Error as e:
            print(f"Ошибка при назначении водителя: {e}")
            return False

    def get_free_drivers(self) -> List[Dict]:
        """Возвращает список свободных водителей"""
        query = """
            SELECT d.* FROM drivers d
            LEFT JOIN driver_car_assignments a ON d.driver_id = a.driver_id
            WHERE a.driver_id IS NULL
            AND d.status = 'available'
        """
        try:
            return self._execute_query(query, fetch=True)
        except Error as e:
            print(f"Ошибка при получении свободных водителей: {e}")
            return []

    def get_free_cars(self) -> List[Dict]:
        """Возвращает список свободных автомобилей"""
        query = """
            SELECT c.* FROM cars c
            LEFT JOIN driver_car_assignments a ON c.car_id = a.car_id
            WHERE a.car_id IS NULL
            AND c.is_active = TRUE
        """
        try:
            return self._execute_query(query, fetch=True)
        except Error as e:
            print(f"Ошибка при получении свободных автомобилей: {e}")
            return []

    def get_assigned_drivers(self) -> List[Dict]:
        """Возвращает список распределенных водителей с их автомобилями"""
        query = """
            SELECT d.driver_id, d.full_name, c.car_id, c.license_plate, c.model
            FROM driver_car_assignments a
            JOIN drivers d ON a.driver_id = d.driver_id
            JOIN cars c ON a.car_id = c.car_id
        """
        try:
            return self._execute_query(query, fetch=True)
        except Error as e:
            print(f"Ошибка при получении распределенных водителей: {e}")
            return []

    def add_maintenance_record(self, car_id: int, date: str, mileage: int,
                               service_type: str, description: str, cost: float = None) -> bool:
        """Добавляет запись о техническом обслуживании"""
        try:
            with self._get_cursor() as cursor:
                # Добавляем запись в историю ТО
                cursor.execute("""
                    INSERT INTO maintenance_history 
                    (car_id, maintenance_date, mileage, service_type, description, cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (car_id, date, mileage, service_type, description, cost))

                # Обновляем пробег автомобиля ТОЛЬКО если новый пробег больше текущего
                cursor.execute("""
                    UPDATE cars 
                    SET last_maintenance = %s, 
                        mileage = GREATEST(COALESCE(mileage, 0), %s)
                    WHERE car_id = %s
                """, (date, mileage, car_id))

                return True
        except Error as e:
            print(f"Ошибка при добавлении записи ТО: {e}")
            return False
    def get_maintenance_history(self, car_id: int) -> List[Dict]:
        """Возвращает историю ТО для автомобиля"""
        query = """
            SELECT * FROM maintenance_history 
            WHERE car_id = %s 
            ORDER BY maintenance_date DESC
        """
        try:
            return self._execute_query(query, (car_id,), fetch=True)
        except Error as e:
            print(f"Ошибка при получении истории ТО: {e}")
            return []

    def get_car_current_status(self, car_id: int) -> Optional[Dict]:
        """Возвращает текущий статус автомобиля"""
        query = """
            SELECT 
                c.*, 
                (SELECT MAX(maintenance_date) FROM maintenance_history WHERE car_id = c.car_id) as last_maintenance_date,
                (SELECT mileage FROM maintenance_history WHERE car_id = c.car_id ORDER BY maintenance_date DESC LIMIT 1) as current_mileage
            FROM cars c
            WHERE c.car_id = %s AND c.is_active = TRUE
        """
        try:
            with self._get_cursor(dictionary=True) as cursor:
                cursor.execute(query, (car_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"Ошибка при получении статуса автомобиля: {e}")
            return None


def main():
    db = DatabaseManager()
    if not db.create_database() or not db.create_tables():
        print("Не удалось инициализировать базу данных")
        return
    print("Инициализация базы данных таксопарка завершена")


if __name__ == '__main__':
    main()